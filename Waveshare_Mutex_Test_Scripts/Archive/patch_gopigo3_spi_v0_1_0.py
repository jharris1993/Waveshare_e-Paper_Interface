#!/usr/bin/env python3

# patch_gopigo3_spi_v0_1_0.py — version 0.1.0 — patch GoPiGo3 SPI transfers in the pi user's egg.
# Run on the robot as pi. Python 3.7 compatible.

import hashlib
import importlib.util
import os
from pathlib import Path
import py_compile
import shutil
import sys
import tempfile
import zipfile

EGG = Path('/home/pi/.local/lib/python3.7/site-packages/gopigo3-1.3.2.1-py3.7.egg')
BACKUP = Path(str(EGG) + '.original')
STAGED = Path(str(EGG) + '.patched')

OLD = b'        result = GPG_SPI.xfer2(data_out)\n        return result'
NEW = (b'        SPI_MUTEX.acquire()\n'
       b'        try:\n'
       b'            return GPG_SPI.xfer2(data_out)\n'
       b'        finally:\n'
       b'            SPI_MUTEX.release()')
IMPORT = b'from di_mutex import DI_Mutex\nSPI_MUTEX = DI_Mutex("SPI")\n'
MARKER = b'import json\n'


def sha256(path):
    h = hashlib.sha256()
    with open(str(path), 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if os.geteuid() != 1000 or Path.home() != Path('/home/pi'):
        sys.exit('ERROR: Run as the pi user (not sudo).')
    if importlib.util.find_spec('di_mutex') is None:
        sys.exit('ERROR: di_mutex is not importable by pi; nothing changed.')
    if not EGG.is_file() or not BACKUP.is_file():
        sys.exit('ERROR: Egg or verified .original backup missing; nothing changed.')
    if sha256(EGG) != sha256(BACKUP):
        sys.exit('ERROR: Current egg differs from .original; nothing changed.')
    if STAGED.exists():
        sys.exit('ERROR: .patched staging file already exists; nothing changed.')

    with zipfile.ZipFile(str(EGG), 'r') as z:
        if z.testzip() is not None:
            sys.exit('ERROR: Egg archive integrity failed.')
        src = z.read('gopigo3.py')
        if src.count(OLD) != 1 or src.count(MARKER) != 1:
            sys.exit('ERROR: Unexpected gopigo3.py contents; nothing changed.')
        patched = src.replace(MARKER, MARKER + IMPORT, 1).replace(OLD, NEW, 1)

        # Syntax-check without importing the robot hardware driver.
        compile(patched, 'gopigo3.py', 'exec')
        try:
            with zipfile.ZipFile(str(STAGED), 'w') as out:
                out.comment = z.comment
                for info in z.infolist():
                    # Do not retain stale bytecode for the modified source.
                    if info.filename == '__pycache__/gopigo3.cpython-37.pyc':
                        continue
                    data = patched if info.filename == 'gopigo3.py' else z.read(info.filename)
                    out.writestr(info, data)
        except BaseException:
            if STAGED.exists():
                STAGED.unlink()
            raise

    with zipfile.ZipFile(str(STAGED), 'r') as z:
        assert z.testzip() is None
        assert z.read('gopigo3.py') == patched
    os.chmod(str(STAGED), EGG.stat().st_mode & 0o777)
    print('Original SHA256:', sha256(EGG))
    print('Patched  SHA256:', sha256(STAGED))
    print('Backup retained:', BACKUP)
    print('Staged archive: ', STAGED)
    print('Preflight successful. Activating patched egg...')
    os.replace(str(STAGED), str(EGG))
    print('Activated:', EGG)
    print('Rollback: cp -av "{}" "{}"'.format(BACKUP, EGG))


if __name__ == '__main__':
    main()
