""" Playlist menu """
from ui.menubase import MenuBase
import settings
import os 
import integrations.functions as functions

class Foldermenu(MenuBase):
    position = 0
    folders = []
    currentfolder = ""
    
    def playfolder(self,folder):
        foldername = folder[len(settings.AUDIO_BASEPATH):]
        os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (foldername))
        self.windowmanager.set_window("idle")

    def on_key_left(self):
        self.currentfolder = functions.get_parent_folder(self.currentfolder)
        if len(self.currentfolder) < len(settings.AUDIO_BASEPATH):
            self.currentfolder = settings.AUDIO_BASEPATH
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
        if settings.currentfolder != "":
            self.currentfolder = settings.currentfolder
        else:
            self.currentfolder = settings.AUDIO_BASEPATH
        self.folders = []
        self.generate_folders()

    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            self.position = self.counter + self.page

            folder = self.folders[self.position-1]
            fullpath = os.path.join(self.currentfolder,folder)
            self.currentfolder = fullpath
            
            if lp:
                settings.currentfolder = self.currentfolder
                self.windowmanager.set_window("folderinfo")
            else:
                if (functions.has_subfolders(fullpath)):
                    self.generate_folders()
                    self.page = 0
                    self.counter = 1
                else:
                    settings.currentfolder=fullpath
                    self.playfolder(fullpath)
                self.counter = 0
                self.page = 0

            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")
        self.lastcounter = self.counter
