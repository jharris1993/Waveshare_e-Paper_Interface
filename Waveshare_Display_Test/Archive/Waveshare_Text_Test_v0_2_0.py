#!/usr/bin/env python3

# Waveshare Text Test v0.2.0 - Waveshare_Text_Test_v0_2_0.py
# Normal full-screen text test; requires Waveshare_Text.py pointing to the current library.

from Waveshare_Text import WaveshareText

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SIZE = 14


def main():
    display = WaveshareText("landscape")
    if not display.init():
        return
    try:
        if not display.set_font(FONT, FONT_SIZE):
            return
        if not display.text(5, 5, "Waveshare e-Paper\nGeneral text interface\nTemperature: 23.5°C"):
            return
        if not display.update():
            return
        input("Text displayed. Press Enter to close (image remains visible)... ")
    except (KeyboardInterrupt, EOFError):
        print("\nClosing display.")
    finally:
        display.close()


if __name__ == "__main__":
    main()
