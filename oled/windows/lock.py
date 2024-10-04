""" Start screen """
from ui.mainwindow import MainWindow
from luma.core.render import canvas
from PIL import ImageFont
import settings

import config.colors as colors
import config.symbols as symbols

import time,random

from datetime import datetime

class Lock(MainWindow):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
    busysymbol=symbols.SYMBOL_LOCKED

    def __init__(self, windowmanager,loop,nowplaying):
        super().__init__(windowmanager, loop,nowplaying)

        self.timeout = False
        self.window_on_back = "idle"
        self.busyrendertime = 0.25

        self.timeout = False
        self.unlockindex = -1

        self.currentkey = 0
        self.handle_key_back = False



    def gen_unlockcodes(self):
        self.unlockcodes = []

        self.unlockcodes.append( ['up','down','left','right','start','select','x','hl','hr'])
        self.unlockcodes.append( ['1','2','3','4','5','6','7','8','9','0','a','b','c','d'] )


    def activate(self):
        self.gen_unlockcodes()

        self.unlockcode = []

        if "gpicase" in settings.INPUTS: self.unlockindex = 0
        elif "keypad4x4" in settings.INPUTS: self.unlockindex = 1

        if self.unlockindex == -1:
            self.set_busyinfo(item="Kein kompatibler INPUT",symbol=symbols.SYMBOL_ERROR,wait=5,set_window=True)
        else:
            try:
                for r in range(0,4):
                    length = len(self.unlockcodes[self.unlockindex])
                    pos = random.randint(0,length-1)
                    char = self.unlockcodes[ self.unlockindex ][pos]

                    self.unlockcode.append(char)
                    self.unlockcodes[ self.unlockindex ].remove(char)
            except:
                self.gen_unlockcodes()
                self.set_busyinfo(item="Random Fehler",set_window=True)


            self.currentkey = 0

            self.genhint()

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
             self.set_busyinfo(item="Gerät entsperrt",symbol=symbols.SYMBOL_UNLOCKED,wait=5,set_window=True)
        else:
            self.genhint()

    def genhint(self):
        self.unlocktext = ""
        for r in range(len(self.unlockcode)):
            if r == self.currentkey:
                self.unlockcode[r] = self.unlockcode[r].upper()
                self.unlocktext += ">%s< " % (self.unlockcode[r])
            else:
                self.unlockcode[r] = self.unlockcode[r].lower()
                self.unlocktext += self.unlockcode[r] + ' '
        self.textwidth, temp = self.font.getsize(self.unlocktext)


    def deactivate(self):
            self.power_timer = False

    def render(self):
        with canvas(self.device) as draw:
            super().render(draw)
            #draw.text((, settings.DISPLAY_HEIGHT - 4*settings.IDLE_LINE_HEIGHT ), self.drawline2, font=self.font, fill="white")
            draw.text(((settings.DISPLAY_WIDTH - self.textwidth) / 2, settings.DISPLAY_HEIGHT - 4*settings.IDLE_LINE_HEIGHT ), self.unlocktext , font=self.font, fill="white")
