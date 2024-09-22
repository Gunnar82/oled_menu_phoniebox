""" Playlist menu """	
import settings

import config.colors as colors
import config.symbols as symbols

import time
import requests

import os
import asyncio
import shutil

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote


from ui.listbase import ListBase
import time
import integrations.playout as playout
from integrations.functions import get_size

import config.online as cfg_online
import config.file_folder as cfg_file_folder


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

        try:
            with open(cfg_file_folder.FILE_LAST_ONLINE,"r") as f:
                self.website = f.read()

            if not self.website.startswith(cfg_online.ONLINE_URL): #Basis-Website geändert
                self.website = cfg_online.ONLINE_URL

        except Exception as error:
            self.set_busy("Dateifehler",symbols.SYMBOL_NOCLOUD,str(error))
            time.sleep(3)
            self.position = -1

        self.set_busy("Verbinde Online",symbols.SYMBOL_CLOUD,self.website,busyrendertime=60)
        self.renderbusy()
        self.loop.run_in_executor(None,self.execute_init)

    def deactivate(self):
        self.canceled = True


    def execute_init(self):

        try:
            r = check_url_reachability(self.website)

            if r == 0:
                self.set_busy("Verbindungsfehler",symbols.SYMBOL_NOCLOUD,self.website,set_window_to="idle")
                return
            elif r != 200:
                self.website = cfg_online.ONLINE_URL
        except:
            self.website = cfg_online.ONLINE_URL

        self.baseurl, self.basecwd = self.split_url(self.website)
        self.cwd = self.basecwd

        self.set_busy("Verbinde Online",symbols.SYMBOL_CLOUD,self.website,busyrendertime=0)

        if self.direct_play_last_folder:
            self.direct_play_last_folder = False
            self.url = self.baseurl + self.cwd
            self.items, directories, self.totalsize = self.get_files_and_dirs_from_listing(self.url)
            if not folders:
                self.playfolder()
        else:
            self.on_key_left()


    def downloadfolder(self):
        try:
            self.downloading = True
            self.totaldownloaded = 0
            settings.callback_active = True
            destdir = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,self.url[len(cfg_online.ONLINE_URL):])

            if not os.path.exists(destdir): os.makedirs(destdir)

            for item in self.items:

                if self.canceled: break;
                filecwd = self.cwd + '/' + self.stripitem(item)
                url = self.baseurl + quote(filecwd)
                destination = os.path.join(destdir, self.stripitem(item))
                self.download_file(url,destination)
                self.busyrendertime = 1
                self.busytext1="Download %2.2d von %2.2d" %(self.items.index(item) + 1,len(self.items) )
                self.busytext2=item
                self.busytext3="Abbruch mit beliebiger Taste"
                self.busysymbol = "\uf0ed"


        except Exception as error:
            print (error)
            self.canceled = True
            self.set_busy(error)
        finally:
            time.sleep(3)
            self.canceled = False
            self.downloading = False
            settings.callback_active = False

    def create_or_modify_folder_conf(self,directory,latestplayed):
        filename = os.path.join(directory,"folder.conf")
        folderconf = {}
        folderconf["CURRENTFILENAME"] = ""
        folderconf["ELAPSED"] = "ON"
        folderconf["PLAYSTATUS"] = "Playing"
        folderconf["SHUFFLE"] = "OFF"
        folderconf["RESUME"] = "ON"
        folderconf["LOOP"] = "OFF"
        folderconf["SINGLE"] = "OFF"

        try:
            folder_conf_file = open(filename,"r")
            lines = folder_conf_file.readlines()
            for line in lines:
                _key, _val = line.split('=',2)
                folderconf[_key] = _val.replace("\"","").strip()
        except Exception as error:
            print (error)

        if latestplayed[0] == "POS":
            folderconf["CURRENTFILENAME"] = "%s%s" % (latestplayed[5],latestplayed[1])
            folderconf["ELAPSED"] = latestplayed[2]
        print (filename)
        try:
            with open(filename,"w") as folder_conf_file:

                for key in folderconf:
                    folder_conf_file.write ("%s=\"%s\"\n" % (key,folderconf[key]))
        except Exception as error:
            print (error)


    def playfolder(self):

        directory = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,self.cwd[len(self.basecwd):])

        try:
            self.create_or_modify_folder_conf(directory,playout.getpos_online(self.baseurl,self.cwd))
        except Exception as error:
            print (error)

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
                    additem = urljoin(self.baseurl,quote(self.cwd + self.stripitem(item))) + '\n'
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
                if self.position == 0:
                    self.playfolder()
                elif self.position == 1:
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
                self.cwd += self.stripitem(self.menu[self.position]) + '/'

                self.url = self.baseurl + self.cwd
                files,directories,self.totalsize = self.get_files_and_dirs_from_listing(self.url, ["mp3"])

                if directories != []:
                    self.menu = directories
                else:
                    self.items = files
                    self.selector = True
                    try:
                        posstring = playout.getpos_online(self.baseurl,self.cwd)
                        if posstring[0] == "POS":
                            online_file = posstring[1]
                            online_pos = "Zeit:  %s " % (posstring[2])

                        else:
                            online_file = ""
                            online_pos = ""
                    except:
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
            selected_item = self.menu[self.position]

            if not self.selector or self.position == 0:
                self.set_busy("Auswahl verarbeiten...",symbols.SYMBOL_CLOUD,selected_item[0] if isinstance(selected_item,list) else selected_item, busyrendertime=2)
            self.loop.create_task(self.push_handler())

    def on_key_left(self):
        self.set_busy("Lese Verzeichnis",busyrendertime=60)

        self.selector = False

        self.cwd = os.path.dirname(self.cwd)

        if len(self.cwd) <= len(self.basecwd):
            self.cwd = self.basecwd
            last = "_-__"

        self.url = self.baseurl + self.cwd

        files, directories,self.totalsize = self.get_files_and_dirs_from_listing(self.url, ["mp3"])

        try:
            self.menu = []
            self.menu += directories
            self.position =  self.menu.index(last)
        except Exception as error:
            try:
                self.position = self.menu.index('%s \u2302'% (last))
            except:
                self.position = -1

        try:
            if len(self.cwd) > len (self.basecwd):
                self.basetitle = self.cwd[pos+1:]
            else:
                self.basetitle = "Online"
        except Exception as error:
            self.basetitle = self.windowtitle
        finally:
            self.set_busy("",busyrendertime=0)


    def stripitem(self, rawitem):
        return rawitem.rstrip('\u2302').rstrip()

    def render(self):
        if self.canceled:
            self.busytext3="Abbruch! Bitte warten!"
            self.renderbusy()
        elif self.downloading:
            self.renderbusy()
        else:
            super().render()


    def get_files_and_dirs_from_listing(self,url, allowed_extensions):
        """Extrahiere Dateien und Verzeichnisse aus dem HTTP-Listing."""
        try:
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
            print(f"Error fetching {url}: {e}")
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
                    directories.append(unquote(href).strip('/')) # trailing slash entfernen
                elif any(href.endswith(ext) for ext in allowed_extensions):
                    # Datei gefunden
                    files.append(unquote(href))
                    file_url = urljoin(url, href)
                    try:
                        file_response = requests.head(file_url)
                        file_response.raise_for_status()
                        # Dateigröße aus dem Header holen, falls vorhanden
                        file_size = int(file_response.headers.get('content-length', 0))
                        total_size += file_size
                    except requests.RequestException as e:
                        print(f"Fehler beim Abrufen der Dateigröße für {file_url}: {e}")
                        continue
        return files, directories, total_size

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
                total_progress = self.totaldownloaded / self.totalsize * 100

                self.busytext4 = "%s / %s, %s / %s %2.2d%%" % ( get_size(totaldlfile), get_size(total_size_in_bytes), get_size(self.totaldownloaded), get_size(self.totalsize), total_progress)
                file.write(data)


    def check_url_reachability(url):
        try:
            # Timeout auf 5 Sekunden setzen, um nicht zu lange zu warten
            response = requests.get(url, timeout=5)
            # Rückgabewert: Statuscode der Anfrage
            return response.status_code
        except requests.exceptions.RequestException as e:
            # Falls ein Fehler auftritt (z.B. URL nicht erreichbar), Rückgabe 0
            print(f"Fehler beim Erreichen der URL: {e}")
            return 0


    def split_url(self,url):
        parsed_url = urlparse(url)

        # Wert 1: Schema und Host (inkl. Port, falls vorhanden)
        schema_and_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Wert 2: URI (Pfad und Query-Parameter, falls vorhanden)
        uri = parsed_url.path + ('?' + parsed_url.query if parsed_url.query else '')

        return schema_and_host, uri

####old

    def get_content(self):
        liste = []
        local_exists = []


        try:
                current_folder = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,self.cwd)
                current_folder = current_folder[len(self.basecwd):]
                selected_folder = os.path.join(current_folder,listobj.name)
                local_folder = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,selected_folder)
                selected_folder = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,selected_folder)


                progress = ' \u2302' if os.path.exists(local_folder) else ''

                try:
                    size = listobj.size
                    self.totalsize += size
                    self.progress[listobj.name] = get_size(size)
                except Exception as error:
                    pass

                try:
                    onlinepath = os.path.join(self.cwd,listobj.name)
                    if onlinepath.endswith('/'):
                        folderinfo = playout.getpos_online(self.baseurl,onlinepath)
                        if len(folderinfo) >= 6 and folderinfo[0] == "POS":
                            song = int(float(folderinfo[3]))
                            length = int(float(folderinfo[4]))
                            prozent = (song - 1) / length * 100
                            progress = "%2.2d%%%s"  % (prozent,progress)
                        elif folderinfo[0] == "ERR":
                            progress = "%s%s"  % (folderinfo[0],progress)

                except Exception as error:
                    print (error)
                self.progress[listobj.name.strip('/')] = progress
        except Exception as error:
            print (error)
        finally:
            return hasfolder,liste

