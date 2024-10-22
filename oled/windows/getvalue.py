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

import config.user_settings as csettings


class GetValue(WindowBase):
    contrasthandle = False
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_XXXL)

    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop)
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

    def get_position(self):
        try:
            drawtext = str(self.__value)
            if self.__unit is not None: drawtext += self.__unit 

            width, height = self.font.getsize(drawtext)
            self.xy = (settings.DISPLAY_WIDTH - width) / 2, (settings.DISPLAY_HEIGHT - height) / 2
        except Exception as error:
            logger.debug(f"get_position: {error}")

    def render(self):
        with canvas(self.device) as draw:
            drawtext = f"{self.__value}"
            if self.__unit is not None: drawtext += self.__unit 
            draw.text((self.xy), drawtext ,font=self.font,fill="white") 

    async def __async_get_value(self, vmin, vmax, vstep, startpos,unit):
        self.__value = startpos
        self.__vmin = vmin
        self.__vmax = vmax
        self.__vstep = vstep
        self.__unit = unit
        self.get_position()

        while not self.finished and self.loop.is_running():
            await asyncio.sleep (0.2)

        return self.__value

    def getValue(self,vmin=0,vmax=100,vstep=1,startpos=50,unit=None):
        future = asyncio.run_coroutine_threadsafe(self.__async_get_value(vmin, vmax, vstep, startpos,unit), self.loop)
        return future.result()

    def activate(self):
        logger.debug("activate: startet")
        self.finished = False
        self.get_position()

    def deactivate(self):
        logger.debug("deactivate: startet")
        self.finished = True


    def push_callback(self,lp=False):
        logger.debug(f"push_callback")
        self.finished = True

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                direction = self.__vstep
            elif key == 'down' or key == '8':
                direction = - self.__vstep
            elif key =='A':
                self.__value = 0
                direction = 0
            elif key == 'D':
                self.__value = self.__vmax
                direction = 0
            elif key == 'B' or key== 'hl':
                    direction = - 10 * self.__vstep
            elif key == 'C' or key == 'hr':
                    direction = 10 * self.__vstep

        if self.__value + direction  >= self.__vmax : # zero based
            self.__value = self.__vmax
        elif self.__value + direction < self.__vmin: # base counter is 2
            self.position = self.__vmin
        else:
           self.__value += direction

        self.get_position()