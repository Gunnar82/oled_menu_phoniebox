""" Main menu """
from ui.menubase import MenuBase
from luma.core.render import canvas
from PIL import ImageFont
import settings, colors, file_folder

from integrations.functions import mountusb, get_folder_from_file
import asyncio

class Mainmenu(MenuBase):

    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager,loop,title)
        self.counter = 0
        self.descr.append ([ "Musik", settings.SYMBOL_MUSIC])
        self.descr.append([ "Hörspiele", settings.SYMBOL_HOERSPIEL])
        self.descr.append([ "Internetradio", settings.SYMBOL_RADIO])
        self.descr.append([ "USB-Stick", settings.SYMBOL_USB] )
        self.descr.append([ "Audioausgabe", "\uf025"])
        self.descr.append([ "Ausschaltmenü", "\uf011"])
        self.descr.append([ "Betriebsinfos", "\uf022"])
        self.descr.append([ "WLAN / Hotspot", "\uf09e"])
        self.descr.append([ "Firewall", "\uf1cb"])
        self.descr.append([ "Download", settings.SYMBOL_CLOUD])

        self.window_on_back = "idle"

    async def push_handler(self):
        if False == True:
            self.counter = 6 if (self.counter < 5)  else 1
        else:
            if self.counter == 1:
                settings.audio_basepath = file_folder.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = get_folder_from_file(settings.FILE_LAST_MUSIC)
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 2:
                settings.audio_basepath = file_folder.AUDIO_BASEPATH_HOERBUCH
                settings.currentfolder = get_folder_from_file(settings.FILE_LAST_HOERBUCH)
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 3:
                settings.audio_basepath = file_folder.AUDIO_BASEPATH_RADIO
                settings.currentfolder = get_folder_from_file(settings.FILE_LAST_RADIO)
                self.windowmanager.set_window("foldermenu")
            elif self.counter == 4:
                settings.audio_basepath = file_folder.AUDIO_BASEPATH_USB
                settings.currentfolder = file_folder.AUDIO_BASEPATH_USB
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
            elif self.counter == 10:
                self.windowmanager.set_window("downloadmenu")

