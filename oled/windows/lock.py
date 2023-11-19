""" Start screen """
from ui.mainwindow import MainWindow
from luma.core.render import canvas
from PIL import ImageFont
import settings

import config.colors as colors
import config.symbols as symbols

import time,random
import asyncio

from datetime import datetime

class Lock(MainWindow):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)

    def __init__(self, windowmanager,loop,nowplaying):
        super().__init__(windowmanager, loop,nowplaying)

        self.timeout = False
        self.window_on_back = "none"
        self.busyrendertime = 0.25

        self.timeout = False
        self.unlockcodes = []

        self.unlockcodes.append( ['up','down','left','right','start','select','x','y','hl','hr'])
        self.unlockcodes.append( ['1','2','3','4','5','6','7','8','9','0','a','b','c','d'] )
        self.unlockindex = -1

        self.currentkey = 0

    def activate(self):
        self.unlockcode = []

        if "gpicase" in settings.INPUTS: self.unlockindex = 0
        elif "keypad4x4" in settings.INPUTS: self.unlockindex = 1

        if self.unlockindex == -1:
            self.set_busy("Kein kompatibler INPUT",symbols.SYMBOL_ERROR,set_window_to="idle")
        else:
            for r in range(0,4):
                length = len(self.unlockcodes[self.unlockindex])
                pos = random.randint(0,length-1)
                char = self.unlockcodes[ self.unlockindex ][pos]

                self.unlockcode.append(char)
                try:
                    self.unlockcodes[ self.unlockindex ].remove(char)
                except:
                    pass

            self.currentkey = 0

            self.busysymbol=symbols.SYMBOL_LOCKED
            self.genhint()

    def render(self):
        with canvas(self.device) as draw:
            super().render(draw)
            self.renderbusydraw(draw)

    def push_callback(self,lp=False):
        pass

    def turn_callback(self,direction, key=None):

        if key.lower() == self.unlockcode[self.currentkey].lower():
            self.busysymbol = symbols.SYMBOL_PASS
            self.currentkey += 1
        else:
            self.busysymbol = symbols.SYMBOL_FAIL
            self.currentkey = 0

        if self.currentkey >= len(self.unlockcode):
             self.currentkey = 0 
             self.set_busy("Gerät entsperrt",symbols.SYMBOL_UNLOCKED,set_window_to="idle")
        else:
            self.genhint()

    def genhint(self):
        self.busytext1 = ""
        for r in range(len(self.unlockcode)):
            if r == self.currentkey:
                self.unlockcode[r] = self.unlockcode[r].upper()
                self.busytext1 += ">%s< " % (self.unlockcode[r])
            else:
                self.unlockcode[r] = self.unlockcode[r].lower()
                self.busytext1 += self.unlockcode[r] + ' '


    def deactivate(self):
            self.power_timer = False

