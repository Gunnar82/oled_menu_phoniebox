""" Main menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class Mainmenu(WindowBase):
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.descr = []
        self.descr.append("Zurück")
        self.descr.append ("Musik")
        self.descr.append("Hörspiele")
        self.descr.append("Internetadio")
        self.descr.append("Einstellungen")
        self.descr.append("Ausschaltmenü")
        self.descr.append("Betriebsinfos")
        self.descr.append("WLAN / Hotspot")

    def render(self):
        with canvas(self.device) as draw:
            mwidth = Mainmenu.font.getsize(self.descr[self.counter])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter], font=Mainmenu.font, fill="white")
 
            #rectangle as selection marker
            if self.counter < 3: #3 icons in one row
                y_coord = 15
                x_coord = 7 + self.counter * 35
            elif self.counter >=3 and self.counter < 6:
                y_coord = 44
                x_coord = 6 + (self.counter - 3) * 35
            if self.counter >=6 and self.counter  < 9: #3 icons in one row
                y_coord = 15
                x_coord = 7 + (self.counter - 6) * 35

            draw.rectangle((x_coord, y_coord, x_coord+25, y_coord+25), outline=255, fill=0)

            #icons as menu buttons
            if self.counter <= 5:
                draw.text((11, 20), text="\uf0a8", font=Mainmenu.faicons, fill="white") #back
                draw.text((44, 20), text="\uf001", font=Mainmenu.faicons, fill="white") #musik
                draw.text((83, 20), text="\uf02d", font=Mainmenu.faicons, fill="white") #hoerbuch
                draw.text((11, 46), text="\uf1eb", font=Mainmenu.faicons, fill="white") #radio
                draw.text((44, 46), text="\uf085", font=Mainmenu.faicons, fill="white") #infos
                draw.text((83, 46), text="\uf011", font=Mainmenu.faicons, fill="white") #shutdown
            elif self.counter <= 11:
                draw.text((11, 20), text="\uf022", font=Mainmenu.faicons, fill="white") #infos
                draw.text((44, 20), text="\uf09e", font=Mainmenu.faicons, fill="white") #infos
        

    def push_callback(self,lp=False):
        if lp == True:
            self.counter = 6 if (self.counter < 5)  else 1 
        else:
            if self.counter == 0:
                self.windowmanager.set_window("idle")
            elif self.counter == 1:
                settings.audio_basepath = settings.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = settings.AUDIO_BASEPATH_MUSIC
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 2:
                settings.audio_basepath = settings.AUDIO_BASEPATH_HOERBUCH
                settings.currentfolder = settings.AUDIO_BASEPATH_HOERBUCH
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 3:
                settings.audio_basepath = settings.AUDIO_BASEPATH_RADIO
                settings.currentfolder = settings.AUDIO_BASEPATH_RADIO
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 4:
                self.windowmanager.set_window("headphonemenu")
            elif self.counter == 5:
                self.windowmanager.set_window("shutdownmenu")
            elif self.counter == 6:
                self.windowmanager.set_window("infomenu")
            elif self.counter == 7:
                self.windowmanager.set_window("wlanmenu")

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up':
                direction = -3
            elif key == 'down':
                direction = 3
            elif key == 'left':
                direction = -1
            else:
                direction = 1

        if (self.counter + direction < 8 and self.counter + direction >= 0):
            self.counter += direction
