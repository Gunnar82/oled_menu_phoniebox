""" Main menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings, colors, file_folder, symbols

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
        self.descr.append([ "Update Radio", "\uf0c2", "none" ])

        self.window_on_back = "idle"

    async def push_handler(self):
        if self.counter == 1:
            settings.audio_basepath = file_folder.AUDIO_BASEPATH_MUSIC
            settings.currentfolder = get_folder_from_file(file_folder.FILE_LAST_MUSIC)
        elif self.counter == 2:
            settings.audio_basepath = file_folder.AUDIO_BASEPATH_HOERBUCH
            settings.currentfolder = get_folder_from_file(file_folder.FILE_LAST_HOERBUCH)
        elif self.counter == 3:
            settings.audio_basepath = file_folder.AUDIO_BASEPATH_RADIO
            settings.currentfolder = get_folder_from_file(file_folder.FILE_LAST_RADIO)
        elif self.counter == 4:
            settings.audio_basepath = file_folder.AUDIO_BASEPATH_USB
            settings.currentfolder = file_folder.AUDIO_BASEPATH_USB
            mountusb()
        elif self.counter == 12:
            if settings.UPDATE_RADIO:
                self.set_busy("Aktualisiere Radiostationen",busyrendertime=10)
                await asyncio.sleep(1)
                retv = os.system("wget  --no-check-certificate  -r %s  --no-parent -A txt -nH -P %s/" %(settings.ONLINE_RADIO_URL,file_folder.AUDIO_BASEPATH_BASE))
                await asyncio.sleep(1)
                self.set_busy("Erfolg" if retv == 0 else "Fehler")
            else:
                self.set_busy("Online Updates deaktiviert")



        self.windowmanager.set_window(self.descr[self.counter][2])



