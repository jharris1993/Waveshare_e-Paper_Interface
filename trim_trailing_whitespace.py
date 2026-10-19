#!/usr/bin/env python3

# trim_trailing_whitespace.py - Version 0.2.0
# Remove trailing whitespace from staged text files in a Git repository.
# Run from the root of the Git repository.

import subprocess
from pathlib import Path


# Obtain staged file names and Git's text/binary classification.
# Git reports "-" for binary files instead of added/deleted line counts.
output = subprocess.check_output(
    ["git", "diff", "--cached", "--numstat", "-z"]
)

files = []

# With -z, Git separates records using null bytes. For renamed files,
# the filename may be in a separate null-delimited field.
records = iter(filter(None, output.split(b"\0")))

for record in records:
    added, deleted, filename = record.split(b"\t", 2)

    if not filename:
        filename = next(records)

    # Only process files Git identifies as text.
    if added != b"-" and deleted != b"-":
        files.append(filename)


for filename in files:
    path = Path(filename.decode("utf-8", "surrogateescape"))

    # Skip files that no longer exist.
    if not path.is_file():
        continue

    data = path.read_bytes()

    # Additional safeguard against modifying binary files.
    if b"\0" in data:
        continue

    lines = data.splitlines(keepends=True)
    cleaned = []

    for line in lines:
        # Preserve the original line ending.
        ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
        content = line[:-len(ending)] if ending else line

        # Remove trailing spaces and tabs.
        cleaned.append(content.rstrip(b" \t") + ending)

    # Remove excess blank lines at EOF.
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()

    # Retain exactly one final newline for nonempty files.
    if cleaned:
        ending = b"\r\n" if b"\r\n" in data else b"\n"
        cleaned[-1] = cleaned[-1].rstrip(b"\r\n") + ending

    result = b"".join(cleaned)

    if result != data:
        path.write_bytes(result)
        print("Cleaned:", path)


print("Whitespace cleanup complete.")
