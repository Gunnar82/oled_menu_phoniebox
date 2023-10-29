""" View class to inherit other views from """

import settings, colors

from PIL import ImageFont
from luma.core.render import canvas


busyfont = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
busyfaicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_L)
busyfaiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXXL)


class WindowBase():
    changerender = False
    def __init__(self, windowmanager):
        self.windowtitle = "untitled"
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
        self.busytext1 = settings.PLEASE_WAIT
        self.busytext2 = ""
        self.busytext3 = ""
        self.busyrendertime = 3
        self._rendertime = 0.25

    def set_busy(self,busytext1,busysymbol=settings.SYMBOL_SANDCLOCK,busytext2="", busyrendertime=3,busytext3=""):
        self.busytext1 = busytext1
        self.busysymbol = busysymbol
        self.busytext2 = busytext2
        self.busytext3 = busytext3
        self.busyrendertime = busyrendertime
        self.busy = True

    def renderbusy(self,symbolcolor = colors.COLOR_RED, textcolor1=colors.COLOR_WHITE, textcolor2=colors.COLOR_WHITE):
        with canvas(self.device) as draw:

            mwidth,mheight = busyfont.getsize(self.busytext1)
            draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, 2), text=self.busytext1, font=busyfont, fill=textcolor1)

            if (self.busytext3 != ""):
                mwidth,mheight = busyfont.getsize(self.busytext3)
                draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, mheight + 2), text=self.busytext3, font=busyfont, fill=textcolor2) #sanduhr

            if (self.busytext2 != ""):
                mwidth,mheight = busyfont.getsize(self.busytext2)
                draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, settings.DISPLAY_HEIGHT - mheight - 2), text=self.busytext2, font=busyfont, fill=textcolor2) #sanduhr

            mwidth,mheight = busyfaiconsbig.getsize(self.busysymbol)
            draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, (settings.DISPLAY_HEIGHT - mheight) / 2), text=self.busysymbol, font=busyfaiconsbig, fill=symbolcolor) #sanduhr

    




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
