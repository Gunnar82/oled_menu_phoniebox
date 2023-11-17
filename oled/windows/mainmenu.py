""" Main menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings, colors

import config.symbols as symbols
import config.file_folder as cfg_file_folder

from integrations.functions import mountusb, get_folder_from_file
import asyncio, os

class Mainmenu(MenuBase):

    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager,loop,title)
        self.counter = 0
        self.descr.append ([ "Musik", symbols.SYMBOL_MUSIC,"foldermenu" ])
        self.descr.append([ "Hörspiele", symbols.SYMBOL_HOERSPIEL, "foldermenu" ])
        self.descr.append([ "Internetradio", symbols.SYMBOL_RADIO, "foldermenu" ])
        self.descr.append([ "USB-Stick", symbols.SYMBOL_USB,"foldermenu" ])
        self.descr.append([ "Audioausgabe", symbols.SYMBOL_HEADPHONE, "headphonemenu" ])
        self.descr.append([ "Ausschaltmenü", "\uf011", "shutdownmenu"])
        self.descr.append([ "Betriebsinfos", "\uf022", "infomenu" ])
        self.descr.append([ "WLAN / Hotspot", "\uf09e", "wlanmenu" ])
        self.descr.append([ "Firewall", "\uf1cb", "firewallmenu" ])
        self.descr.append([ "Download", symbols.SYMBOL_CLOUD, "downloadmenu"])
        self.descr.append([ "Tastensperre", symbols.SYMBOL_LOCKED, "lock" ])
        self.descr.append([ "Systemmenu", "\uf013", "systemmenu" ])

        self.window_on_back = "idle"

    async def push_handler(self):
        if self.counter == 1:
            settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_MUSIC
            settings.currentfolder = get_folder_from_file(cfg_file_folder.FILE_LAST_MUSIC)
        elif self.counter == 2:
            settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_HOERBUCH
            settings.currentfolder = get_folder_from_file(cfg_file_folder.FILE_LAST_HOERBUCH)
        elif self.counter == 3:
            settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_RADIO
            settings.currentfolder = get_folder_from_file(cfg_file_folder.FILE_LAST_RADIO)
        elif self.counter == 4:
            settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_USB
            settings.currentfolder = cfg_file_folder.AUDIO_BASEPATH_USB
            mountusb()

        self.windowmanager.set_window(self.descr[self.counter][2])



