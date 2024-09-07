""" Playlist menu """
import settings

import config.colors as colors
import config.symbols as symbols

import re
import imp
import time
import requests
import htmllistparse
import subprocess,os
import asyncio
import shutil

from ui.listbase import ListBase
import time
import integrations.playout as playout
from integrations.functions import get_size,delete_local_online_folder

import config.online as cfg_online
import config.file_folder as cfg_file_folder
import config.services as cfg_services

class SystemMenu(ListBase):
    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager, loop, title)
        self.loop = loop
        self.window_on_back = "idle"
        self.timeout = False
        self.handle_left_key = False
        self.processing = False
        self.totalsize = 0
        self.menu.append(["Update Radiosender"])
        self.menu.append(["Lösche Online-Ordner"])
        self.menu.append(["Lösche Online-Status Online"])

        self.menu.append(["Lösche Hörspielstatus"])
        self.menu.append(["Lösche Musikstatus"])
        self.menu.append(["Lösche Radiostatus"])
        self.menu.append(["Lösche Onlinestatus"])

        self.menu.append(["Update OLED"])

        self.menu.append(["WLAN: aus"])
        self.menu.append(["WLAN: an"])

        self.menu.append(["Bluetooth: autoconnect AN"])
        self.menu.append(["Bluetooth: autoconnect AUS"])

        self.menu.append(["> service hostapd:", "h"])

        self.menu.append([" beenden"])
        self.menu.append([" starten"])
        self.menu.append([" deaktivieren"])
        self.menu.append([" aktivieren"])


        self.menu.append(["> Dienste neustarten:", "h"])

        for srv in cfg_services.RESTART_LIST:
            self.menu.append(["%s" % (srv)])

    def activate(self):
        self.cmd = ""

    def exec_command(self):
        try:
            self.processing = True
            subprocess_result = subprocess.Popen(self.cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
            if subprocess_result.returncode == 0:
                self.set_busy(self.menu[self.position][0],symbols.SYMBOL_PASS, busytext2="Erfolgreich")
            else:
                self.set_busy(self.menu[self.position][0],symbols.SYMBOL_FAIL, busytext2=subprocess_output[0].decode())
        finally:
            time.sleep(5)
            self.processing = False


    async def push_handler(self,button = '*'):
        self.cmd = ""
        self.set_busy("Verarbeite...",busytext2=self.menu[self.position][0],busyrendertime=5)

        if self.position == 0:
            if cfg_online.UPDATE_RADIO:
                self.cmd = "wget  --no-verbose --no-check-certificate  -r %s  --no-parent -A txt -nH -P %s/" %(cfg_online.ONLINE_RADIO_URL,cfg_file_folder.AUDIO_BASEPATH_BASE)

            else:
                self.set_busy("Online Updates deaktiviert")

        elif self.position == 1:
            delete_local_online_folder()

        elif self.position == 2:
            self.cmd = "wget  --no-verbose --no-check-certificate %sdeletepos.php?confirm=true -O-" %(cfg_online.ONLINE_SAVEPOS)

        elif self.position >=3 and self.position <= 6:
            if self.position == 3:
                what = cfg_file_folder.FILE_LAST_HOERBUCH
            elif self.position == 4:
                what = cfg_file_folder.FILE_LAST_MUSIC
            elif self.position == 5:
                what = cfg_file_folder.FILE_LAST_RADIO
            else:
                what = cfg_file_folder.FILE_LAST_ONLINE

            self.cmd = "sudo rm %s" % (what)


        elif self.position == 7:

            self.cmd = "cd /home/pi/oledctrl && git pull && sudo pip3 install -r requirements.txt && sudo systemctl restart oled"

        elif self.position == 8 or self.position == 9:
            if self.position == 9:
                self.cmd = "sudo ip link set wlan0 down"
            else:
                self.cmd = "sudo ip link set wlan0 up"

        elif self.position == 10:
            self.cmd = "sed -i 's/BLUETOOTH_AUTOCONNECT=False/BLUETOOTH_AUTOCONNECT=True/g' /home/pi/oledctrl/oled/config/bluetooth.py"

        elif self.position == 11:
            self.cmd = "sed -i 's/BLUETOOTH_AUTOCONNECT=True/BLUETOOTH_AUTOCONNECT=False/g' /home/pi/oledctrl/oled/config/bluetooth.py"

        elif self.position == 13:
            self.cmd = "sudo systemctl stop hostapd"

        elif self.position == 14:
            self.cmd = "sudo systemctl start hostapd"

        elif self.position == 15:
            self.cmd = "echo \"disabled\" > /home/pi/oledctrl/oled/config/hotspot"

        elif self.position == 16:
            self.cmd = "echo \"enabled\" > /home/pi/oledctrl/oled/config/hotspot"

        else:
            self.cmd = "sudo systemctl restart %s" % (self.menu[self.position][0])


        self.loop.run_in_executor(None,self.exec_command)



    def push_callback(self,lp=False):
        if self.position < 0:
            self.windowmanager.set_window(self.window_on_back)
        elif self.position == 12:
            pass
        else:
            self.set_busy("Verarbeite...", busytext2=self.menu[self.position][0])
            self.loop.create_task(self.push_handler())


    def render(self):
        if self.processing:
            self.renderbusy()
        else:
            super().render()
