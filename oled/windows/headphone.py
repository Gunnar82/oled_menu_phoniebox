""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.bluetooth

class Headphonemenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=24)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0

    def render(self):
        with canvas(self.device) as draw:
            x_coord = 2 + self.counter * 35
            y_coord = 7

            draw.rectangle((x_coord, y_coord, x_coord+30, y_coord+40), outline=255, fill=0)

#            draw.text((13, 25), text="Zurück", font=Headphonemenu.font, fill="white")
            draw.text((5, 15), text="\uf0a8", font=Headphonemenu.faicons, fill="white")

#            draw.text((30, 25), text="Kopfhörer", font=Headphonemenu.font, fill="white")
            draw.text((45, 15), text="\uf293", font=Headphonemenu.faicons, fill="white")

#            draw.text((56, 25), text="Ja", font=Headphonemenu.font, fill="white")
            draw.text((75, 15), text="\uf026", font=Headphonemenu.faicons, fill="white")


    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            integrations.bluetooth.enable_dev_bt()
        elif self.counter == 2:
            integrations.bluetooth.enable_dev_local()
    def turn_callback(self, direction):
        if self.counter + direction <= 2 and self.counter + direction >= 0:
            self.counter += direction
