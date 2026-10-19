#!/bin/bash

DIR="/home/pi/Project_Files/External_Display_Software/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd"

echo "===== Back up Waveshare drivers ====="
cp -avn "$DIR/epd2in7.py" "$DIR/epd2in7.py.original"
cp -avn "$DIR/epdconfig.py" "$DIR/epdconfig.py.original"

echo "===== Verify backups ====="
sha256sum "$DIR/epd2in7.py" "$DIR/epd2in7.py.original"
sha256sum "$DIR/epdconfig.py" "$DIR/epdconfig.py.original"

echo "===== Verify imports from project directory ====="
PYTHONPATH="$(dirname "$DIR")" python3 -c "from waveshare_epd import epd2in7, epdconfig; print(epd2in7.__file__); print(epdconfig.__file__)"
