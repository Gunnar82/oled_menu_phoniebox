""" Main menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.functions as fn
import integrations.playout as pc

class PinMenu(WindowBase):
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.pincode = ""
        self.descr = "PIN-Menü"
        self.window_on_back = "idle"
        self.line3 = ""
        self.drawtextx = 0

    def render(self):
         with canvas(self.device) as draw:
            mwidth = PinMenu.font.getsize(self.descr)
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr, font=PinMenu.font, fill="white")
            mwidth = PinMenu.font.getsize(self.pincode)
            draw.text((64 - int(mwidth[0]/2),20), text=self.pincode, font=PinMenu.font, fill="white")
            if self.font.getsize(self.line3[self.drawtextx:])[0] > 127:
                self.drawtextx += 1
            else:
                self.drawtextx = 0

            mwidth = PinMenu.font.getsize(self.line3)
            draw.text((64 - int(mwidth[0]/2),40), text=self.line3[self.drawtextx:], font=PinMenu.font, fill="white")


    def activate(self):
        self.pincode = ""
        self.line3 = ""


    def push_callback(self,lp=False):
        filename = '/home/pi/oledctrl/oled/pins/' + self.pincode

        try:
            with open(filename) as f:
                line = f.readlines()[0][len(settings.AUDIO_BASEPATH_BASE):].strip()
                pc.pc_playfolder(line)
                self.windowmanager.set_window("playlistmenu")
        except:
            self.line3 = "PIN n/a"


    def turn_callback(self, direction, key=None):
        if key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            self.pincode += key
        elif key == 'A':
            self.pincode = ""
        elif key == 'B':
            try:
                self.pincode = self.pincode[:-1]
            except:
                pass
        elif key == '#':
               self.windowmanager.set_window("idle")
        try:
            filename = '/home/pi/oledctrl/oled/pins/' + self.pincode
            with open(filename) as f:
                line = f.readlines()[0].strip()
                self.line3 = line[len(settings.AUDIO_BASEPATH_BASE):].replace("/", " | ")
        except:
            self.line3 = ""
