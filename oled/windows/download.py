""" Playlist menu """
import settings

import config.colors as colors
import config.symbols as symbols

import time
import requests
import htmllistparse
import os
import asyncio
import shutil

from ui.listbase import ListBase
import time
import integrations.playout as playout
from integrations.functions import get_size

import config.online as cfg_online
import config.file_folder as cfg_file_folder


class DownloadMenu(ListBase):
    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop, "Download")
        self.direct_play_last_folder = False

        self.window_on_back = "idle"
        self.timeout = False
        self.contrasthandle = False
        self.canceled = False
        self.downloading = False
        self.totalsize = 0
        self.lastplayedfile = ""

    def activate(self):
        self.progress = {}
        self.items = []
        self.selector = False
        self.download = False
        self.website = cfg_online.ONLINE_URL
        self.set_busy("Verbinde Online",symbols.SYMBOL_CLOUD,self.website,busyrendertime=5)
        self.renderbusy()
        time.sleep(2)

        self.baseurl = self.website[:cfg_online.ONLINE_URL.find('/',9)]
        self.basecwd= self.website[cfg_online.ONLINE_URL.find('/',9):]

        try:
            with open(cfg_file_folder.FILE_LAST_ONLINE,"r") as f:
                self.website = f.read()
                self.cwd = self.website[len(self.baseurl):]
            if not self.website.startswith(cfg_online.ONLINE_URL): raise "Website geändert"

        except Exception as error:
            self.set_busy("Dateifehler",symbols.SYMBOL_NOCLOUD,str(error))
            time.sleep(3)

            self.position = -1
            self.website = cfg_online.ONLINE_URL
            self.cwd = self.basecwd

        try:
            r = requests.get(self.website)
            if r.status_code == 404:
                print("URL nicht gefunden")
                self.website = cfg_online.ONLINE_URL
                self.cwd = self.basecwd
                r = requests.get(self.website)
                if r.status_code != 200:
                    raise Exception( "Keine Verbindung, Code: %d" % (r.status_code))
            elif r.status_code != 200:
                raise Exception("Keine Verbindung, Code: %d" % (r.status_code))
        except requests.exceptions.RequestException as error:
            self.set_busy("Verbindungsfehler",symbols.SYMBOL_NOCLOUD,self.website,set_window_to="idle")
            return
        except requests.exceptions.HTTPError as error:
            self.set_busy("HTTP-Fehler",symbols.SYMBOL_NOCLOUD,str(error),set_window_to="idle")
            return

        if self.direct_play_last_folder:
            self.direct_play_last_folder = False
            self.url = self.baseurl + self.cwd
            folders, self.items = self.get_content()
            if not folders:
                self.playfolder()
        else:
            self.on_key_left()

    def get_content(self):
        liste = []
        local_exists = []
        hasfolder = False

        if not self.cwd.endswith('/'): self.cwd += '/'

        try:
            url = self.baseurl + requests.utils.quote(self.cwd)

            temp, listing = htmllistparse.fetch_listing(url, timeout=30)
            self.totalsize = 0

            for listobj in listing:
                if '/' in listobj.name and not hasfolder: hasfolder = True


                current_folder = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,self.cwd)
                current_folder = current_folder[len(self.basecwd):]
                selected_folder = os.path.join(current_folder,listobj.name)
                local_folder = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,selected_folder)
                selected_folder = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,selected_folder)

                liste.append(listobj.name.strip('/'))

                progress = ' \u2302' if os.path.exists(local_folder) else ''

                try:
                    size = listobj.size
                    self.totalsize += size
                    self.progress[listobj.name] = get_size(size)
                except Exception as error:
                    pass

                try:
                    fn = os.path.join(selected_folder,"folder.conf")

                    folder_conf_file = open(fn,"r")
                    lines = folder_conf_file.readlines()
                    folder_conf_file.close()

                    folderconf = {}
                    folderconf["RESUME"] = "off"
                    folderconf["CURRENTFILENAME"] = ""
                    for line in lines:
                        _key, _val = line.split('=',2)
                        folderconf[_key] = _val.replace("\"","").strip()
                    self.lastplayedfile =  folderconf["CURRENTFILENAME"]

                    if (folderconf["CURRENTFILENAME"] != "") and ((folderconf["RESUME"]).lower() == "on"):
                        fn = os.path.join(selected_folder,"livestream.txt")
                        livestream = open(fn, "r")
                        subfiles = livestream.readlines()
                        livestream.close()

                        subfiles2 = [s.strip() for s in subfiles]

                        if self.lastplayedfile in subfiles2:
                            pos = subfiles2.index(self.lastplayedfile)
                            prozent = (pos + 1) / len (subfiles2) * 100

                            progress = "%2.2d%%%s"  % (prozent,progress)

                except Exception as error:
                    pass
                self.progress[listobj.name.strip('/')] = progress
        except Exception as error:
            print (error)
        finally:
            print(self.progress)
            return hasfolder,liste


    def downloadfolder(self):
        try:
            self.downloading = True
            settings.callback_active = True
            destdir = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,self.url[len(cfg_online.ONLINE_URL):])

            if not os.path.exists(destdir): os.makedirs(destdir)

            for item in self.items:

                if self.canceled: break;

                url = self.baseurl + requests.utils.quote(self.cwd + '/' + self.stripitem(item))
                destination = os.path.join(destdir, self.stripitem(item))
                self.busyrendertime = 1
                self.busytext1="Download %2.2d von %2.2d" %(self.items.index(item) + 1,len(self.items) )
                self.busytext2=item
                self.busytext3="Abbruch mit beliebiger Taste"
                self.busysymbol = "\uf0ed"
                r = requests.get(url)
                if r.status_code == 200:
                    if self.canceled: break;

                    with open(destination,'wb') as f:
                        f.write(r.content)
        except Exception as error:
            self.canceled = True
            self.set_busy(error)
        finally:
            time.sleep(3)
            self.canceled = False
            self.downloading = False
            settings.callback_active = False


    def playfolder(self):

        directory = os.path.join(cfg_file_folder.AUDIO_BASEPATH_ONLINE,self.cwd[len(self.basecwd):])

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
                    additem = self.baseurl + requests.utils.quote(self.cwd + self.stripitem(item)) + '\n'
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
                    self.menu = self.items
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

                hasfolder, self.items = self.get_content()

                if hasfolder:
                    self.menu = self.items
                else:
                    self.selector = True
                    try:
                        posstring = playout.getpos_online(self.baseurl,self.cwd).split('|')
                        if posstring[0] == "POS":
                            online_file = "Datei: %s" % (posstring[1])
                            online_pos = "Pos:  %s " % (posstring[2])

                        else:
                            online_file = ""
                            online_pos = ""
                    except:
                        online_file = ""
                        online_pos = ""

                    try:
                        current_pos = "Fortschritt: %s" % (self.progress[self.menu[self.position]])
                    except:
                        current_pos = "Fortschritt nicht verfügbar"

                    self.menu = []
                    self.menu.append("Abspielen")
                    self.menu.append("Herunterladen")
                    self.menu.append("informationen")
                    self.menu.append("Lokal löschen")
                    self.menu.append("")
                    self.menu.append("Anzahl Titel :%2.2d " %  (len(self.items)))
                    self.menu.append("Gesamtgröße %s" % (get_size(self.totalsize)))
                    self.menu.append(current_pos)
                    self.menu.append("")

                    try:
                        self.menu.append("Aktueller Titel:")
                        self.menu.append(" " % (self.lastplayedfile[self.lastplayedfile.rfind('/')+1:]))
                        self.menu.append("")
                    except:
                        pass

                    self.menu.append("Onlineinformationen:")
                    self.menu.append(online_file)
                    self.menu.append(online_pos)

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
            if not self.selector or self.position == 0: self.set_busy("Auswahl verarbeiten...",symbols.SYMBOL_CLOUD,self.menu[self.position],busyrendertime=2)
            self.loop.create_task(self.push_handler())

    def on_key_left(self):

        self.selector = False
        self.cwd = self.cwd.rstrip('/')
        pos = self.cwd.rfind('/')

        last = self.cwd[pos+1:]

        self.cwd = self.cwd[:pos]

        if len(self.cwd) <= len(self.basecwd):
            self.cwd = self.basecwd
            last = "_-__"

        self.url = self.baseurl + self.cwd

        #pos = self.cwd.rfind("/")

        test, self.menu = self.get_content()

        try:
            self.position =  self.menu.index(last) 
        except:
            try:
                self.position =  self.menu.index('%s \u2302'% (last))
            except:
                self.position = -1

        try:
            if len(self.cwd) > len (self.basecwd):
                self.basetitle = self.cwd[pos+1:]
            else:
                self.basetitle = "Online"
        except Exception as error:
            self.basetitle = self.windowtitle

    def stripitem(self, rawitem):
        return rawitem.rstrip('\u2302').rstrip()

    def render(self):
        if self.canceled or self.downloading:
            self.renderbusy()
        else:
            super().render()
