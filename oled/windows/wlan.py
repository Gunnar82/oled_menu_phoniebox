""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import asyncio
import subprocess
import qrcode

class Wlanmenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=10)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=15)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self._active = False
        self._hostapd = False
        self.counter = 0
        self.descr = []
        self.descr.append("Zurück")
        self.descr.append("Hotspot umschalten")
        self._hostapd_wifi_ssid = "n/a"
        self._hostapd_wifi_psk = "n/a"
        self.wifi_ssid = "n/a"
        self._ip_addr = "n/a"
        self.timeout = False

    def activate(self):
        self._active = True
        self.loop.create_task(self._wlanstate())

    def deactivate(self):
        self._active = False




    def render(self):
        with canvas(self.device) as draw:


            mwidth = Wlanmenu.font.getsize(self.descr[self.counter])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter], font=Wlanmenu.font, fill="white")

            x_coord = 2 
            y_coord = 19+ self.counter * 20

            draw.rectangle((x_coord, y_coord, x_coord+20, y_coord+20), outline=255, fill=0)

            draw.text((5, 22), text="\uf0a8", font=Wlanmenu.faicons, fill="white") #zurück
            draw.text((5, 42), text="\uf09e" if self._hostapd else "\uf140", font=Wlanmenu.faicons, fill="white") #script starten
            draw.text((30, 22), text="IP: %s" % (self._ip_addr), font=Wlanmenu.font, fill="white") #zurück

            if self._hostapd:
                draw.text((30, 35), text=self._hostapd_wifi_ssid, font=Wlanmenu.font, fill="white") #zurück
                draw.text((30, 50), text=self._hostapd_wifi_psk, font=Wlanmenu.font, fill="white") #script starten
            else:
                draw.text((30,35), text="WiFi: %s" % (self.wifi_ssid), font=Wlanmenu.font, fill="white")

    async def _wlanstate(self):

        while self.loop.is_running():
            try:
                self._hostapd = True if os.system('systemctl is-active --quiet hostapd.service') == 0 else False
            except:
                pass

            try:
                subprocess_result = subprocess.Popen('hostname -I',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self._ip_addr = subprocess_output[0].decode('utf-8')
            except:
                self._ip_addr = "n/a"
            try:
                subprocess_result = subprocess.Popen('iwgetid',shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self.wifi_ssid = subprocess_output[0].decode('utf-8')
                self.wifi_ssid = self.wifi_ssid[self.wifi_ssid.rfind(":")+1:]
            except:
                self.wifi_ssid = "n/a"


            if self._hostapd:
                try:
                    subprocess_result = subprocess.Popen('cat /etc/hostapd/hostapd.conf  | grep ^ssid=',shell=True,stdout=subprocess.PIPE)
                    subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                    self._hostapd_wifi_ssid = subprocess_output[0].decode('utf-8')
                    self._hostapd_wifi_ssid = self._hostapd_wifi_ssid[self._hostapd_wifi_ssid.rfind("=")+1:]
                except:
                    self._hostapd_wifi_ssid = "n/a"

                try:
                    subprocess_result = subprocess.Popen('cat /etc/hostapd/hostapd.conf  | grep ^wpa_passphrase=',shell=True,stdout=subprocess.PIPE)
                    subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                    self._hostapd_wifi_psk = subprocess_output[0].decode('utf-8')
                    self._hostapd_wifi_psk = self._hostapd_wifi_psk[self._hostapd_wifi_psk.rfind("=")+1:]
                except:
                    self._hostapd_wifi_psk = "n/a"


            await asyncio.sleep(5)



    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            try:
                os.system('sudo /usr/bin/autohotspotN')

            except:
                pass

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'right' or key == '6' or key == '8':
                direction = 1
            elif key == 'left' or key == '4' or key == '2':
                direction = -1

        if self.counter + direction <= 1 and self.counter + direction >= 0:
            self.counter += direction
