""" Playlist menu """
from ui.listbase import ListBase
import settings
import os 
import integrations.functions as functions
import integrations.playout as playout

from integrations.logging import *

class Foldermenu(ListBase):
    folders = []

    def playfolder(self,folder):
        foldername = folder[len(settings.AUDIO_BASEPATH_BASE):]
        print (folder)
        playout.pc_playfolder(foldername)
        self.windowmanager.set_window("playlistmenu")

    def on_key_left(self):
        self.counter = 2
        log(lDEBUG,"settings.currentfolder:%s " %(settings.currentfolder))
        settings.current_selectedfolder = settings.currentfolder
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)
        if len(settings.currentfolder) < len(settings.audio_basepath):
            settings.currentfolder = settings.audio_basepath
        self.generate_folders(settings.currentfolder)
        self.basetitle = os.path.split(settings.currentfolder)[-1]
        log(lDEBUG,"self.basetitle: %s" % (self.basetitle))


    def on_key_right(self):
        self.push_callback()


    def generate_folders_array(self,path):
        self.folders = []
        self.progress = {}

        for file in os.listdir(path):
            d = os.path.join(path, file)
            if os.path.isdir(d):
                try:
                    settings = {}
                    settings["SONG"]="0"
                    settings["PLAYLISTLENGTH"]="0"
                    settings["RESUME"] = "off"

                    fn = os.path.join(d,"folder.conf")
                    log(lDEBUG,"playlistfolder: %s" % (fn))
                    folder_conf = open(fn,"r")
                    lines = folder_conf.readlines()
                    folder_conf.close()

                    for line in lines:
                        _key, _val = line.split('=',2)
                        settings[_key] = _val.replace("\"","").strip()

                    if (settings["SONG"] != "0") and (settings["PLAYLISTLENGTH"] != "0") and ((settings["RESUME"]).lower() == "on"):
                        prozent = float(int(settings["SONG"]) / int(settings["PLAYLISTLENGTH"]))
                        log(lDEBUG2,"foldermenu: progress: %d von %d ist %.2f" % (int(settings["SONG"]), int(settings["PLAYLISTLENGTH"]),prozent))
                        self.progress[file] = prozent * 100
                except:
                    log(lDEBUG2,"No folder.conf for %s" % (d))

                self.folders.append(file)

        self.folders.sort()


    def __init__(self, windowmanager):
        super().__init__(windowmanager, "Auswahl")
        #self.timeoutwindow="folderinfo"
        self.timeout = False

    def generate_folders(self,folder):

        self.generate_folders_array(folder)
        self.menu = []
        self.menu = self.folders

        if settings.current_selectedfolder.rfind(settings.currentfolder) == 0:
            search = settings.current_selectedfolder[len(settings.currentfolder)+1:]
            log(lDEBUG,"search: %s" % (search))
            try:
                _pos = self.folders.index(search)
    
                log(lDEBUG,"foldermenu: generate_folders: position: %d, _pos: %d, self.displaylines: %d" % ( self.position, _pos, self.displaylines))

                if _pos > self.displaylines - 1:                      # Anzahl menu > displaylines
                    log(lDEBUG,"_pos > displaylines -1")
                    self.counter = self.displaylines + 1
                    self.page = _pos - self.displaylines + 1

                else:                                                 # Anzahl menu <= displaylines
                    self.counter = _pos + 2
                    self.page = 0
                    self.position= _pos + 1
            except:
                self.counter = 1
                self.page = 0

    def activate(self):
        self.page = 0
        self.folders = []

        self.generate_folders(settings.currentfolder)
        self.on_key_left()

    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)
        self.basetitle = os.path.split(settings.currentfolder)[-1]

        if (self.counter > 1):
            self.timeout = True
        else:
            self.timeout = False

        if key == '9':
            self.windowmanager.set_window("folderinfo")
        else:
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
                    self.counter = 1
                else:
                    print ("play %s " % (settings.current_selectedfolder))
                    self.playfolder(settings.current_selectedfolder)


            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")
        self.lastcounter = self.counter
