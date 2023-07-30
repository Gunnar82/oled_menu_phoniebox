""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
from datetime import datetime

import settings

import integrations.bluetooth
from integrations.functions import get_battload_color
from integrations.logging import *


class Start(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_NORMAL)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)

    def __init__(self, windowmanager, mopidyconnection):
        super().__init__(windowmanager)
        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.startup = datetime.now()
        self.conrasthandle = False
        self.busytext1 = "Wird gestartet..."

    def render(self):
        if settings.X728_ENABLED:
            color = get_battload_color()
            self.busysymbol = settings.battsymbol
            self.busytext2 = "%d%% geladen" % (settings.battcapacity)
        else:
            color = settings.COLOR_WHITE

        self.renderbusy(symbolcolor=color, textcolor2=color)


        if self.mopidyconnection.connected and ((datetime.now() - self.startup).total_seconds() >= settings.START_TIMEOUT):
            log (lDEBUG,"start: init")
            self.windowmanager.set_window("idle")




    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
