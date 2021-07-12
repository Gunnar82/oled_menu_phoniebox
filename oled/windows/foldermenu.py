""" Playlist menu """
from ui.menubase import MenuBase
import settings
import os 
import integrations.functions as functions

class Foldermenu(MenuBase):
    position = 0
    folders = []
    

    
    def playfolder(self,folder):
        foldername = folder[len(settings.AUDIO_BASEPATH):]
        os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\"" % (foldername))
        self.windowmanager.set_window("idle")

    def on_key_left(self):
        self.counter = 2
        settings.current_selectedfolder = settings.currentfolder
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)
        if len(settings.currentfolder) < len(settings.AUDIO_BASEPATH):
            settings.currentfolder = settings.AUDIO_BASEPATH
        self.generate_folders(settings.currentfolder)


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
        self.timeoutwindow="folderinfo"
        
    def generate_folders(self,folder):
        self.generate_folders_array(folder)
        self.menu = []
        self.menu = self.folders
        if settings.current_selectedfolder.rfind(settings.currentfolder) == 0:
            search = settings.current_selectedfolder[len(settings.currentfolder)+1:]
            try:
                _pos = self.folders.index(search)
                if _pos > 3:
                    self.counter = 5
                    self.page = _pos -3
                else:
                    self.counter = _pos + 2
                    self.page = 0
            except:
                self.counter = 1
                self.page = 0

    def activate(self):
        self.folders = []
        self.generate_folders(settings.currentfolder)

    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)
        self.position = self.counter + self.page
        try:
            folder = self.folders[self.position-2]
            fullpath = os.path.join(settings.currentfolder,folder)
            settings.current_selectedfolder = fullpath
        except:
            settings.current_selectedfolder = settings.currentfolder

    def push_callback(self,lp=False):
        if self.counter == 0:
            settings.currentfolder = settings.AUDIO_BASEPATH
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1:
            self.on_key_left()
        else:
            #folder = self.folders[self.position-1]
            #fullpath = os.path.join(settings.currentfolder,folder)
            #settings.currentfolder = fullpath
            
            if lp:
                self.windowmanager.set_window("folderinfo")
            else:
                if (functions.has_subfolders(settings.current_selectedfolder)):
                    self.generate_folders(settings.current_selectedfolder)
                    settings.currentfolder = settings.current_selectedfolder
                    self.page = 0
                    self.counter = 2
                else:
                    print ("play %s " % (settings.current_selectedfolder))
                    self.playfolder(settings.current_selectedfolder)
                    

            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")
        self.lastcounter = self.counter
