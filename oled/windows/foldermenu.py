""" Playlist menu """
from ui.listbase import ListBase
import settings

import config.colors as colors
import config.symbols as symbols

import os 
import integrations.functions as functions
import time

import config.file_folder as cfg_file_folder

from integrations.logging_config import *

logger = setup_logger(__name__)


class Foldermenu(ListBase):
    folders = []
    busysymbol = symbols.SYMBOL_LIST

    def __init__(self, windowmanager,loop,musicmanager):
        super().__init__(windowmanager, loop, "Auswahl")
        #self.timeoutwindow="folderinfo"
        self.timeout = False
        self.loop = loop
        self.musicmanager = musicmanager


    def activate(self):
        self.folders = []
        settings.currentfolder = self.check_if_subdir_of_basepath(settings.currentfolder,settings.audio_basepath)
        self.position = -1

        if settings.currentfolder.startswith(cfg_file_folder.AUDIO_BASEPATH_MUSIC): self.busysymbol = f"{symbols.SYMBOL_LIST} {symbols.SYMBOL_MUSIC}"
        elif settings.currentfolder.startswith(cfg_file_folder.AUDIO_BASEPATH_HOERBUCH): self.busysymbol = f"{symbols.SYMBOL_LIST} {symbols.SYMBOL_HOERSPIEL}"
        elif settings.currentfolder.startswith(cfg_file_folder.AUDIO_BASEPATH_RADIO): self.busysymbol = f"{symbols.SYMBOL_LIST} {symbols.SYMBOL_RADIO}"
        else: busysymbol = symbols.SYMBOL_LIST

        self.generate_folders(settings.currentfolder)
        self.on_key_left()

    def playfolder(self,fullfolder):
        try:
            self.set_window_busy()
            foldername = fullfolder[len(cfg_file_folder.AUDIO_BASEPATH_BASE) + 1:]
            logger.debug (f"enable_resume: {foldername}")

            self.append_busytext("Abspielen:")
            self.append_busytext(foldername)
            self.musicmanager.playfolderstart(fullfolder,foldername)
            self.windowmanager.set_window("idle")
        except Exception as error:
            logger.debug(f"{error}")
            self.append_busyerror(error)
        finally:
            self.set_window_busy(False)

    def check_if_subdir_of_basepath(self,directory, basepath):
        try:
            thedir = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,directory)
            print (thedir)
            if len(thedir) >= len(basepath) and thedir.startswith(basepath) and os.path.exists(thedir):
                return thedir
            else: 
                return settings.audio_basepath
        except Exception as error:
            logger.error(f"check_if_subdir: {error}")
            return settings.audio_basepath


    def on_key_left(self):
        self.set_window_busy()
        self.append_busytext("Ebene höher...")

        logger.debug(f"settings.currentfolder: {settings.currentfolder}")
        self.append_busytext(f"von {settings.currentfolder}")

        settings.current_selectedfolder = settings.currentfolder
        settings.currentfolder = functions.get_parent_folder(settings.currentfolder)

        settings.currentfolder = self.check_if_subdir_of_basepath(settings.currentfolder,settings.audio_basepath)

        self.append_busytext(f"nach {settings.currentfolder}")

        self.generate_folders(settings.currentfolder)
        self.basetitle = os.path.split(settings.currentfolder)[-1]
        logger.debug("self.basetitle: %s" % (self.basetitle))
        self.set_window_busy(False)

    def generate_folders_array(self,path):
        logger.debug("generate_folders_array: start")
        folders_info = []
        for filename in os.listdir(path):
            d = os.path.join(path, filename)
            if os.path.isdir(d):
                try:
                    progress = ""
                    folder = d[len(cfg_file_folder.AUDIO_BASEPATH_BASE) + 1:]
                    percentage = self.musicmanager.get_folder_info(folder)
                    logger.debug("foldermenu: progress: %.2f" % (percentage))
                    progress = "%2.2d %%" % (percentage)
                except Exception as error:
                    logger.debug(error)

                try:
                    if (functions.has_subfolders(os.path.join(path,filename))):
                        filename = symbols.SYMBOL_FOLDER +" " + filename
                except Exception as error:
                    logger.debug(error)

                new_element = [filename,"x",progress]
                logger.debug(f"append new element: {new_element}")
                folders_info.append(new_element)

        folders_info.sort()
        logger.debug("generate_folders_array: end")
        return folders_info

    def generate_folders(self,folder):
        folders_info = self.generate_folders_array(folder)
        self.menu = []
        for folder in folders_info:
            logger.debug(f"append folder to self.menu: {folder}")
            self.menu.append(folder)

        if settings.current_selectedfolder.rfind(settings.currentfolder) == 0:
            search = settings.current_selectedfolder[len(settings.currentfolder)+1:]
            logger.debug(f"search: {search}")
            try:
                filtered = list(filter(lambda x: x[0] == search, folders_info))
                _pos = folders_info.index(filtered[0]) if filtered else -1
                logger.debug("foldermenu: generate_folders: position: %d, _pos: %d, self.displaylines: %d" % ( self.position, _pos, self.displaylines))

                self.position= _pos
            except Exception as error:
                print (error)
                self.position = -1


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
                selected_item = self.menu[self.position]
                folder = functions.remove_folder_symbol(selected_item[0])

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


            #self.musicmanagerconnection.loadplaylist(self.musicmanagerconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")

