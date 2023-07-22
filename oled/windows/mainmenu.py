""" Main menu """
from ui.menubase import MenuBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
from integrations.functions import mountusb

class Mainmenu(MenuBase):

    def __init__(self, windowmanager,title):
        super().__init__(windowmanager,title)
        self.counter = 0
        self.descr.append([ "Zurück", "\uf0a8"])
        self.descr.append ([ "Musik", settings.SYMBOL_MUSIC])
        self.descr.append([ "Hörspiele", settings.SYMBOL_HOERSPIEL])
        self.descr.append([ "Internetradio", settings.SYMBOL_RADIO])
        self.descr.append([ "USB-Stick", settings.SYMBOL_USB] )
        self.descr.append([ "Audioausgabe", "\uf025"])
        self.descr.append([ "Ausschaltmenü", "\uf011"])
        self.descr.append([ "Betriebsinfos", "\uf022"])
        self.descr.append([ "WLAN / Hotspot", "\uf09e"])
        self.descr.append([ "Firewall", "\uf1cb"])

        self.window_on_back = "idle"

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
                settings.audio_basepath = settings.AUDIO_BASEPATH_USB
                settings.currentfolder = settings.AUDIO_BASEPATH_USB
                mountusb()
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 5:
                self.windowmanager.set_window("headphonemenu")
            elif self.counter == 6:
                self.windowmanager.set_window("shutdownmenu")
            elif self.counter == 7:
                self.windowmanager.set_window("infomenu")
            elif self.counter == 8:
                self.windowmanager.set_window("wlanmenu")
            elif self.counter == 9:
                self.windowmanager.set_window("firewallmenu")

