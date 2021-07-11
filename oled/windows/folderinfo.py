""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import socket
import subprocess
import os

class FolderInfo(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
    

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.settings = {}
        self.settings["RESUME"] = "n/a"
        self.settings["CURRENTFILENAME="] = "n/a"
        self.settings["ELAPSED"]="n/a"
        self.settings["SHUFFLE"]="n/a"
        self.settings["LOOP"]="n/a"
        self.settings["SINGLE"]="n/a"


    def read_folderconf(self):
        try:
            fn = os.path.join(settings.currentfolder,"folder.conf")
            folder_conf = open(fn,"r")
            self.lines = folder_conf.readlines()
            folder_conf.close()
            return True
        except:
            return False

    def activate(self):
        if self.read_folderconf():
            for line in self.lines:
                _key, _val = line.split('=',2)
                self.settings[_key] = _val.replace("\"","")


    def render(self):
        with canvas(self.device) as draw:

            draw.text((1, 1), text=self.settings["CURRENTFILENAME"][self.settings["CURRENTFILENAME"].rfind("/")+1:], font=FolderInfo.font, fill="white")
            draw.text((1, 16), text="Zeit: %s" % (self.settings["ELAPSED"]), font=FolderInfo.font, fill="white")
            draw.text((1, 31), text="RESUME: %s" % (self.settings["RESUME"]), font=FolderInfo.font, fill="white")
            #draw.text((1, 46), text=self.settings["CURRENTFILENAME"], font=FolderInfo.font, fill="white")
            #draw.text((1, 16), text="WiFi: " + self.wifi_ssid, font=FolderInfo.font, fill="white")
            #draw.text((1, 31), text="hostapdi: " + str(self.hostapd), font=FolderInfo.font, fill="white")
            #draw.text((1, 46), text=self.temp, font=FolderInfo.font, fill="white")


    def push_callback(self,lp=False):
        print (settings.currentfolder)
        foldername = settings.currentfolder[len(settings.AUDIO_BASEPATH):]
        os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (foldername))


    def turn_callback(self, direction, key=None):
        if self.counter + direction <= 0 and self.counter + direction >= 0:
            self.counter += direction
