""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.bluetooth
from datetime import datetime

class Ende(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=25)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.timeout = False
        self.startup = datetime.now()

    def activate(self):
        with canvas(self.device) as draw:
            mwidth = Ende.font.getsize(settings.shutdown_reason)
            draw.text((50, 3), text="wird", font=Ende.font, fill="white")
            draw.text((50, 20), text="\uf011", font=Ende.fontawesome, fill="white")
            draw.text((64 - int(mwidth[0]/2), 50), text=settings.shutdown_reason, font=Ende.font, fill="white")

    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
