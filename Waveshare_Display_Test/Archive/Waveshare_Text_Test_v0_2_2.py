#!/usr/bin/env python3

# Waveshare Bitmap Test v0.2.2 - Waveshare_Text_Test_v0_2_2.py
# v0.2.2: Add AUTOSCALE and CLEAR switches for bitmap display tests.
# Load a bitmap, display it, and optionally erase it before power-down.

import os
from Waveshare_Text import WaveshareText

# Test configuration. Change these settings without editing the library.
AUTOSCALE = 0    # 0 = original size, clipped at display edges; 1 = scale to fit
CLEAR = 0        # 0 = preserve displayed image on exit; 1 = clear on exit
BITMAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Waveshare_Text_preview.bmp")


def main():
    if AUTOSCALE not in (0, 1) or CLEAR not in (0, 1):
        print("AUTOSCALE and CLEAR must each be 0 or 1.")
        return

    display = WaveshareText("landscape")
    if not display.init():
        print("Initialization failed: {}".format(display.last_error))
        return

    try:
        if not display.load_image(BITMAP, scale=bool(AUTOSCALE)):
            print("Image load failed: {}".format(display.last_error))
            return
        if not display.update():
            print("Display update failed: {}".format(display.last_error))
            return
        input("Bitmap displayed. Press Enter to exit... ")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting display test.")
    finally:
        if CLEAR == 1:
            if not display.clear():
                print("Display clear failed: {}".format(display.last_error))
        if not display.close():
            print("Display shutdown reported an error: {}".format(display.last_error))


if __name__ == "__main__":
    main()
