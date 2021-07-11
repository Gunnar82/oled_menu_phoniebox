""" Playlist menu """
from ui.menubase import MenuBase
import settings
import os 

class Foldermenu(MenuBase):
    position = 0
    folders = []
    basepath = "/home/pi/RPi-Jukebox-RFID/shared/audiofolders"
    currentfolder = ""
    
    def playfolder(self,folder):
        foldername = folder[len(self.basepath):]
        os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (foldername))
        self.windowmanager.set_window("idle")

    def get_parent_folder(self,folder):
        return os.path.dirname(folder)

    def has_subfolders(self, path):
        for file in os.listdir(path):
            d = os.path.join(path, file)
            if os.path.isdir(d):
                return True
        return False

    def on_key_left(self):
        self.currentfolder = self.get_parent_folder(self.currentfolder)
        if len(self.currentfolder) < len(self.basepath):
            self.currentfolder = self.basepath
        self.generate_folders()


    def on_key_right(self):
        self.push_callback()


    def generate_folders_array(self,path):
        self.folders = []
        for file in os.listdir(path):
            d = os.path.join(path, file)
            if os.path.isdir(d) and (str(file) != settings.RADIO_PLAYLIST):
                self.folders.append(file)
        self.folders.sort()

    def __init__(self, windowmanager):
        super().__init__(windowmanager, "Auswahl")

    def generate_folders(self):
        self.generate_folders_array(self.currentfolder)
        self.menu = []
        self.menu = self.folders

    def activate(self):
        self.counter = 0
        self.page = 0
        self.currentfolder = self.basepath
        self.folders = []
        self.generate_folders()

    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            self.position = self.counter + self.page

            folder = self.folders[self.position-1]
            fullpath = os.path.join(self.currentfolder,folder)
            if (self.has_subfolders(fullpath)):
                self.currentfolder = fullpath
                self.generate_folders()
                self.page = 0
                self.counter = 1
            else:
                settings.currentfolder=fullpath
                self.windowmanager.set_window("folderinfo")
                #self.playfolder(fullpath)
            self.counter = 0
            self.page = 0

            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")
        self.lastcounter = self.counter
