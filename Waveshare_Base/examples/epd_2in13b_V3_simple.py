#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in13b_V3 Demo")

    epd = epd2in13b_V3.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    time.sleep(1)

    # Drawing on the image
    logging.info("Drawing")
    font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    logging.info("1.Drawing on the Horizontal image...")
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    HRYimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126  ryimage: red or yellow image
    drawblack = ImageDraw.Draw(HBlackimage)
    drawry = ImageDraw.Draw(HRYimage)

#     logging.info("Clearing e-Ink screen")
#     epd.init()
#     epd.Clear()
    logging.info("Writing test message. . .")
    drawblack.text((10, 0), 'hello world', font = font20, fill = 0)
    drawblack.text((10, 20), '2.13inch e-Paper bc', font = font20, fill = 0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    time.sleep(2)

    logging.info("Goto Sleep...")
    drawblack.text((10, 40), 'Going to sleep. . .', font = font20, fill = 0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13b_V3.epdconfig.module_exit()
    exit()
