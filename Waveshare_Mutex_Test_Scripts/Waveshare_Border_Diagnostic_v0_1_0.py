#!/usr/bin/env python3

# Waveshare Border Diagnostic v0.1.0 - Waveshare_Border_Diagnostic_v0_1_0.py
# Compare monochrome and 4-gray clearing without changing the vendor driver.

import os
import sys
from PIL import Image

WAVESHARE_LIB = (
    "/home/pi/Project_Files/External_Display_Software/e-Paper/"
    "RaspberryPi_JetsonNano/python/lib"
)


def pause(message):
    input("\n" + message + "\nInspect/photograph the border, then press Enter... ")


def main():
    if not os.path.isdir(WAVESHARE_LIB):
        raise FileNotFoundError("Waveshare library not found: " + WAVESHARE_LIB)
    sys.path.insert(0, WAVESHARE_LIB)
    from waveshare_epd import epd2in7

    epd = epd2in7.EPD()
    initialized = False
    try:
        print("Initializing in monochrome mode...")
        result = epd.init()
        if result == -1:
            raise RuntimeError("Waveshare EPD initialization failed")
        initialized = True

        print("TEST A: Monochrome Clear(0xFF)")
        epd.Clear(0xFF)
        pause("A: monochrome clear complete.")

        print("TEST B: Display an all-white monochrome image")
        white = Image.new("1", (epd.height, epd.width), 255)
        epd.display(epd.getbuffer(white))
        pause("B: white-image display complete.")

        print("TEST C: Switch to 4-gray mode, then Clear(0xFF)")
        epd.Init_4Gray()
        epd.Clear(0xFF)
        pause("C: 4-gray initialization + clear complete.")

    except (KeyboardInterrupt, EOFError):
        print("\nTest interrupted.")
    finally:
        if initialized:
            try:
                print("Final clear...")
                epd.Clear(0xFF)
            finally:
                print("Going to sleep...")
                epd.sleep()


if __name__ == "__main__":
    main()
