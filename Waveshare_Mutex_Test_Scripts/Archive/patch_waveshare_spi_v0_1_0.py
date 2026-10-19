#!/usr/bin/env python3

# patch_waveshare_spi_v0_1_0.py - Version 0.1.0 - Patch Waveshare SPI with Dexter mutex.

import hashlib
import os
from pathlib import Path
import sys
import tempfile

DIRECTORY = Path('/home/pi/Project_Files/External_Display_Software/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd')
TARGET = DIRECTORY / 'epd2in7.py'
BACKUP = DIRECTORY / 'epd2in7.py.original'
EXPECTED_SHA256 = 'cd7b83cd5f2ab675fef4b17790cdfbb6170391078e6c15e3cdbe52a81129099a'

OLD_IMPORT = 'import logging\nfrom . import epdconfig\n'
NEW_IMPORT = 'import logging\nfrom di_mutex import DI_Mutex\nfrom . import epdconfig\n\nSPI_MUTEX = DI_Mutex("SPI")\n'
OLD_METHODS = '''    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)
'''
NEW_METHODS = '''    def send_command(self, command):
        SPI_MUTEX.acquire()
        try:
            epdconfig.digital_write(self.dc_pin, 0)
            try:
                epdconfig.digital_write(self.cs_pin, 0)
                epdconfig.spi_writebyte([command])
            finally:
                epdconfig.digital_write(self.cs_pin, 1)
        finally:
            SPI_MUTEX.release()

    def send_data(self, data):
        SPI_MUTEX.acquire()
        try:
            epdconfig.digital_write(self.dc_pin, 1)
            try:
                epdconfig.digital_write(self.cs_pin, 0)
                epdconfig.spi_writebyte([data])
            finally:
                epdconfig.digital_write(self.cs_pin, 1)
        finally:
            SPI_MUTEX.release()
'''

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    from di_mutex import DI_Mutex
    print('Mutex:', DI_Mutex('SPI').Filename)
    original = BACKUP.read_bytes()
    active = TARGET.read_bytes()
    if digest(original) != EXPECTED_SHA256 or active != original:
        sys.exit('STOP: active driver or backup does not match verified original; nothing changed.')
    source = active.decode('utf-8')
    if source.count(OLD_IMPORT) != 1 or source.count(OLD_METHODS) != 1:
        sys.exit('STOP: expected source patterns not found exactly once; nothing changed.')
    modified = source.replace(OLD_IMPORT, NEW_IMPORT, 1).replace(OLD_METHODS, NEW_METHODS, 1)
    compile(modified, str(TARGET), 'exec')
    fd, staged = tempfile.mkstemp(prefix='epd2in7-', suffix='.py', dir=str(DIRECTORY))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(modified.encode('utf-8'))
            f.flush()
            os.fsync(f.fileno())
        os.chmod(staged, TARGET.stat().st_mode & 0o777)
        print('Original SHA256:', digest(original))
        print('Patched  SHA256:', digest(modified.encode('utf-8')))
        print('Backup:', BACKUP)
        os.replace(staged, str(TARGET))
        print('Activated:', TARGET)
        print('Rollback: cp -av "{}" "{}"'.format(BACKUP, TARGET))
    finally:
        if os.path.exists(staged):
            os.unlink(staged)

if __name__ == '__main__':
    main()
