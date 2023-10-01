""" Playlist menu """
from ui.listbase import ListBase
import settings
import os 
import integrations.functions as functions
import integrations.playout as playout
import asyncio

from integrations.logging import *

class Foldermenu(ListBase):
    folders = []

    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, "Auswahl")
        #self.timeoutwindow="folderinfo"
        self.timeout = False
        self.loop = loop


    def activate(self):
        self.folders = []
        if not os.path.exists(settings.currentfolder):
            settings.currentfolder = settings.audio_basepath
            self.position = -1

        self.generate_folders(settings.currentfolder)
        self.on_key_left()

    async def playfolder(self,folder):
        foldername = folder[len(settings.AUDIO_BASEPATH_BASE):]
        await asyncio.sleep(1)
        playout.pc_playfolder(foldername)
        self.windowmanager.set_window("idle")

    def on_key_left(self):
        log(lDEBUG,"settings.currentfolder:%s " %(settings.currentfolder))
        settings.current_selectedfolder = settings.currentfolder
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)
        if len(settings.currentfolder) < len(settings.audio_basepath):
            settings.currentfolder = settings.audio_basepath
        self.generate_folders(settings.currentfolder)
        self.basetitle = os.path.split(settings.currentfolder)[-1]
        log(lDEBUG,"self.basetitle: %s" % (self.basetitle))


    def generate_folders_array(self,path):
        self.folders = []
        self.progress = {}

        for file in os.listdir(path):
            d = os.path.join(path, file)
            if os.path.isdir(d):
                try:
                    folderconf = {}
                    folderconf["RESUME"] = "off"
                    folderconf["CURRENTFILENAME"] = ""

                    fn = os.path.join(d,"folder.conf")
                    log(lDEBUG,"playlistfolder: %s" % (fn))
                    folder_conf_file = open(fn,"r")
                    lines = folder_conf_file.readlines()
                    folder_conf_file.close()

                    for line in lines:
                        _key, _val = line.split('=',2)
                        folderconf[_key] = _val.replace("\"","").strip()

                    if (folderconf["CURRENTFILENAME"] != "") and ((folderconf["RESUME"]).lower() == "on"):
                        subfiles =[]
                        for subfile in os.listdir(d):
                            subfiles.append(subfile) # nur mp3
                        subfiles = sorted(subfiles)
                        lastplayedfile = folderconf["CURRENTFILENAME"]
                        lastplayedfile = lastplayedfile[lastplayedfile.rfind('/')+1:]
                        mpos = (subfiles.index(lastplayedfile))
                        prozent = (mpos +1)  / len(subfiles)
                        #print ("prozent: %s, lastplayedfile: %s, mpos: %s" %(prozent, lastplayedfile, mpos))

                        log(lDEBUG2,"foldermenu: ptogress%.2f" % (prozent))
                        self.progress[file] = "%2.2d %%" % (prozent * 100)
                except Exception as error:
                    log(lDEBUG2,error)

                try:
                    if (functions.has_subfolders(os.path.join(path,file))):
                        file = settings.SYMBOL_FOLDER +" " + file
                except Exception as error:
                    log(lDEBUG2,error)
                self.folders.append(file)

        self.folders.sort()


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

                self.position= _pos
            except:
                try:
                    _pos = self.folders.index(settings.SYMBOL_FOLDER + " " + search)
    
                    log(lDEBUG,"foldermenu: generate_folders: position: %d, _pos: %d, self.displaylines: %d" % ( self.position, _pos, self.displaylines))

                    self.position= _pos
                except:
                    self.position = 0


    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)
        self.basetitle = os.path.split(settings.currentfolder)[-1]

        if (self.position > 0):
            self.timeout = True
        else:
            self.timeout = False

        if key == '9':
            self.windowmanager.set_window("folderinfo")
        else:
            try:
                folder = functions.remove_folder_symbol(self.folders[self.position])

                fullpath = os.path.join(settings.currentfolder,folder)
                settings.current_selectedfolder = fullpath

            except:
                settings.current_selectedfolder = settings.currentfolder

    def push_callback(self,lp=False):
        if self.position  == -2:
            settings.currentfolder = settings.audio_basepath
            self.windowmanager.set_window("mainmenu")
        elif self.position == -1:
            self.on_key_left()
        else:
            #folder = self.folders[self.position-1]
            #fullpath = os.path.join(settings.currentfolder,folder)
            #settings.currentfolder = fullpath

            if lp:
                self.windowmanager.set_window("folderinfo")
            else:
                thefile = os.listdir(settings.current_selectedfolder)
                print (settings.current_selectedfolder)
                if (functions.has_subfolders(settings.current_selectedfolder)):
                    self.generate_folders(settings.current_selectedfolder)
                    settings.currentfolder = settings.current_selectedfolder
                    self.position = 0
                elif not os.listdir(settings.current_selectedfolder) == 1 and thefile[0] == "folder.conf":
                    self.set_busy("Verzeichnis ist leer",busysymbol="\uf059")
                else:
                    self.set_busy("Auswahl startet","\uf07C",self.menu[self.position])
                    self.loop.create_task(self.playfolder(settings.current_selectedfolder))


            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")

