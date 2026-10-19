#!/usr/bin/env python3

# Waveshare Text v0.1.0 - Waveshare_Text_v0_1_0.py
# Render text into a display-sized image without accessing display hardware.

import sys
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class WaveshareText:
    def __init__(self, width, height, orientation="landscape"):
        self.last_error = None
        self.font_path = None
        self.font_size = 14
        self.image = None
        self.orientation = None
        self.width = 0
        self.height = 0

        if not self.set_orientation(width, height, orientation):
            raise ValueError(self.last_error)

        self.set_font("DejaVu Sans", 14)

    def _error(self, operation, exception):
        self.last_error = "{}: {}".format(operation, exception)
        print("WaveshareText: " + self.last_error, file=sys.stderr)
        return False

    def set_orientation(self, width, height, orientation):
        try:
            if not isinstance(width, int) or not isinstance(height, int):
                raise ValueError("Display dimensions must be integers")
            if width <= 0 or height <= 0:
                raise ValueError("Display dimensions must be positive")
            if orientation not in ("landscape", "portrait"):
                raise ValueError("Orientation must be landscape or portrait")

            long_side = max(width, height)
            short_side = min(width, height)
            new_width, new_height = (
                (long_side, short_side) if orientation == "landscape"
                else (short_side, long_side)
            )

            # Changing orientation starts a new blank page.
            self.image = Image.new("1", (new_width, new_height), 255)
            self.width, self.height = new_width, new_height
            self.orientation = orientation
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("set_orientation", exception)

    def set_font(self, family="DejaVu Sans", size=14, style="Book"):
        try:
            if not isinstance(size, int) or size <= 0:
                raise ValueError("Font size must be a positive integer")

            # Find the requested installed family exactly. Do not allow
            # Fontconfig to silently substitute an unrelated font.
            result = subprocess.run(
                ["fc-list", "-f", "%{family}|%{style}|%{file}\n"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=5,
                check=True,
            )
            font_path = None
            for entry in result.stdout.splitlines():
                fields = entry.split("|", 2)
                if len(fields) != 3:
                    continue
                families, styles, candidate = fields
                family_names = [name.strip().casefold() for name in families.split(",")]
                style_names = [name.strip().casefold() for name in styles.split(",")]
                if family.casefold() in family_names and style.casefold() in style_names:
                    if Path(candidate).is_file():
                        font_path = candidate
                        break
            if font_path is None:
                raise ValueError("Requested font family/style not installed: {} / {}".format(family, style))

            ImageFont.truetype(font_path, size)
            self.font_path = font_path
            self.font_size = size
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("set_font", exception)

    def clear(self):
        try:
            self.image.paste(255, (0, 0, self.width, self.height))
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("clear", exception)

    def text(self, x, y, message, spacing=4):
        try:
            if not isinstance(x, int) or not isinstance(y, int):
                raise ValueError("Text coordinates must be integers")
            if not isinstance(message, str):
                raise TypeError("Text must be a Python string")
            if not isinstance(spacing, int) or spacing < 0:
                raise ValueError("Line spacing must be a nonnegative integer")
            if self.font_path is None:
                raise RuntimeError("No font selected")

            font = ImageFont.truetype(self.font_path, self.font_size)
            draw = ImageDraw.Draw(self.image)
            draw.multiline_text((x, y), message, font=font, fill=0, spacing=spacing)
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("text", exception)

    def textfile(self, filename, x=0, y=0, spacing=4):
        try:
            # Invalid UTF-8 sequences are replaced, not allowed to crash
            # the caller. UTF-8 BOMs are accepted.
            with open(filename, "r", encoding="utf-8-sig", errors="replace") as file:
                message = file.read()
            return self.text(x, y, message, spacing=spacing)
        except Exception as exception:
            return self._error("textfile", exception)

    def save(self, filename):
        try:
            self.image.save(filename)
            self.last_error = None
            return True
        except Exception as exception:
            return self._error("save", exception)

    def get_image(self):
        # Return a copy so callers cannot inadvertently modify our buffer.
        return self.image.copy()
