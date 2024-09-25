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

logger = setup_logger(__name__)


# SSL-Zertifikatswarnungen deaktivieren, nur für HTTPS-URLs
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class DownloadMenu(ListBase):
    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop, "Download")
        self.direct_play_last_folder = False

        self.timeout = False
        self.contrasthandle = False

        self.info_key_left = False

        self.downloading = False
        self.totalsize = 0
        self.lastplayedfile = ""

    def activate(self):

        self.init_finished = False
        self.canceled = False
        self.progress = {}
        self.items = []
        self.selector = False
        self.download = False
        self.website = cfg_online.ONLINE_URL
        self.url = self.website
        self.baseurl, self.basecwd = split_url(self.website)
        self.clearmenu()
        self.appendsymbol(symbols.SYMBOL_CLOUD)
        self.change_type_info()

        try:
            self.appendcomment("Suche letzten Onlinetitel...")
            with open(cfg_file_folder.FILE_LAST_ONLINE,"r") as f:
                self.url = f.read()
            self.appendheading(self.url)

            files,directories, temp = self.get_files_and_dirs_from_listing(self.website, ["mp3"],False)

            if files != []:
                logger.info(f"letztes online: {self.url}")
                self.url = get_parent_directory_of_url(self.url)

            if not self.url.startswith(self.website): 
                self.appendcomment(f"Basis-Website geändert, setze auf Standard")
                self.addheading(self.website)
                logger.warning(f"{self.website} nicht in {self.url}")
                self.url = self.website

        except Exception as error:
            logger.error(f"activate: {error}")
            self.appendcomment(f"Fehler: {error}")
            time.sleep(3)
            self.position = -1

        self.loop.run_in_executor(None,self.execute_init)

    def deactivate(self):
        logger.info("deactivate")
        self.canceled = True

    def push_callback(self,lp=False):
        if self.counter in [ -1, -2]:
            self.windowmanager.set_window(self.window_on_back)
        else:
            if not self.is_comment() and not self.is_heading():

                self.loop.run_in_executor(None,self.push_handler)



    def turn_callback(self, direction, key=None):
        super().turn_callback(direction,key)

        #Download abbrechen, falls aktiv
        if self.downloading: self.canceled = True

    def execute_init(self):
        # Verbinungsversuch mit zuletzt abgespieltem Titel, ob vorhanden
        try:
            r = check_url_reachability(self.url)

            if r != 200:
                logger.error(f"execute_init: Verbindungsfehler letzter Onlinetitel {r}: {self.url}")
                self.appendcomment(f"Verbindungsfehler {r}:")
                self.appendheading(self.url)

                if r > 200:
                    self.appendcomment("Setze auf Standard:")
                    self.appendheading(self.website)
                    self.url = self.website
                    if not self.check_website_return(self.url):
                        self.appenditem(f"Gebe auf! Taste! drücken")
                        return
                else:
                    return

            else: #r == 200:
                logger.info(f"execute_init: erfolg {r}: {self.url}")

        except Exception as error:
            logger.error(f"execute_init: exception: Verbindungsfehler {error}")
            self.appendcomment(f"Verbindungsfehler {error}:")
            self.appendheading(self.url)

            self.url = self.website

            # Verbindungsversuch mit Website
            if not self.check_website_return(self.url):
                self.appenditem(f"Gebe auf! Taste drücken!")
                return

        temp, self.cwd = split_url(self.url)

        self.appendcomment(f"Erfolgreich:")
        self.appendheading(self.url)

        time.sleep(3)
        self.init_finished = True

        self.change_type_info(False)

        if self.direct_play_last_folder:
            self.direct_play_last_folder = False
            self.url = construct_url(self.cwd,self.baseurl)
            self.items, directories, self.totalsize = self.get_files_and_dirs_from_listing(self.url)
            if not folders:
                self.playfolder()
        else:
            self.on_key_left()

    def check_website_return(self,url):
        try:
            self.appendcomment("Prüfe URL:")
            self.appendheading(url)
            r1 = check_url_reachability(url)
            if r1 != 200:
                raise Exception(f"Keine Verbindung! Fehler {r1})")
            else:
                return True
        except Exception as error:
            logger.info(f"check_website_return: exception: {error}")
            self.appendcomment(f"Fehler: {error}")
            return False


    def downloadfolder(self):
        try:
            logger.debug(f"start downloadfolder")
            self.downloading = True
            self.handle_key_back = False
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

                self.busyrendertime = 1
                self.busytext1="Download %2.2d von %2.2d" % (self.items.index(item) + 1,len(self.items)) 
                self.busytext2=item
                self.busytext3="Abbruch mit beliebiger Taste" 
                self.busysymbol = "\uf0ed"
                self.render_progressbar = True
                try:
                    self.download_file(url,destination)
                except Exception as error:
                    logger.error(f"downloadfolder: {error}")


        except Exception as error:
            logger.error(f"downloadfolder: {error}")
            self.set_busy(error)
        finally:
            time.sleep(3)
            self.downloading = False
            self.canceled = False
            self.handle_key_back = True
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


    def push_handler(self,button = '*'):
        time.sleep(0.3)

        try:
            self.change_type_info()

            if not self.init_finished:
                self.windowmanager.set_window(self.window_on_back)
                return

            if self.selector:
                if self.downloading:
                    self.canceled = True
                    return
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
                if self.downloading:
                    self.canceled = True
                    return

                if not self.cwd.endswith('/'): self.cwd += '/'

                selected_item = get_first_or_self(self.menu[self.position])
                self.clearmenu()
                self.appendcomment("Verarbeite...")
                self.appendheading(selected_item)

                logger.debug(f"push_handler {selected_item}")

                self.cwd += stripitem(selected_item)

                if not self.cwd.endswith('/'): self.cwd += '/'

                self.url = construct_url_from_local_path(self.baseurl,self.cwd)

                logger.info(f"Wechsle zu {self.url}")
                self.appendcomment("Neue URL:")
                self.appendheading(self.url)

                self.items,directories,self.totalsize = self.get_files_and_dirs_from_listing(self.url, ["mp3"])

                time.sleep(0.5)

                if directories != []:
                    logger.debug(f"Verzeichnisse gefunden: {directories}")
                    self.change_type_info(False)
                    self.create_menu_from_directories(directories)
                else:
                    logger.debug(f"Verzeichnis ausgewählt: {self.cwd}")
                    self.appendcomment("Deteien gefunden")

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
                    #if online_file in self.items:
                    #    self.menu.append(["Aktueller Titel :%2.2d " %  (self.items.index(online_file) + 1)])
                    self.menu.append(["Anzahl Titel :%2.2d " %  (len(self.items))])
                    self.menu.append(["Gesamtgröße %s" % (get_size(self.totalsize))])
                    #self.menu.append([current_pos])
                    #self.menu.append([f"Datei: {online_file}"])
                    #self.menu.append([online_pos])

                time.sleep(0.5)


        except Exception as error:
            logger.error(f"push_handler: exception: {error}")
            self.set_busy(error)
        finally:
            self.change_type_info(False)
            time.sleep(0.5)
            self.position = -1

    def on_key_left(self):
        try:
            self.change_type_info()
            self.clearmenu()
            self.appendcomment("Lese Verzeichnis")

            self.selector = False
            logger.debug(f"derzeitiges Verzeichnis: {self.cwd}")
            last = get_current_directory(self.cwd)

            self.cwd = get_parent_directory(self.cwd)
            self.appendheading(self.cwd)

            logger.debug(f"neues Verzeichnis: {self.cwd}")

            if len(self.cwd) <= len(self.basecwd):
                self.cwd = self.basecwd
                last = "_-__"

            self.url = construct_url(self.cwd,self.baseurl)

            self.appendcomment("Prüfe URL")
            self.appendheading(self.url)

            files, directories,self.totalsize = self.get_files_and_dirs_from_listing(self.url, ["mp3"])

            time.sleep(1)

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
                time.sleep(1)
                self.change_type_info(False)

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
                if self.canceled: break


    def create_menu_from_directories(self,directories):
        for i in range(len(directories)): 
            url = construct_url(directories[i],self.url)
            logger.debug(f"prüfe {directories[i]} {self.url}: {url}")

            if uri_exists_locally(url,self.website,cfg_file_folder.AUDIO_BASEPATH_BASE):
                directories[i] = f"{directories[i]} \u2302"
        self.menu = directories_to_list(directories)
        #TODO progress

    def get_files_and_dirs_from_listing(self,url, allowed_extensions,get_filesize=True):
        """Extrahiere Dateien und Verzeichnisse aus dem HTTP-Listing."""
        try:
            logger.debug(f"Verzeichnis-URL: {url}")
            if not url.endswith('/'): url += '/'
            parsed_url = urlparse(url)

            # Zertifikatsprüfung nur bei HTTPS-URLs deaktivieren
            if parsed_url.scheme == 'https':
                response = requests.get(url, verify=False)
            else:
                response = requests.get(url)  # Keine Zertifikatsprüfung für HTTP

            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Fehler bei der HTTP-Anfrage abfangen
            logger.info(f"Error fetching {url}: {e}")
            return [], [], 0

        soup = BeautifulSoup(response.text, 'html.parser')

        files = []
        directories = []
        total_size = 0

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not href.startswith('?') and not href.startswith('/'):
                if href.endswith('/'):
                    # Unterverzeichnis gefunden
                    directory = unquote(href).strip('/')
                    self.appendcomment(f"Ordner: {directory}")
                    directories.append(unquote(href).strip('/')) # trailing slash entfernen
                elif any(href.endswith(ext) for ext in allowed_extensions):
                    # Datei gefunden
                    filename = unquote(href)
                    self.appendcomment(f"Datei: {filename}")
                    files.append(unquote(href))

                    #Wenn Dateigröße abgefragt werden soll
                    if get_filesize:
                        file_url = urljoin(url, href)
                        try:
                            file_response = requests.head(file_url)
                            file_response.raise_for_status()
                            # Dateigröße aus dem Header holen, falls vorhanden
                            file_size = int(file_response.headers.get('content-length', 0))
                            self.appendheading(f"Dateigröße: {file_size}")
                            total_size += file_size
                        except requests.RequestException as e:
                            logger.info(f"Fehler beim Abrufen der Dateigröße für {file_url}: {e}")
                            continue
        return files, directories, total_size



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

