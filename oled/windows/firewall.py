""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import socket
import subprocess
import os
import asyncio
import re

class Firewallmenu(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self._ufw_status = "n/a"


    def render(self):
        with canvas(self.device) as draw:
            mwidth = Firewallmenu.font.getsize("Firewall")
            draw.text((64 - int(mwidth[0]/2),1), text="Firewall", font=Firewallmenu.font, fill="white")

            draw.text((10, 15), text=self._ufw_status, font=Firewallmenu.font, fill="white")
            


    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")

    def turn_callback(self, direction, key=None):

        if key == 'A':
            for srv in settings.ufw_services_allow:
                os.system("sudo ufw deny %s" % (srv))
        elif key == 'B':
            for srv in settings.ufw_services_allow:
                os.system("sudo ufw allow %s" % (srv))

    def activate(self):
        self._active = True
        self.loop.create_task(self._get_firewallstatus())

    def deactivate(self):
        self._active = False




    async def _get_firewallstatus(self):
        while self.loop.is_running() and self._active:
            try:
                subprocess_result = subprocess.Popen("sudo ufw status numbered | grep '\[' | cut -d ']' -f 2",shell=True,stdout=subprocess.PIPE)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                self._ufw_status = subprocess_output[0].decode('utf-8')
                self._ufw_status = re.sub(' +',' ', self._ufw_status)
                self._ufw_status = self._ufw_status.replace("ALLOW IN"," allow")
                self._ufw_status = self._ufw_status.replace("DENY IN"," deny")

                self._ufw_status = self._ufw_status.replace("Anywhere","")



            except:
                self._ufw_status = "n/a"

            await asyncio.sleep(3)

