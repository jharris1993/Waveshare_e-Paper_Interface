#!/usr/bin/env python3

# Waveshare Typography Test v0.1.4a - Waveshare_Typography_Test_v0_1_4a.py
# Alternating-orientation 250-column x 100-row typography test for the 2.7-inch EPD.

import os
import sys
import select
import time

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

FONT_SIZE = 10       # Pixel size
LINE_SPACING = 0     # Additional pixels between successive text rows
ORIGIN_X = 0         # Horizontal text origin in pixels; negatives allowed
ORIGIN_Y = 0         # Vertical text origin in pixels; negatives allowed
ORIENTATION = 0      # Initial clockwise rotation: 0, 90, 180, or 270 degrees
sleep_timer = 0      # Seconds to hold each displayed image; zero allowed
pause_timer = 0      # Seconds between clear/sleep and next display
COLUMNS = 250
ROWS = 100
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

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

# Removed absolute library path reference
# WAVESHARE_LIB = "/home/pi/Project_Files/External_Display_Software/e-Paper/RaspberryPi_JetsonNano/python/lib"

# Locate the project root by finding its Waveshare_Base directory.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = next((directory for directory in (SCRIPT_DIR, *SCRIPT_DIR.parents) if (directory / "Waveshare_Base" / "lib").is_dir()), None)
if PROJECT_ROOT is None:
    raise FileNotFoundError("Cannot locate the Waveshare project bundle")
WAVESHARE_LIB = str(PROJECT_ROOT / "Waveshare_Base" / "lib")

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
    if FONT_SIZE <= 0:
        raise ValueError("FONT_SIZE must be positive")
    if sleep_timer < 0:
        raise ValueError("sleep_timer must be nonnegative")
    if pause_timer < 0:
        raise ValueError("pause_timer must be nonnegative")
    if not os.path.isfile(FONT):
        raise FileNotFoundError("Font not installed: " + FONT)
    if not os.path.isdir(WAVESHARE_LIB):
        raise FileNotFoundError("Waveshare library not found: " + WAVESHARE_LIB)

    sys.path.insert(0, WAVESHARE_LIB)
    from waveshare_epd import epd2in7, epdconfig

    font = ImageFont.truetype(FONT, FONT_SIZE)
    ascent, descent = font.getmetrics()
    row_pitch = ascent + descent + LINE_SPACING

    epd = epd2in7.EPD()
    landscape_size = (epd.height, epd.width)

    def make_frame(orientation):
        # Use the same logical text window for each orientation.
        drawing_size = (
            (landscape_size[1], landscape_size[0])
            if orientation in (90, 270) else landscape_size
        )
        frame = Image.new("1", drawing_size, 255)
        draw = ImageDraw.Draw(frame)
        for row_number in range(1, ROWS + 1):
            y = ORIGIN_Y + (row_number - 1) * row_pitch
            if y >= frame.height and row_pitch > 0:
                break
            draw.text((ORIGIN_X, y), make_row(row_number), font=font, fill=0)
        if orientation:
            frame = frame.rotate(-orientation, expand=True)
        return frame

    orientations = (ORIENTATION, (ORIENTATION + 180) % 360)
    frames = (make_frame(orientations[0]), make_frame(orientations[1]))

    print("Font: {}".format(FONT))
    print("Size: {} px; spacing: {} px; row pitch: {} px".format(
        FONT_SIZE, LINE_SPACING, row_pitch))
    print("Logical grid: {} columns x {} rows".format(COLUMNS, ROWS))
    print("Visible window: {} x {} px".format(*frames[0].size))
    print("Text origin: ({}, {}) px".format(ORIGIN_X, ORIGIN_Y))
    print("Alternating orientations: {} and {} degrees".format(*orientations))
    print("Display hold: {} seconds; pause: {} seconds".format(
        sleep_timer, pause_timer))

    def wait_or_exit(seconds):
        """Return True if Enter or input EOF requests exit."""
        deadline = time.monotonic() + seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            readable, _, _ = select.select([sys.stdin], [], [], remaining)
            if readable:
                sys.stdin.readline()
                return True

    def clear_and_sleep():
        print("Clear...")
        epd.Clear(0xFF)
        print("Goto Sleep (controller commands only; no module_exit)...")
        # epd.sleep()
        #
        # "unpacked" epd.sleep() commands.
        epd.send_command(0x50)
        epd.send_data(0xF7)
        epd.send_command(0x02)
        epd.send_command(0x07)
        epd.send_data(0xA5)

# Diagnostic: isolate SPI.close() from module_exit().
        epdconfig.SPI.close()

    awake = False
    try:
        while True:
            for index in (0, 1):
                # Reinitialize after each controller sleep.
                epd.init()
                awake = True
                print("Displaying orientation {} degrees...".format(
                    orientations[index]))
                epd.display(epd.getbuffer(frames[index]))
                exit_requested = wait_or_exit(sleep_timer)
                clear_and_sleep()
                awake = False
                if exit_requested:
                    return
                if wait_or_exit(pause_timer):
                    return
    except KeyboardInterrupt:
        print("\nCtrl+C received.")
    finally:
        if awake:
            # If interrupted during a display or hold, clear and sleep.
            clear_and_sleep()
        else:
            # The last completed iteration already cleared and slept.
            print("Display already cleared and sleeping.")


if __name__ == "__main__":
    main()
