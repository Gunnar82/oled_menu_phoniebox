""" View class to inherit other views from """

import settings
from PIL import ImageFont
from luma.core.render import canvas

busyfont = ImageFont.truetype(settings.FONT_TEXT, size=12)
busyfaicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
busyfaiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=35)


class WindowBase():
    def __init__(self, windowmanager):
        self.windowmanager = windowmanager
        self.counter = 0
        self.page = 0
        self.device = self.windowmanager.device
        self.loop = self.windowmanager.loop
        self.timeout = True
        self.contrasthandle = True
        self.timeoutwindow="idle"
        self.window_on_back = "mainmenu"
        self.busy = False
        self.busysymbol = settings.SYMBOL_SANDCLOCK

    def renderbusy(self):
        print ("busy")
        with canvas(self.device) as draw:

            mwidth = busyfont.getsize(settings.PLEASE_WAIT)
            draw.text(((64 - int(mwidth[0]/2)), 5), text=settings.PLEASE_WAIT, font=busyfont, fill="white") #sanduhr

            mwidth = busyfaiconsbig.getsize(self.busysymbol)
            draw.text(((64 - int(mwidth[0]/2)), 25), text=self.busysymbol, font=busyfaiconsbig, fill=settings.COLOR_RED) #sanduhr

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        raise NotImplementedError()
