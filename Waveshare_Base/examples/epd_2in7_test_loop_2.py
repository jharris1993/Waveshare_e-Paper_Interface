#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

while(1 == 1):
    try:
        logging.info("epd2in7 Demo")
        epd = epd2in7.EPD()

        '''2Gray(Black and white) display'''
        logging.info("init and Clear")
        epd.init()
        epd.Clear(0xFF)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)

        epd.Init_4Gray()

        #display 4Gra bmp
        Himage = Image.open(os.path.join(picdir, '2in7_Scale1.bmp'))
        epd.display_4Gray(epd.getbuffer_4Gray(Himage))
        time.sleep(2)

        #display Pico bmp
        Himage = Image.open(os.path.join(picdir, 'Pico_2in7.bmp'))
        epd.display_4Gray(epd.getbuffer_4Gray(Himage))
        time.sleep(2)

        logging.info("Clear...")
        epd.Clear(0xFF)
        logging.info("Goto Sleep...")
        epd.sleep()

    except IOError as e:

        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
#        epd2in7.epdconfig.module_exit()
        logging.info("Clear...")
        epd.Clear(0xFF)
        logging.info("Goto Sleep...")
        epd.sleep()
        exit()
