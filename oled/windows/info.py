""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import socket
import subprocess
import os

class Infomenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
    ipaddr = ""
    wifi_ssid = ""
    hostapd = False
    temp = "n/a"
    window_on_back = "mainmenu"

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0


    def render(self):
        with canvas(self.device) as draw:

            try:
                subprocess_result = subprocess.Popen('iwgetid',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.wifi_ssid = subprocess_output[0].decode('utf-8')
                self.wifi_ssid = self.wifi_ssid[self.wifi_ssid.rfind(":")+1:]
            except:
                self.wifi = "n/a"

            try:
                subprocess_result = subprocess.Popen('/opt/vc/bin/vcgencmd measure_temp',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.temp = subprocess_output[0].decode('utf-8')
            except:
                self.temp = "n/a"

            try:
                subprocess_result = subprocess.Popen('hostname -I',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.ipaddr = subprocess_output[0].decode('utf-8')
            except:
                self.ipaddr = "n/a"

            try:
                self.hostapd = True if os.system('systemctl is-active --quiet hostapd.service') == 0 else False
            except:
                pass
            draw.text((1, 1), text="IP: " + self.ipaddr, font=Infomenu.font, fill="white")
            draw.text((1, 16), text="WiFi: " + self.wifi_ssid, font=Infomenu.font, fill="white")
            draw.text((1, 31), text="hostapdi: " + str(self.hostapd), font=Infomenu.font, fill="white")
            draw.text((1, 46), text=self.temp, font=Infomenu.font, fill="white")


    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")

    def turn_callback(self, direction, key=None):
        if self.counter + direction <= 0 and self.counter + direction >= 0:
            self.counter += direction
