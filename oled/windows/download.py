""" Playlist menu """	
import settings

import config.colors as colors
import config.symbols as symbols

import time
import requests

import os
import asyncio
import shutil

from luma.core.render import canvas

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote


from ui.listbase import ListBase
import time
import integrations.playout as playout
from integrations.functions import get_size

import config.online as cfg_online
import config.file_folder as cfg_file_folder


from integrations.download import *

from integrations.logging_config import *

logger = setup_logger(__name__,lvlDEBUG)


# SSL-Zertifikatswarnungen deaktivieren, nur für HTTPS-URLs
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class DownloadMenu(ListBase):
    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop, "Download")
        self.direct_play_last_folder = False

        self.timeout = False
        self.contrasthandle = False

        self.downloading = False
        self.totalsize = 0
        self.lastplayedfile = ""

    def activate(self):
        self.canceled = False
        self.progress = {}
        self.items = []
        self.selector = False
        self.download = False
        self.website = cfg_online.ONLINE_URL
        self.url = self.website
        self.baseurl, self.basecwd = split_url(self.website)

        try:
            with open(cfg_file_folder.FILE_LAST_ONLINE,"r") as f:
                self.url = f.read()

                files,directories, temp = get_files_and_dirs_from_listing(self.website, ["mp3"],False)

                if files != []:
                    logger.info(f"letztes online {self.url}")
                    self.url = get_parent_directory_of_url(self.url)


            if not self.url.startswith(self.website): #Basis-Website geändert
                logger.warning(f"{self.website} nicht in {self.url}")
                self.url = self.website


        except Exception as error:
            logger.error(f"activate: {error}")
            self.set_busy("Dateifehler",symbols.SYMBOL_NOCLOUD,str(error))
            time.sleep(3)
            self.position = -1

        self.set_busy("Verbinde Online",symbols.SYMBOL_CLOUD,self.website,busyrendertime=60)
        self.renderbusy()
        self.loop.run_in_executor(None,self.execute_init)

    def deactivate(self):
        logger.info("deactivate")
        self.canceled = True


    def execute_init(self):

        try:
            r = check_url_reachability(self.url)

            if r == 0:
                logger.error(f"Verbindungsfehler {r}")
                self.set_busy("Verbindungsfehler",symbols.SYMBOL_NOCLOUD,self.url,set_window_to="mainmenu")
                return
            elif r != 200:
                logger.info(f"Verbindungsfehler {r}: {self.url}")
                self.url = self.website
            elif r == 200:
                logger.info(f"erfolg {r}: {self.url}")
        except Exception as error:
            logger.error(f"Verbindungsfehler {error}")

            self.url = self.website

        temp, self.cwd = split_url(self.url)

        self.set_busy("Verbinde Online",symbols.SYMBOL_CLOUD,self.url,busyrendertime=0)

        if self.direct_play_last_folder:
            self.direct_play_last_folder = False
            self.url = construct_url(self.cwd,self.baseurl)
            self.items, directories, self.totalsize = get_files_and_dirs_from_listing(self.url)
            if not folders:
                self.playfolder()
        else:
            self.on_key_left()


    def downloadfolder(self):
        try:
            logger.debug(f"start downloadfolder")
            self.downloading = True
            self.totaldownloaded = 0
            settings.callback_active = True
            uri = get_relative_path(self.basecwd,get_unquoted_uri(self.url))
            logger.debug(f"downloadfolder: uri: {uri}")
            destdir = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,uri)
            logger.debug(f"downloadfolder: destdir: {destdir}")

            try:
                if not os.path.exists(destdir): os.makedirs(destdir)
            except Exception as error:
                logger.error(f"downloadfolder: error {error}")
            for item in self.items:

                if self.canceled:
                    logger.info("downloadfolder: Abbruch")
                    break;
                url = construct_url_from_local_path(self.baseurl,self.cwd,item)
                logger.debug(f"downloadfolder: url: {url}")

                destination = os.path.join(destdir, stripitem(item))

                logger.debug(f"downloadfolder: destination: {destination}")

                self.download_file(url,destination)
                self.busyrendertime = 1
                self.busytext1="Download %2.2d von %2.2d" %(self.items.index(item) + 1,len(self.items) )
                self.busytext2=item
                self.busytext3="Abbruch mit beliebiger Taste"
                self.busysymbol = "\uf0ed"


        except Exception as error:
            logger.error(f"downloadfolder: {error}")
            self.canceled = True
            self.set_busy(error)
        finally:
            time.sleep(3)
            self.canceled = False
            self.downloading = False
            settings.callback_active = False


    def playfolder(self):


        try:
            directory = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,get_relative_path(self.basecwd,self.cwd))
            logger.info(f"playfolder {directory}")

            create_or_modify_folder_conf(directory,playout.getpos_online(self.baseurl,self.cwd))
        except Exception as error:
            logger.error (error)

        try:
            with open(cfg_file_folder.FILE_LAST_ONLINE,"w") as f:
                f.write(self.url)
        except Exception as error:
            print (error)
        if not os.path.exists(directory): os.makedirs(directory)

        try:
            filename = os.path.join(directory,"livestream.txt")
            with open(filename,"w") as ofile:
                for item in self.items:
                    additem = construct_url_from_local_path(self.baseurl,self.cwd,item) + '\n'
                    print (item)
                    ofile.write(additem)
            foldername = directory[len(cfg_file_folder.AUDIO_BASEPATH_BASE):]
            playout.pc_playfolder(foldername)
            self.windowmanager.set_window("idle")
        except Exception as error:
            print (error)


    async def push_handler(self,button = '*'):
        await asyncio.sleep(1)
        try:
            if self.selector:
                logger.debug(f"Untermenü aktiv: {self.position}")
                if self.position == 0:
                    logger.debug(f"Untermenü aktiv: {self.position}, abspielen")
                    self.playfolder()
                elif self.position == 1:
                    logger.debug(f"Untermenü aktiv: {self.position}, starte download")
                    self.loop.run_in_executor(None, self.downloadfolder)
                elif self.position == 2 and self.selector:
                    self.menu = []
                    for items in self.items: self.menu.append([item])
                elif self.position == -1 and self.selector:
                    self.selector = False
                elif self.position == 3:
                    destdir = cfg_file_folder.AUDIO_BASEPATH_BASE + '/' + self.url[len(cfg_online.ONLINE_URL):]
                    if not os.path.exists(destdir):
                        self.set_busy("lokal nicht gefunden",busysymbol="\uf059")
                    else:
                        try:
                            shutil.rmtree(destdir)
                            self.set_busy(destdir,busytext2="erfolgreich",busysymbol="\uf058")
                        except FileNotFoundError:
                            self.set_busy("nicht gefunden!",busyrendertime=5,busysymbol="\uf057")
                        except PermissionError:
                            self.set_busy("Fehlerhafte Berechrigung",busyrendertime=5,busysymbol="\uf057")
                        except Exception as e:
                            self.set_busy("Fehler!",busytext2=str(e),busyrendertime=5,busysymbol="\uf057")
            else:
                if not self.cwd.endswith('/'): self.cwd += '/'

                selected_item = get_first_or_self(self.menu[self.position])
                logger.debug(f"push_callback {selected_item}")

                self.cwd += stripitem(selected_item)

                if not self.cwd.endswith('/'): self.cwd += '/'

                self.url = construct_url_from_local_path(self.baseurl,self.cwd)

                logger.info(f"Wechsle zu {self.url}")
                self.items,directories,self.totalsize = get_files_and_dirs_from_listing(self.url, ["mp3"])

                if directories != []:
                    logger.debug(f"Verzeichnisse gefunden: {directories}")
                    self.create_menu_from_directories(directories)
                else:
                    logger.debug(f"Verzeichnis ausgewählt: {self.cwd}")
                    self.selector = True
                    try:
                        posstring = playout.getpos_online(self.baseurl,self.cwd)
                        if posstring[0] == "POS":
                            online_file = posstring[1]
                            online_pos = "Zeit:  %s " % (posstring[2])

                        else:
                            online_file = ""
                            online_pos = ""
                    except Exception as error:
                        logger.error(f"getpos_online: {error}")
                        online_file = ""
                        online_pos = ""

                    try:
                        current_pos = "Fortschritt: %s" % (self.progress[self.items[self.position]])
                    except:
                        current_pos = "Fortschritt nicht verfügbar"

                    self.menu = []
                    self.menu.append(["Abspielen"])
                    self.menu.append(["Herunterladen"])
                    self.menu.append(["informationen"])
                    self.menu.append(["Lokal löschen"])
                    self.menu.append([""])
                    if online_file in self.items:
                        self.menu.append(["Aktueller Titel :%2.2d " %  (self.items.index(online_file) + 1)])
                    self.menu.append(["Anzahl Titel :%2.2d " %  (len(self.items))])
                    self.menu.append(["Gesamtgröße %s" % (get_size(self.totalsize))])
                    self.menu.append([current_pos])
                    self.menu.append([f"Datei: {online_file}"])
                    self.menu.append([online_pos])

                    return

        except Exception as error:
            self.set_busy(error)
            time.sleep(3)
        finally:
            self.position = -1

    def push_callback(self,lp=False):
        if self.downloading:
            self.set_busy("Abbruch",busysymbol = "\uf05e")
            self.canceled = True
        elif (self.position == -1 or  self.position == -2) and not self.selector:
            self.windowmanager.set_window("mainmenu")
        else:
            selected_item = get_first_or_self(self.menu[self.position])

            if not self.selector or self.position == 0:
                self.set_busy("Auswahl verarbeiten...",symbols.SYMBOL_CLOUD,selected_item, busyrendertime=2)
            self.loop.create_task(self.push_handler())

    def on_key_left(self):
        self.set_busy("Lese Verzeichnis",busyrendertime=60)

        self.selector = False
        logger.debug(f"derzeitiges Verzeichnis: {self.cwd}")
        last = get_current_directory(self.cwd)

        self.cwd = get_parent_directory(self.cwd)
        logger.debug(f"neues Verzeichnis: {self.cwd}")

        if len(self.cwd) <= len(self.basecwd):
            self.cwd = self.basecwd
            last = "_-__"

        self.url = construct_url(self.cwd,self.baseurl)

        files, directories,self.totalsize = get_files_and_dirs_from_listing(self.url, ["mp3"])

        self.create_menu_from_directories(directories)

        self.position = find_element_or_formatted_position(self.menu,last)[0]

        try:
            if len(self.cwd) > len (self.basecwd):
                self.basetitle = self.cwd[pos+1:]
            else:
                self.basetitle = "Online"
        except Exception as error:
            self.basetitle = self.windowtitle
        finally:
            self.set_busy("",busyrendertime=0)

    def render(self):
        if self.canceled:
            self.busytext3="Abbruch! Bitte warten!"
            self.renderbusy()
        elif self.downloading:
            self.renderbusy()
        else:
            super().render()


    def download_file(self,url, local_path):
        # Den Inhalt der Datei herunterladen und den Fortschritt anzeigen
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Überprüfen, ob die Anfrage erfolgreich war

        # Dateigröße ermitteln
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte


        # Datei speichern
        totaldlfile = 0
        with open(local_path, 'wb') as file:
            for data in response.iter_content(block_size):
                totaldlfile += len(data)
                self.totaldownloaded += len(data)
                #dl_progress = totaldlfile / total_size_in_bytes * 100
                try:
                    self.progessbarpos = self.totaldownloaded / self.totalsize # float zahl
                except:
                    pass

                self.busytext4 = "%s / %s, %s / %s" % ( get_size(totaldlfile), get_size(total_size_in_bytes), get_size(self.totaldownloaded), get_size(self.totalsize))
                file.write(data)


    def create_menu_from_directories(self,directories):
        for i in range(len(directories)): 
            url = construct_url(directories[i],self.url)
            logger.debug(f"prüfe {directories[i]} {self.url}: {url}")

            if uri_exists_locally(url,self.website,cfg_file_folder.AUDIO_BASEPATH_BASE):
                directories[i] = f"{directories[i]} \u2302"
        self.menu = directories_to_list(directories)
        #TODO progress


####old

    def get_content(self):
        folderinfo = playout.getpos_online(self.baseurl,onlinepath)
        if len(folderinfo) >= 6 and folderinfo[0] == "POS":
            song = int(float(folderinfo[3]))
            length = int(float(folderinfo[4]))
            prozent = (song - 1) / length * 100
            progress = "%2.2d%%%s"  % (prozent,progress)
        elif folderinfo[0] == "ERR":
            progress = "%s%s"  % (folderinfo[0],progress)



    def renderbusy(self,symbolcolor = colors.COLOR_RED, textcolor1=colors.COLOR_WHITE, textcolor2=colors.COLOR_WHITE):
        with canvas(self.device) as draw:
            try:
                mypos = int(self.progessbarpos * settings.DISPLAY_WIDTH)
                draw.rectangle((mypos, settings.DISPLAY_HEIGHT - 1, settings.DISPLAY_WIDTH, settings.DISPLAY_HEIGHT - 1),outline="red", fill="red")
                draw.rectangle((0, settings.DISPLAY_HEIGHT - 1, mypos, settings.DISPLAY_HEIGHT - 1),outline=colors.COLOR_SELECTED, fill=colors.COLOR_SELECTED)
            except Exception as error:
                logger.debug(f"{error}")

            self.renderbusydraw(draw,symbolcolor,textcolor1,textcolor2)
