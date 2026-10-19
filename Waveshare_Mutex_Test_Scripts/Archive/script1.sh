#!/bin/bash

EGG=/home/pi/.local/lib/python3.7/site-packages/gopigo3-1.3.2.1-py3.7.egg

echo "===== Archive identification ====="
file "$EGG"

echo "===== Archive integrity ====="
unzip -t "$EGG"

echo "===== Library contents ====="
unzip -l "$EGG" | grep -E '(^|/)(gopigo3|easygopigo3)\.py$'

echo "===== Backup original egg ====="
cp -av "$EGG" "$EGG.original"

echo "===== SHA256 checksums ====="
sha256sum "$EGG" "$EGG.original"

echo "===== SPI transfer implementation ====="
unzip -p "$EGG" gopigo3.py | grep -A 12 'def spi_transfer_array'
