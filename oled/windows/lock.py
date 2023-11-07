""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings, colors, symbols
import time

from datetime import datetime

class Lock(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.timeout = False
        self.window_on_back = "none"
        self._rendertime = 0.5

        self.windowmanager = windowmanager
        self.timeout = False
        self.unlockcode = ['up','left','left','right']
        self.currentkey = 0


    def activate(self):
        self.currentkey = 0
        self.hint = "System entsperren mit"

        self.busysymbol=symbols.SYMBOL_LOCK

    def render(self):

        for r in range(len(self.unlockcode)):
            if r == self.currentkey:
                self.unlockcode[r] = self.unlockcode[r].upper()
            else:
                self.unlockcode[r] = self.unlockcode[r].lower()
        self.set_busy("Tastensperre",self.busysymbol,busyrendertime=0.4, busytext3 = self.hint, busytext2 = ' '.join(self.unlockcode))


    def push_callback(self,lp=False):
        pass

    def turn_callback(self,direction, key=None):

        if key == self.unlockcode[self.currentkey].lower():
            self.busysymbol = symbols.SYMBOL_PASS
            self.currentkey += 1
        else:
            self.busysymbol = symbols.SYMBOL_FAIL
            self.currentkey = 0

        if self.currentkey >= len(self.unlockcode):
             self.currentkey = 0 

             self.windowmanager.set_window("idle")


    def deactivate(self):
            self.power_timer = False

