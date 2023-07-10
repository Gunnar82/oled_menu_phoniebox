""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

import integrations.bluetooth
import integrations.functions as fn

from datetime import datetime

class Start(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_NORMAL)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)

    def __init__(self, windowmanager, mopidyconnection):
        super().__init__(windowmanager)
        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.startup = datetime.now()
        self.conrasthandle = False
        self.hinttext = "Wird gestartet..."
        (self.hintwidth, self.hintheight) = Start.font.getsize(self.hinttext)
        self.symbol1 = settings.SYMBOL_SANDCLOCK
        (self.symbol1width,self.symbol1height) = Start.fontawesome.getsize(self.symbol1)

        self.xmid = int(settings.DISPLAY_WIDTH / 2)
        self.ymid = int (settings.DISPLAY_HEIGHT / 2)

    def render(self):
        with canvas(self.device) as draw:


            if self.mopidyconnection.connected and ((datetime.now() - self.startup).total_seconds() >= settings.START_TIMEOUT):
                #print ("init")
                self.windowmanager.set_window("idle")
            draw.text((self.xmid -int(self.hintwidth / 2), 3), text=self.hinttext, font=Start.font, fill="white")

            if settings.X728_ENABLED:
                symbol = settings.battsymbol

                draw.text((50, 20), text=symbol, font=Start.fontawesome, fill=fn.get_battload_color())
                draw.text((25, 50), text="%d%% geladen" % (settings.battcapacity), font=Start.font, fill=fn.get_battload_color())
            else:
                draw.text((self.xmid - int(self.symbol1width / 2), self.ymid -int(self.symbol1height / 2)), text=self.symbol1, font=Start.fontawesome, fill="white")


    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
