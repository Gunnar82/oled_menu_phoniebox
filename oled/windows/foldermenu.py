""" Playlist menu """
from ui.menubase import MenuBase
import settings
import os 
import integrations.functions as functions
import integrations.playout as playout
class Foldermenu(MenuBase):
    folders = []
    

    
    def playfolder(self,folder):
        foldername = folder[len(settings.AUDIO_BASEPATH_BASE):]
        playout.pc_playfolder(foldername)
        self.windowmanager.set_window("playlistmenu")

    def on_key_left(self):
        self.counter = 2
        settings.current_selectedfolder = settings.currentfolder
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)
        if len(settings.currentfolder) < len(settings.audio_basepath):
            settings.currentfolder = settings.audio_basepath
        self.generate_folders(settings.currentfolder)


    def on_key_right(self):
        self.push_callback()


    def generate_folders_array(self,path):
        self.folders = []
        for file in os.listdir(path):
            d = os.path.join(path, file)
            if os.path.isdir(d):
                self.folders.append(file)
        self.folders.sort()

    def __init__(self, windowmanager):
        super().__init__(windowmanager, "Auswahl")
        self.timeoutwindow="folderinfo"
        #self.timeout = False
        
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
        if (self.counter > 1):
            self.timeout = True
        else:
            self.timeout = False
 
        try:
            folder = self.folders[self.position]
            fullpath = os.path.join(settings.currentfolder,folder)
            settings.current_selectedfolder = fullpath
        except:
            settings.current_selectedfolder = settings.currentfolder

    def push_callback(self,lp=False):
        if self.counter == 0:
            settings.currentfolder = settings.audio_basepath
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
