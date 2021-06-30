""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os


class Shutdownmenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=10)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=10)

    def __init__(self, windowmanager, mopidyconnection):
        super().__init__(windowmanager)
        self.counter = 0
        self.mopidyconnection = mopidyconnection
        self.execshutdown = False
        self.execreboot = False

    def activate(self):
        self.counter = 0

    def render(self):
        with canvas(self.device) as draw:
            draw.text((5, 2), text="Wirklich ausschalten?", font=Shutdownmenu.font, fill="white")
            if self.counter < 4:
                x_coord = 10 + (self.counter * 25)
                y_coord = 12
            else:
                x_coord = 10 + ((self.counter -4)*25)
                y_coord = 37
            draw.rectangle((x_coord, y_coord, x_coord+18, y_coord+25), outline=255, fill=0)

            draw.text((15, 14), text="Ja", font=Shutdownmenu.font, fill="white")
            draw.text((15, 25), text="\uf011", font=Shutdownmenu.faicons, fill="white")

            draw.text((40, 14), text="No", font=Shutdownmenu.font, fill="white")
            draw.text((40, 25), text="\uf0a8", font=Shutdownmenu.faicons, fill="white")

            draw.text((65, 14), text="RT", font=Shutdownmenu.font, fill="white")
            draw.text((65, 25), text="\uf0e2", font=Shutdownmenu.faicons, fill="white")

            draw.text((90, 14), text="0", font=Shutdownmenu.font, fill="white")
            draw.text((90, 25), text="\uf0a2", font=Shutdownmenu.faicons, fill="white")


#####
            draw.text((15, 40), text="15", font=Shutdownmenu.font, fill="white")
            draw.text((15, 51), text="\uf0f3", font=Shutdownmenu.faicons, fill="white")

            draw.text((40, 40), text="30", font=Shutdownmenu.font, fill="white")
            draw.text((40, 51), text="\uf0f3", font=Shutdownmenu.faicons, fill="white")

            draw.text((65, 40), text="60", font=Shutdownmenu.font, fill="white")
            draw.text((65, 51), text="\uf0f3", font=Shutdownmenu.faicons, fill="white")

            draw.text((90, 40), text="90", font=Shutdownmenu.font, fill="white")
            draw.text((90, 51), text="\uf0f3", font=Shutdownmenu.faicons, fill="white")


    def push_callback(self,lp=False):
        if self.counter == 0:
            self.mopidyconnection.stop()
            self.execshutdown = True
            print("Stopping event loop")
            self.loop.stop()
        elif self.counter == 1:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 2:
            self.windowmanager.set_window("start")
            self.mopidyconnection.stop()
            self.execreboot = True
            print("Stopping event loop")
            self.loop.stop()
        
        elif self.counter == 3:
            os.system("%s -c=shutdownafter -v=00" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 4:
            os.system("%s -c=shutdownafter -v=15" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 5:
            os.system("%s -c=shutdownafter -v=30" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 6:
            os.system("%s -c=shutdownafter -v=60" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 7:
            os.system("%s -c=shutdownafter -v=90" % settings.PLAYOUT_CONTROLS)
        
        self.windowmanager.set_window("idle")
            #self.mopidyconnection.stop()
            #self.execreboot = True
            #print("Stopping event loop")
            #self.loop.stop()

    def turn_callback(self, direction, ud=False):
        if ud:
            direction = direction * 4
        if self.counter + direction <= 5 and self.counter + direction >= 0:
            self.counter += direction
