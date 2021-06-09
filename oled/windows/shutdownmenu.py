""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os


class Shutdownmenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=14)

    def __init__(self, windowmanager, mopidyconnection):
        super().__init__(windowmanager)
        self.counter = 0
        self.mopidyconnection = mopidyconnection
        self.execshutdown = False
        self.execreboot = False

    def render(self):
        with canvas(self.device) as draw:
            draw.text((5, 2), text="Wirklich ausschalten?", font=Shutdownmenu.font, fill="white")
            if self.counter == 0:
                x_coord = 10
                y_coord = 22
            elif self.counter == 1:
                x_coord = 47
                y_coord = 22
            else:
                x_coord = 89
                y_coord = 22
            draw.rectangle((x_coord, y_coord, x_coord+30, y_coord+40), outline=255, fill=0)

            draw.text((13, 25), text="Nein", font=Shutdownmenu.font, fill="white")
            draw.text((15, 40), text="\uf0a8", font=Shutdownmenu.faicons, fill="white")

            draw.text((56, 25), text="Ja", font=Shutdownmenu.font, fill="white")
            draw.text((55, 40), text="\uf011", font=Shutdownmenu.faicons, fill="white")

            draw.text((92, 25), text="S60", font=Shutdownmenu.font, fill="white")
            draw.text((94, 40), text="\uf0a2", font=Shutdownmenu.faicons, fill="white")

    def push_callback(self):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            self.mopidyconnection.stop()
            self.execshutdown = True
            print("Stopping event loop")
            self.loop.stop()
        elif self.counter == 2:
            os.system("%s -c=shutdownafter -v=60" % settings.PLAYOUT_CONTROLS)
            self.windowmanager.set_window("idle")
            #self.mopidyconnection.stop()
            #self.execreboot = True
            #print("Stopping event loop")
            #self.loop.stop()

    def turn_callback(self, direction):
        if self.counter + direction <= 2 and self.counter + direction >= 0:
            self.counter += direction
