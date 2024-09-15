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
import importlib

from ui.listbase import ListBase
import time
import integrations.playout as playout

from integrations.functions import *

import config.online as cfg_online
import config.file_folder as cfg_file_folder
import config.services as cfg_services


import config.bluetooth
import config.firewall


class SystemMenu(ListBase):
    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager, loop, title)
        self.loop = loop
        self.hostapd_status = get_hostapd_file_status()
        self.firewall_status = str(get_firewall_state())
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

        self.menu.append([""])
        self.menu.append(["> aktivieren"])
        self.menu.append(["> deaktivieren"])

        self.menu.append([""])
        self.menu.append(["> EIN"])
        self.menu.append(["> AUS"])

        self.menu.append([""])
        self.menu.append(["> aktivieren"])
        self.menu.append(["> deaktivieren"])

        self.menu.append([""])

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
            if self.position == 14:
                enable_firewall()
            elif self.position == 15:
                disable_firewall()
            else:
                if run_command(self.cmd) == True:
                    self.set_busy(self.menu[self.position][0],symbols.SYMBOL_PASS, busytext2="Erfolgreich")
                else:
                    self.set_busy(self.menu[self.position][0],symbols.SYMBOL_FAIL, busytext2="Fehler")
        finally:
            time.sleep(5)
            importlib.reload(config.firewall)
            importlib.reload(config.bluetooth)

            self.hostapd_status = get_hostapd_file_status()
            self.firewall_status = str(get_firewall_state())

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

            self.cmd = ["git pull", "sudo pip3 install -r requirements.txt", "sudo systemctl restart oled"]

        elif self.position == 8 or self.position == 9:
            if self.position == 9:
                self.cmd = "sudo ip link set wlan0 down"
            else:
                self.cmd = "sudo ip link set wlan0 up"

        elif self.position == 11:
            self.cmd = "sed -i 's/AUTO_ENABLED=False/AUTO_ENABLED=True/g' /home/pi/oledctrl/oled/config/firewall.py"

        elif self.position == 12:
            self.cmd = "sed -i 's/AUTO_ENABLED=True/AUTO_ENABLED=False/g' /home/pi/oledctrl/oled/config/firewall.py"


        elif self.position == 17:
            self.cmd = "sed -i 's/BLUETOOTH_AUTOCONNECT=False/BLUETOOTH_AUTOCONNECT=True/g' /home/pi/oledctrl/oled/config/bluetooth.py"

        elif self.position == 18:
            self.cmd = "sed -i 's/BLUETOOTH_AUTOCONNECT=True/BLUETOOTH_AUTOCONNECT=False/g' /home/pi/oledctrl/oled/config/bluetooth.py"


        elif self.position == 20:
            self.cmd = "sudo systemctl stop hostapd"

        elif self.position == 21:
            self.cmd = "sudo systemctl start hostapd"

        elif self.position == 22:
            self.cmd = "echo \"disabled\" > /home/pi/oledctrl/oled/config/hotspot"

        elif self.position == 23:
            self.cmd = "echo \"enabled\" > /home/pi/oledctrl/oled/config/hotspot"

        elif self.position > 24:
            self.cmd = "sudo systemctl restart %s" % (self.menu[self.position][0])


        self.loop.run_in_executor(None,self.exec_command)


    def render(self):
        self.menu[10] = [f"Firewall AUTO_ENABLED ({config.firewall.AUTO_ENABLED}):","h"]
        self.menu[13] = ["Firewall Status: %s " % ("AUS" if "deny" not in self.firewall_status else "EIN"),"h"]
        self.menu[16] = [f"Bluetooth_Autoconnect ({config.bluetooth.BLUETOOTH_AUTOCONNECT}):","h"]
        self.menu[19] = [f"hostapd (aktiviert: {self.hostapd_status}):", "h"]


        if self.processing:
            self.renderbusy()
        else:
            super().render()
