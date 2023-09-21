""" Playlist menu """
import settings

import time
import xml.etree.ElementTree as ET

from ui.listbase import ListBase

class DownloadMenu(ListBase):
    def __init__(self, windowmanager):
        super().__init__(windowmanager, "Download")


    def activate(self):
        self.window_on_back = "idle"
        self.menu = []
        try:
            tree = ET.parse('/home/pi/test.xml')
            self.root = tree.getroot()
            downloads = self.root.findall('Download')
            for download in downloads:
                self.menu.append(download.get('name'))
        except:
            pass
        self.position = -1


    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)

        if self.position >= 0:
            self.title = "%2.2d / %2.2d" %(self.position + 1,len(self.menu))
        else:
            self.title = "Playlist"

    def push_callback(self,lp=False):
        if self.position == -1 or  self.position == -2 :
            self.windowmanager.set_window("mainmenu")
        else:
            try:
                download = self.root.find(".//*[@name='%s']" %(self.menu[self.position]))
                url = download.find('url').text
                files = download.find('files')
                for myfile in files:
                    print (myfile.text)
            except:
                pass


