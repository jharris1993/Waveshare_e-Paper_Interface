#!/usr/bin/env python3

# Waveshare Typography Test v0.1.3 - Waveshare_Typography_Test_v0_1_3.py
# Static 250-column x 100-row walking-alphabet test for the 2.7-inch EPD.

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Pre-defined system constants. Adjust as necessary.
FONT_SIZE = 10       # Pixel size
LINE_SPACING = 0     # Additional pixels between successive text rows
ORIGIN_X = 0         # Horizontal text origin in pixels; negatives allowed
ORIGIN_Y = 0         # Vertical text origin in pixels; negatives allowed
ORIENTATION = 180    # Clockwise rotation: 0, 90, 180, or 270 degrees
COLUMNS = 250
ROWS = 100
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
WAVESHARE_LIB = (
    "/home/pi/Project_Files/External_Display_Software/e-Paper/RaspberryPi_JetsonNano/python/lib"
)

# Font list.  These fonts should be available in typical Linux systems.
#
# Select ONE font by uncommenting its assignment and commenting the others.
# Availability depends on the fonts installed on your system.
#
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
# FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
# FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
# FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
# FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
# FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
# FONT = "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"
# FONT = "/usr/share/fonts/truetype/nimbus/NimbusRoman-Regular.otf"

def make_row(row_number):
    """Return a row of exactly COLUMNS characters (row numbers start at 1)."""
    if row_number == 1:
        return "".join(str((col % 10)) for col in range(1, COLUMNS + 1))
    prefix = str(row_number % 10)
    offset = (row_number - 2) % len(ALPHABET)
    walking = ALPHABET[offset:] + ALPHABET[:offset]
    count = COLUMNS - 1
    return prefix + (walking * ((count // len(walking)) + 1))[:count]


def main():
    if ORIENTATION not in (0, 90, 180, 270):
        raise ValueError("ORIENTATION must be 0, 90, 180, or 270")
    if FONT_SIZE <= 0 or LINE_SPACING < 0:
        raise ValueError("FONT_SIZE must be positive and LINE_SPACING nonnegative")
    if not os.path.isfile(FONT):
        raise FileNotFoundError("Font not installed: " + FONT)
    if not os.path.isdir(WAVESHARE_LIB):
        raise FileNotFoundError("Waveshare library not found: " + WAVESHARE_LIB)

    sys.path.insert(0, WAVESHARE_LIB)
    from waveshare_epd import epd2in7

    font = ImageFont.truetype(FONT, FONT_SIZE)
    ascent, descent = font.getmetrics()
    row_pitch = ascent + descent + LINE_SPACING

    epd = epd2in7.EPD()
    # The vendor's landscape example uses (epd.height, epd.width).
    landscape_size = (epd.height, epd.width)
    drawing_size = (landscape_size[1], landscape_size[0]) if ORIENTATION in (90, 270) else landscape_size
    frame = Image.new("1", drawing_size, 255)
    draw = ImageDraw.Draw(frame)

    for row_number in range(1, ROWS + 1):
        y = ORIGIN_Y + (row_number - 1) * row_pitch
        if y >= frame.height:
            break
        draw.text((ORIGIN_X, y), make_row(row_number), font=font, fill=0)

    if ORIENTATION:
        frame = frame.rotate(-ORIENTATION, expand=True)

    print("Font: {}".format(FONT))
    print("Size: {} px; spacing: {} px; row pitch: {} px".format(
        FONT_SIZE, LINE_SPACING, row_pitch))
    print("Logical grid: {} columns x {} rows".format(COLUMNS, ROWS))
    print("Visible window: {} x {} px".format(*frame.size))
    print("Text origin: ({}, {}) px".format(ORIGIN_X, ORIGIN_Y))
    print("Clockwise rotation: {} degrees".format(ORIENTATION))

    initialized = False
    try:
        epd.init()
        initialized = True
        epd.display(epd.getbuffer(frame))
        input("Pattern displayed. Press Enter to clear and exit... ")
    except KeyboardInterrupt:
        print("\nCtrl+C received.")
    except EOFError:
        print("\nInput closed.")
    finally:
        if initialized:
            try:
                print("Clear...")
                epd.Clear(0xFF)
            finally:
                print("Goto Sleep...")
#                epd.sleep()
#
# "unpacked" epd.sleep() commands.
                epd.send_command(0x50)
                epd.send_data(0xF7)
                epd.send_command(0x02)
                epd.send_command(0x07)
                epd.send_data(0xA5)

if __name__ == "__main__":
    main()
