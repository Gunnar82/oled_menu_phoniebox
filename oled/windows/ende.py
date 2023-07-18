""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.bluetooth
from datetime import datetime

class Ende(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.timeout = False
        self.startup = datetime.now()

    def activate(self):
        with canvas(self.device) as draw:
            line="wird"
            (linex,liney) = Ende.font.getsize(line)
            draw.text(((settings.DISPLAY_WIDTH - linex) / 2 , 3), text=line, font=Ende.font, fill="white")

            line="\uf011"
            (linex,liney) = Ende.fontawesome.getsize(line)
            draw.text(( (settings.DISPLAY_WIDTH - linex) / 2, (settings.DISPLAY_HEIGHT - liney) / 2), text=line, font=Ende.fontawesome, fill="white")

            (linex, liney) = Ende.font.getsize(settings.shutdown_reason)
            draw.text(((settings.DISPLAY_WIDTH - linex) / 2 , settings.DISPLAY_HEIGHT - liney - 5), text=settings.shutdown_reason, font=Ende.font, fill="white")

    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
