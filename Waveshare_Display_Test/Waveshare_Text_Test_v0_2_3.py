#!/usr/bin/env python3

# Waveshare Text Test v0.2.3 - Waveshare_Text_Test_v0_2_3.py
# Test BMP/text loading, scaling, clockwise orientation, and image retention.

import importlib.util
import os
import sys
from pathlib import Path

# Test settings: change these without modifying the display library.
PREVIEW_FILE = "2in71.bmp"   # .bmp or UTF-8 .txt
AUTOSCALE = 0     # 0 = original size and clipping; 1 = proportional fit (BMP only)
ORIENTATION = 180 # Clockwise degrees: 0, 90, 180, or 270
CLEAR = 1         # 0 = retain image on exit; 1 = erase display on exit
FONT_SIZE = 10
LINE_SPACING = 0
ORIGIN_X = 0
ORIGIN_Y = 0
ERROR_LOG = 0    # 0 = stderr only; 1 = also write timestamped error log

# Removed absolute library path reference
# WAVESHARE_LIB = "/home/pi/Project_Files/External_Display_Software/e-Paper/RaspberryPi_JetsonNano/python/lib"

# Locate the project root by finding its Waveshare_Base directory.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = next((directory for directory in (SCRIPT_DIR, *SCRIPT_DIR.parents) if (directory / "Waveshare_Base" / "lib").is_dir()), None)
if PROJECT_ROOT is None:
    raise FileNotFoundError("Cannot locate the Waveshare project bundle")
WAVESHARE_LIB = str(PROJECT_ROOT / "Waveshare_Base" / "lib")
LIBRARY_FILE = os.path.join(WAVESHARE_LIB, "Waveshare_Text_v0_2_3.py")

# Font list.  These fonts should be available in typical Linux systems.
#
# Select ONE font by uncommenting its assignment and commenting the others.
# Availability depends on the fonts installed on your system.
#
FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"
# FONT_FILE = "/usr/share/fonts/truetype/nimbus/NimbusRoman-Regular.otf"


def load_library():
    # Load the exact matching revision, not an older Waveshare_Text.py symlink.
    spec = importlib.util.spec_from_file_location("waveshare_text_test_library", LIBRARY_FILE)
    if spec is None or spec.loader is None:
        raise ImportError("Cannot load library: " + LIBRARY_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.WaveshareText


def main():
    if AUTOSCALE not in (0, 1) or CLEAR not in (0, 1) or ERROR_LOG not in (0, 1):
        print("AUTOSCALE, CLEAR, and ERROR_LOG must be 0 or 1.")
        return
    if ORIENTATION not in (0, 90, 180, 270):
        print("ORIENTATION must be 0, 90, 180, or 270.")
        return

    try:
        WaveshareText = load_library()
    except Exception as exception:
        print("Library load failed: {}".format(exception), file=sys.stderr)
        return

    log_file = os.path.join(SCRIPT_DIR, "Waveshare_Text_Test_v0_2_3_errors.txt") if ERROR_LOG else None
    display = WaveshareText(orientation=ORIENTATION, error_log=log_file)
    if not display.init():
        print("Initialization failed: {}".format(display.last_error))
        return

    try:
        filename = os.path.join(SCRIPT_DIR, PREVIEW_FILE)
        extension = os.path.splitext(filename)[1].lower()
        if extension == ".bmp":
            loaded = display.load_image(filename, scale=bool(AUTOSCALE))
        elif extension == ".txt":
            loaded = display.set_font(FONT_FILE, FONT_SIZE)
            if loaded:
                loaded = display.load_text(filename, ORIGIN_X, ORIGIN_Y, LINE_SPACING)
        else:
            print("Unsupported file type: {} (use .bmp or .txt)".format(extension))
            return

        if not loaded:
            print("File load failed: {}".format(display.last_error))
            return
        if not display.update():
            print("Display update failed: {}".format(display.last_error))
            return
        input("Display updated. Press Enter to exit... ")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting display test.")
    finally:
        if CLEAR == 1 and not display.clear():
            print("Display clear failed: {}".format(display.last_error))
        if not display.close():
            print("Display shutdown reported an error: {}".format(display.last_error))


if __name__ == "__main__":
    main()
