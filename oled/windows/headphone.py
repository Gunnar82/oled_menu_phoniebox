""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.bluetooth

class Headphonemenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.descr = []
        self.descr.append("Zurück")
        self.descr.append(settings.NAME_DEV_BT_1 + " " + settings.ENABLED_DEV_BT_1)
        self.descr.append(settings.NAME_DEV_BT_2 + " " + settings.ENABLED_DEV_BT_2)
        self.descr.append("Lautsprecher")


    def render(self):
        with canvas(self.device) as draw:
            mwidth = Headphonemenu.font.getsize(self.descr[self.counter])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter], font=Headphonemenu.font, fill="white")

            x_coord = 2 + self.counter * 30
            y_coord = 27

            draw.rectangle((x_coord, y_coord, x_coord+20, y_coord+30), outline=255, fill=0)

#            draw.text((13, 25), text="Zurück", font=Headphonemenu.font, fill="white")
            draw.text((5, 35), text="\uf0a8", font=Headphonemenu.faicons, fill="white")
            text = "\uf293" if settings.ENABLED_DEV_BT_1 == "ON" else "\uf057"
#            draw.text((30, 25), text="Bluetooth 1", font=Headphonemenu.font, fill="white")
            draw.text((35, 35), text=text, font=Headphonemenu.faicons, fill="white")

            text = "\uf293" if settings.ENABLED_DEV_BT_2 == "ON" else "\uf057"
#            draw.text((30, 25), text="Kopfhörer", font=Headphonemenu.font, fill="white")
            draw.text((65, 35), text=text, font=Headphonemenu.faicons, fill="white")

#            draw.text((56, 25), text="Ja", font=Headphonemenu.font, fill="white")
            draw.text((95, 35), text="\uf028", font=Headphonemenu.faicons, fill="white")


    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1 and settings.ENABLED_DEV_BT_1 == "ON":
            integrations.bluetooth.enable_dev_bt_1()
            self.windowmanager.set_window("mainmenu")    
        elif self.counter == 2 and settings.ENABLED_DEV_BT_1 == "ON":
            integrations.bluetooth.enable_dev_bt_2()
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 3:
            integrations.bluetooth.enable_dev_local()
            self.windowmanager.set_window("mainmenu")

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'right':
                direction = 1
            elif key == 'left':
                direction = -1
            elif key == 'down':
                direction = 0
            else:
                direction = 0

        if self.counter + direction <= 3 and self.counter + direction >= 0:
            self.counter += direction
