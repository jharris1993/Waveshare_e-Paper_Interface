#!/usr/bin/env python3

# Waveshare Bitmap Test v0.2.1 - Waveshare_Text_Test_v0_2_1.py
# Load a full-screen bitmap, display it, and power down without erasing it.

import os
from Waveshare_Text import WaveshareText

# The bitmap must be in the same directory as this test program.
BITMAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Pico_2in7.bmp")


def main():
    display = WaveshareText("landscape")
    if not display.init():
        return

    try:
        if not display.load_image(BITMAP):
            return
        if not display.update():
            return
        input("Bitmap displayed. Press Enter to close (image remains visible)... ")
    except (KeyboardInterrupt, EOFError):
        print("\nClosing display.")
    finally:
        if not display.close():
            print("Display shutdown reported an error.")


if __name__ == "__main__":
    main()
