#!/usr/bin/env python3

# Waveshare Text v0.2.3 - Waveshare_Text_v0_2_3.py
# Full-screen text and bitmap interface for the Waveshare 2.7-inch e-paper HAT.
# v0.2.3: Add clockwise orientation, UTF-8 text loading, and optional error logging.

import os
import sys
import traceback
from PIL import Image, ImageDraw, ImageFont

WAVESHARE_LIB = "/home/pi/Project_Files/External_Display_Software/e-Paper/RaspberryPi_JetsonNano/python/lib"


class WaveshareText:
    def __init__(self, orientation=0, error_log=None):
        self.orientation = orientation
        self.error_log = error_log
        self.last_error = None
        self.initialized = False
        self.epd = None
        self.font = None
        self.image = None
        self.width = 0
        self.height = 0

    def _error(self, operation, exception):
        self.last_error = "{}: {}".format(operation, exception)
        print("WaveshareText: " + self.last_error, file=sys.stderr)
        if self.error_log:
            try:
                from datetime import datetime
                with open(self.error_log, "a", encoding="utf-8") as log:
                    log.write("{} | {}\n".format(datetime.now().isoformat(), self.last_error))
                    log.write("".join(traceback.format_exception(type(exception), exception, exception.__traceback__)))
            except Exception as log_exception:
                print("WaveshareText: error log unavailable: {}".format(log_exception), file=sys.stderr)
        return False

    def _require_init(self):
        if not self.initialized:
            raise RuntimeError("Display is not initialized; call init()")

    def init(self):
        if self.initialized:
            return True
        try:
            if self.orientation not in (0, 90, 180, 270):
                raise ValueError("Orientation must be 0, 90, 180, or 270 degrees")
            if not os.path.isdir(WAVESHARE_LIB):
                raise FileNotFoundError("Waveshare library not found: " + WAVESHARE_LIB)
            if WAVESHARE_LIB not in sys.path:
                sys.path.insert(0, WAVESHARE_LIB)
            from waveshare_epd import epd2in7

            self.epd = epd2in7.EPD()
            if self.epd.init() != 0:
                raise RuntimeError("Waveshare hardware initialization failed")

            # Orientation 0 is the native landscape image used by the working v0.2.2 driver.
            # For quarter-turns, exchange the logical canvas dimensions.
            native_width, native_height = self.epd.height, self.epd.width
            if self.orientation in (0, 180):
                self.width, self.height = native_width, native_height
            else:
                self.width, self.height = native_height, native_width
            self.image = Image.new("1", (self.width, self.height), 255)
            self.initialized = True
            self.last_error = None
            return True
        except Exception as exception:
            self.initialized = False
            return self._error("init", exception)

    def set_font(self, filename, size):
        try:
            self._require_init()
            if not isinstance(size, int) or size <= 0:
                raise ValueError("Font size must be a positive integer")
            self.font = ImageFont.truetype(filename, size)
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("set_font", exception)

    def text(self, x, y, message, spacing=4):
        try:
            self._require_init()
            if self.font is None:
                raise RuntimeError("Select a font with set_font()")
            if not isinstance(message, str):
                raise TypeError("Text must be a string")
            ImageDraw.Draw(self.image).multiline_text((x, y), message, font=self.font, fill=0, spacing=spacing)
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("text", exception)

    def textfile(self, filename, x=0, y=0, spacing=4):
        try:
            self._require_init()
            with open(filename, "r", encoding="utf-8-sig", errors="replace") as source:
                message = source.read()
            return self.text(x, y, message, spacing=spacing)
        except Exception as exception:
            return self._error("textfile", exception)

    def load_text(self, filename, x=0, y=0, spacing=0):
        """Replace the image buffer with a UTF-8 text file, preserving explicit newlines.

        Text is clipped at the logical canvas boundaries; no wrapping or pagination.
        """
        try:
            self._require_init()
            if self.font is None:
                raise RuntimeError("Select a font with set_font()")
            with open(filename, "r", encoding="utf-8-sig") as source:
                message = source.read()
            new_image = Image.new("1", (self.width, self.height), 255)
            ImageDraw.Draw(new_image).multiline_text((x, y), message, font=self.font, fill=0, spacing=spacing)
            self.image = new_image
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("load_text", exception)

    def load_image(self, filename, scale=False):
        """Load an image into the buffer; physical display changes only on update().

        scale=False: preserve original pixel size, clip from upper-left if too large.
        scale=True:  proportionally resize to fit and center on white background.
        """
        try:
            self._require_init()
            if not isinstance(scale, bool):
                raise ValueError("scale must be True or False")

            with Image.open(filename) as source:
                # Conversion to 1-bit occurs after resizing, preserving gray detail.
                if scale:
                    # Use the original image's aspect ratio, never stretch it.
                    source_width, source_height = source.size
                    if source_width <= 0 or source_height <= 0:
                        raise ValueError("Image has invalid dimensions")
                    factor = min(self.width / source_width, self.height / source_height)
                    new_width = max(1, min(self.width, round(source_width * factor)))
                    new_height = max(1, min(self.height, round(source_height * factor)))
                    # Pillow versions on Raspberry Pi OS Buster support LANCZOS.
                    scaled_image = source.convert("L").resize((new_width, new_height), Image.LANCZOS)
                    converted_image = scaled_image.convert("1")
                    x = (self.width - new_width) // 2
                    y = (self.height - new_height) // 2
                else:
                    converted_image = source.convert("1")
                    x = 0
                    y = 0

                # A full-size buffer is required by epd2in7.getbuffer().
                # Pillow paste clips oversize images at the buffer boundaries.
                new_image = Image.new("1", (self.width, self.height), 255)
                new_image.paste(converted_image, (x, y))

            self.image = new_image
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("load_image", exception)

    def update(self):
        try:
            self._require_init()
            # Pillow rotates counterclockwise; negate the requested clockwise angle.
            # epd2in7.getbuffer() expects native landscape (264 x 176) or portrait.
            native_image = self.image.rotate(-self.orientation, expand=True)
            self.epd.display(self.epd.getbuffer(native_image))
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("update", exception)

    def clear(self):
        try:
            self._require_init()
            # Clear the physical panel and the software image, synchronously.
            self.epd.Clear(0xFF)
            self.image.paste(255, (0, 0, self.width, self.height))
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("clear", exception)

    def reset(self):
        try:
            if self.epd is None:
                return True
            self.epd.reset()
            self.initialized = False
            self.last_error = None
            return True
        except Exception as exception:
            self.initialized = False
            return self._error("reset", exception)

    def close(self):
        if self.epd is None:
            return True
        try:
            # The manufacturer's sleep sequence does not erase the panel.
            self.epd.sleep()
            self.epd = None
            self.initialized = False
            self.last_error = None
            return True
        except Exception as exception:
            self.initialized = False
            return self._error("close", exception)
