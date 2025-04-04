""" Main menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.symbols as symbols
import config.file_folder as cfg_file_folder

from integrations.functions import mountusb, get_folder_from_file
import os

class Mainmenu(MenuBase):

    def __init__(self, windowmanager,loop,usersettings,title,musicmanager):
        super().__init__(windowmanager,loop,usersettings,title)
        self.usersettings = usersettings
        self.counter = 0
        self.musicmanager = musicmanager
        self.descr.append ([ "Musik", symbols.SYMBOL_MUSIC,"foldermenu" ])
        self.descr.append([ "Hörspiele", symbols.SYMBOL_HOERSPIEL, "foldermenu" ])
        self.descr.append([ "Internetradio", symbols.SYMBOL_RADIO, "radiomenu"])
        self.descr.append([ "Online", symbols.SYMBOL_CLOUD, "downloadmenu"])
        self.descr.append([ "USB-Stick", symbols.SYMBOL_USB,"foldermenu" ])
        self.descr.append([ "Betriebsinfos", "\uf022", "infomenu" ])
        self.descr.append([ "Audioausgabe" if self.usersettings.BLUETOOTH_ENABLED else "Bluetooth deaktiviert", symbols.SYMBOL_BLUETOOTH_OFF, "headphonemenu" ])
        self.descr.append([ "Systemmenu", "\uf013", "systemmenu" ])
        self.descr.append([ "Tastensperre", symbols.SYMBOL_LOCKED, "lock" ])
        self.descr.append([ "Ausschaltmenü", "\uf011", "shutdownmenu"])
        self.descr.append([ "Snake", "\uf011", "snakegame"])

        self.window_on_back = "idle"

    def push_handler(self):
        try:
            if self.counter == 1:
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = self.musicmanager.get_latest_folder('Musik')
            elif self.counter == 2:
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_HOERBUCH
                settings.currentfolder = self.musicmanager.get_latest_folder('Hörspiele')
            elif self.counter == 3:
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_RADIO
                settings.currentfolder = self.musicmanager.get_latest_folder('Radio')
            elif self.counter == 5:
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_USB
                settings.currentfolder = cfg_file_folder.AUDIO_BASEPATH_USB
                mountusb()

            self.windowmanager.set_window(self.descr[self.counter][2])
        except Exception as error:
            print (error)


