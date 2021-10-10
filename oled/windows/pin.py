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

    def render(self):
         with canvas(self.device) as draw:
            mwidth = PinMenu.font.getsize(self.descr)
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr, font=PinMenu.font, fill="white")
            mwidth = PinMenu.font.getsize(self.pincode)
            draw.text((64 - int(mwidth[0]/2),20), text=self.pincode, font=PinMenu.font, fill="white")


    def activate(self):
        self.pincode = ""


    def push_callback(self,lp=False):
        filename = '/home/pi/oledctrl/oled/pins/' + self.pincode

        try:
            with open(filename) as f:
                line = f.readlines()[0]
                pc.pc_playfolder(line)
        except:
            self.descr = "PIN n/a"


    def turn_callback(self, direction, key=None):
        if key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            self.pincode += key
        elif key == '#':
               self.windowmanager.set_window("idle")