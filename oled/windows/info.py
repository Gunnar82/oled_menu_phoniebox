""" Shutdown menu """
from ui.listbase import ListBase
from luma.core.render import canvas
from PIL import ImageFont

import settings
import asyncio

import config.colors as colors
import integrations.functions as fn

import socket
import subprocess
import os

class Infomenu(ListBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_NORMAL)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XL)
    ipaddr = ""
    wifi_ssid = ""
    hostapd = False
    temp = "n/a"
    window_on_back = "mainmenu"

    def __init__(self, windowmanager, loop):
        super().__init__(windowmanager, loop,"Systeminfo")
        self.counter = 0
        self.loop = loop
        self.linewidth, self.lineheight = self.font.getsize("000")
        self.handle_left_key = False

    def activate(self):
        self.active = True
        self.loop.create_task(self.generate())

    def deactivate(self):
        self.active = False


    async def generate(self):
        while self.loop.is_running() and self.active:
            try:
                subprocess_result = subprocess.Popen('iwgetid',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.wifi_ssid = subprocess_output[0].decode()
                self.wifi_ssid = self.wifi_ssid[self.wifi_ssid.rfind(":")+1:]
            except:
                self.wifi = "n/a"

            try:
                subprocess_result = subprocess.Popen('/opt/vc/bin/vcgencmd measure_temp',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.temp = subprocess_output[0].decode()
            except:
                self.temp = "n/a"

            try:
                subprocess_result = subprocess.Popen('hostname -I',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.ipaddr = subprocess_output[0].decode()
            except:
                self.ipaddr = "n/a"

            try:
                self.hostapd = True if os.system('systemctl is-active --quiet hostapd.service') == 0 else False
            except:
                pass

            try:
                subprocess_result = subprocess.Popen('df -hl -text4 -tvfat -text3 -traiserfs --output=pcent,target,size | grep / ',shell=True,stdout=subprocess.PIPE)
                #subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                subprocess_output = subprocess_result.stdout.readlines()
                self.dfh = subprocess_output
                #self.dfh = subprocess_output[0].decode().split()
            except:
                self.dfh = "n/a"

            try:
                self.hostapd = True if os.system('systemctl is-active --quiet hostapd.service') == 0 else False
            except:
                pass


            self.menu = []
            self.menu.append(["IP: " + self.ipaddr, "c"] )
            self.menu.append(["WiFi: " + self.wifi_ssid, "c"])
            self.menu.append(["hostapdi: " + str(self.hostapd), "c"])
            self.menu.append(["OLED Version: " + fn.get_oledversion(), "c"])
            self.menu.append([self.temp, "comment"])

            self.menu.append(["Disk-Usage:", "c"])
            for e in self.dfh:
                self.menu.append([e.decode(), "c"])


            await asyncio.sleep(10)


    def push_callback(self,lp=False):
        self.windowmanager.set_window("mainmenu")
