""" Start screen """
from PIL import ImageFont
from ui.listbase import WindowBase
from luma.core.render import canvas

from datetime import datetime

import settings
import time
import asyncio

from integrations.logging_config import *

logger = setup_logger(__name__)


import config.colors as colors
import config.symbols as symbols

class GetValue(WindowBase):
    contrasthandle = False
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_XXXL)
    font_l = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)

    window_on_back = "none"

    def __init__(self, windowmanager,loop,usersettings):
        super().__init__(windowmanager, loop,usersettings)
        self.busysymbol = symbols.SYMBOL_PROGRAMM
        self.timeout = False
        self.conrasthandle = False
        self.__value = 0
        self.__vmax = 100
        self.__vmin = 0
        self.__vstep = 1
        self.__unit = None
        self.finished = False
        self.__result = self.__vmin -1
        self.__min_text = "min"
        self.__max_text = "max"
        self.__hint_text = ""
        self.__windowtitle = ""
        self.__canceled = False

    def get_position(self):
        try:
            drawtext = str(self.__value)
            self.__hint_text = "min" if self.__value <= self.__vmin else "max" if self.__value >= self.__vmax else ""

            if self.__unit is not None: drawtext += self.__unit 

            width, height = self.font.getsize(drawtext)
            self.xy = (settings.DISPLAY_WIDTH - width) / 2, (settings.DISPLAY_HEIGHT - height) / 2

            width, height = self.font.getsize(self.__hint_text)
            self.xy_hint = (settings.DISPLAY_WIDTH - width) / 2, settings.DISPLAY_HEIGHT - height - 2


            width, height = self.font_l.getsize(self.__windowtitle)
            self.xy_windowtitle = (settings.DISPLAY_WIDTH - width) / 2, 0 #height

        except Exception as error:
            logger.debug(f"get_position: {error}")

    def render(self):
        with canvas(self.device) as draw:
            drawtext = f"{self.__value}"
            if self.__unit is not None: drawtext += self.__unit 

            draw.text((self.xy), drawtext ,font=self.font,fill="white") 

            if not self.__hint_text == "": draw.text((self.xy_hint), self.__hint_text ,font=self.font,fill=colors.COLOR_ORANGE)
            if not self.__windowtitle == "": draw.text((self.xy_windowtitle), self.__windowtitle ,font=self.font_l,fill=colors.COLOR_ORANGE)

            try:
                pos = (self.__value - self.__vmin) / (self.__vmax - self.__vmin)
                logger.debug(f"pos for progressbar: {pos}")
                self.render_progressbar_draw(draw,pos=pos,buttom_top=True)
            except Exception as error:
                logger.debug(f"render: {error}")

    async def __async_get_value(self, vmin, vmax, vstep, startpos,unit,windowtitle):
        if vmin > vmax: return startpos
        if startpos > vmax: startpos = vmax
        if startpos < vmin: startpos = vmin

        if vmin > vmax: return startpos
        self.__value = startpos
        self.__vmin = vmin
        self.__vmax = vmax
        self.__vstep = vstep
        self.__unit = unit
        self.__windowtitle = windowtitle
        self.get_position()

        while not self.finished and self.loop.is_running():
            await asyncio.sleep (0.2)
        return not self.__canceled, self.__value

    def getValue(self,vmin=0,vmax=100,vstep=1,startpos=50,unit=None,windowtitle=""):
        future = asyncio.run_coroutine_threadsafe(self.__async_get_value(vmin, vmax, vstep, startpos,unit,windowtitle), self.loop)
        return future.result()

    def activate(self):
        logger.debug("activate: startet")
        self.finished = False
        self.__canceled = False
        self.get_position()

    def deactivate(self):
        logger.debug("deactivate: startet")
        self.finished = True
        self.__canceled = False

    def push_callback(self,lp=False):
        logger.debug(f"push_callback")
        self.finished = True

    def turn_callback(self, direction, key=None):
        if key:
            logger.debug(f"turn_callback, key: {key}")
            if key in ['2','6']:
                direction = self.__vstep
            elif key in ['4','8']:
                direction = - self.__vstep
            elif key =='D':
                self.__value = self.__vmin
                direction = 0
            elif key == 'A':
                self.__value = self.__vmax
                direction = 0
            elif key in ['C']:
                    direction = - 5 * self.__vstep
            elif key in ['B']:
                    direction = 5 * self.__vstep
            elif key in ['#']:
                self.__canceled = True
                self.finished = True

        self.__value = min(max(self.__value + direction, self.__vmin), self.__vmax)

        self.get_position()