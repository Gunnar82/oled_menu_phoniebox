""" Playlist menu """
from ui.listbase import ListBase
import settings

import config.colors as colors
import config.symbols as symbols

import os 
import integrations.functions as functions
import integrations.playout as playout
import time

import config.file_folder as cfg_file_folder

from integrations.logging_config import *

logger = setup_logger(__name__)


class Foldermenu(ListBase):
    folders = []
    new_busyrender = True

    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop, "Auswahl")
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

    def playfolder(self,folder):
        try:
            self.set_window_busy(with_symbol = False, clear_busymenu = False)
            foldername = folder[len(cfg_file_folder.AUDIO_BASEPATH_BASE) + 1:]

            if folder.startswith(cfg_file_folder.AUDIO_BASEPATH_HOERBUCH):
                playout.pc_enableresume(foldername)
            elif folder.startswith(cfg_file_folder.AUDIO_BASEPATH_MUSIC):
                playout.pc_disableresume(foldername)
            elif folder.startswith(cfg_file_folder.AUDIO_BASEPATH_RADIO):
                playout.pc_disableresume(foldername)
            else:
                self.append_busyerror ("unbeknnt")

            self.append_busytext("Abspielen...")
            self.append_busytext(foldername)
            playout.pc_playfolder(foldername)
            self.windowmanager.set_window("idle")
        except Exception as error:
            self.append_busyerror(error)
        finally:
            self.set_window_busy(False)

    def on_key_left(self):
        self.set_window_busy(with_symbol=False,clear_busymenu=False)
        self.append_busytext("Ebene höher...")

        logger.debug("settings.currentfolder:%s " %(settings.currentfolder))
        self.append_busytext(f"von {settings.currentfolder}")

        settings.current_selectedfolder = settings.currentfolder
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)
        if len(settings.currentfolder) < len(settings.audio_basepath):
            settings.currentfolder = settings.audio_basepath
        self.append_busytext(f"nach {settings.currentfolder}")

        self.generate_folders(settings.currentfolder)
        self.basetitle = os.path.split(settings.currentfolder)[-1]
        logger.debug("self.basetitle: %s" % (self.basetitle))
        self.set_window_busy(False)

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
                    logger.debug("playlistfolder: %s" % (fn))
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

                        logger.debug("foldermenu: ptogress%.2f" % (prozent))
                        self.progress[file] = "%2.2d %%" % (prozent * 100)
                except Exception as error:
                    logger.debug(error)

                try:
                    if (functions.has_subfolders(os.path.join(path,file))):
                        file = symbols.SYMBOL_FOLDER +" " + file
                except Exception as error:
                    logger.debug(error)
                self.folders.append(file)

        self.folders.sort()


    def generate_folders(self,folder):

        self.generate_folders_array(folder)
        self.menu = []
        for folder in self.folders:
            self.menu.append([folder])
        if settings.current_selectedfolder.rfind(settings.currentfolder) == 0:
            search = settings.current_selectedfolder[len(settings.currentfolder)+1:]
            logger.debug("search: %s" % (search))
            try:
                _pos = self.folders.index(search)
    
                logger.debug("foldermenu: generate_folders: position: %d, _pos: %d, self.displaylines: %d" % ( self.position, _pos, self.displaylines))

                self.position= _pos
            except:
                try:
                    _pos = self.folders.index(symbols.SYMBOL_FOLDER + " " + search)
    
                    logger.debug("foldermenu: generate_folders: position: %d, _pos: %d, self.displaylines: %d" % ( self.position, _pos, self.displaylines))

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

    def push_handler(self):
        set_window = True
        try:

            self.set_window_busy()

            if self.position  == -2:
                settings.currentfolder = settings.audio_basepath
                self.windowmanager.set_window("mainmenu")
            elif self.position == -1:
                self.append_busytext("Eine Ebene höher...")
                set_window = False
                self.on_key_left()
            else:
                #folder = self.folders[self.position-1]
                #fullpath = os.path.join(settings.currentfolder,folder)
                #settings.currentfolder = fullpath
                self.append_busytext("Auswahl...")
                thefile = os.listdir(settings.current_selectedfolder)

                if (functions.has_subfolders(settings.current_selectedfolder)):
                    self.append_busytext("Suche Ordner...")
                    self.append_busytext(settings.current_selectedfolder)
                    self.generate_folders(settings.current_selectedfolder)
                    settings.currentfolder = settings.current_selectedfolder
                    self.position = -1
                elif len(thefile) <= 1 and not 'livestream.txt' in thefile:
                    self.append_busyerror("Verzeichnis ist leer")
                    self.append_busyerror(settings.current_selectedfolder)
                else:
                    set_window = False
                    self.append_busytext("Auswahl startet...")
                    self.append_busytext(self.menu[self.position][0])

                    self.loop.run_in_executor(None,self.playfolder,settings.current_selectedfolder)
        except Exception as error:
            self.append_busyerror(error)
        finally:
            if set_window: self.set_window_busy(False,wait=5)


            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")

