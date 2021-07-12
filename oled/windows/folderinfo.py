""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import socket
import subprocess
import os
import integrations.functions as functions
import re
from datetime import datetime

class FolderInfo(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
    

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.counter = 0
        self.settings = {}
        self.settings["RESUME"] = "n/a"
        self.settings["CURRENTFILENAME="] = "not/available"
        self.settings["ELAPSED"]="n/a"
        self.settings["SHUFFLE"]="n/a"
        self.settings["LOOP"]="n/a"
        self.settings["SINGLE"]="n/a"
        self.settings["SONG"]="0"
        self.settings["PLAYLISTLENGTH"]="0"
        self.line1 = "n/a"
        self.line2 = "n/a"
        self.line3 = "n/a"
        self.line4 = "n/a"
        self.fn = ""

    def read_folderconf(self,_fn):
        try:
            folder_conf = open(_fn,"r")
            self.lines = folder_conf.readlines()
            folder_conf.close()
            return True
        except:
            return False

    def activate(self):
        self.fn = os.path.join(settings.currentfolder,"folder.conf")
        if self.read_folderconf(self.fn):
            for line in self.lines:
                _key, _val = line.split('=',2)
                self.settings[_key] = _val.replace("\"","").strip()


    def render(self):
        with canvas(self.device) as draw:
            try:
                self.line1 = self.settings["CURRENTFILENAME"][self.settings["CURRENTFILENAME"].rfind("/")+1:]
            except:
                pass

            try:
                self.line2 = "Pos: %d / %s %s" % (int(self.settings["SONG"])+1,self.settings["PLAYLISTLENGTH"],datetime.strptime(self.settings["ELAPSED"],"%S.%f").strftime("%H:%M:%S"))
            except:
                pass

            try:
                ctime = os.path.getmtime(self.fn)
                cstime = datetime.fromtimestamp(ctime)
                self.line3 = cstime.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

            try:
                list_of_files = os.listdir(settings.currentfolder)
                self.line4 = "Anzahl MP3: %d" % (len([x for x in list_of_files if x.endswith(".mp3")]))
            except:
                pass

            draw.text((1, 1), text=self.line1, font=FolderInfo.font, fill="white")
            draw.text((1, 16), text=self.line2, font=FolderInfo.font, fill="white")
            draw.text((1, 31), text=self.line3, font=FolderInfo.font, fill="white")
            draw.text((1, 46), text=self.line4, font=FolderInfo.font, fill="white")
            #draw.text((1, 16), text="WiFi: " + self.wifi_ssid, font=FolderInfo.font, fill="white")
            #draw.text((1, 31), text="hostapdi: " + str(self.hostapd), font=FolderInfo.font, fill="white")
            #draw.text((1, 46), text=self.temp, font=FolderInfo.font, fill="white")


    def push_callback(self,lp=False):
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)
        self.windowmanager.set_window("foldermenu")


    def turn_callback(self, direction, key=None):
        if self.counter + direction <= 0 and self.counter + direction >= 0:
            self.counter += direction
