""" Playlist menu """
import settings

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




class DownloadMenu(ListBase):
    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, "Download")
        self.loop = loop
        self.window_on_back = "idle"
        self.timeout = False
        self.contrasthandle = False
        self.canceled = False
        self.downloading = False
        self.totalsize = 0

    def activate(self):
        self.progress = {}
        self.items = []
        self.selector = False
        self.download = False
        self.website = settings.ONLINEURL
        self.set_busy("Verbinde Online",settings.SYMBOL_CLOUD,self.website,busyrendertime=5)
        self.renderbusy()
        time.sleep(2)

        self.baseurl = self.website[:settings.ONLINEURL.find('/',9)]
        self.basecwd= self.website[settings.ONLINEURL.find('/',9):]

        try:
            with open(settings.FILE_LAST_ONLINE,"r") as f:
                self.website = f.read()
                self.cwd = self.website[len(self.baseurl):]
            if not self.website.startswith(settings.ONLINEURL): raise "Website geändert"

        except Exception as error:
            self.set_busy(error,settings.SYMBOL_NOCLOUD)
            time.sleep(3)

            self.position = -1
            self.website = settings.ONLINEURL
            self.cwd = self.basecwd

        try:
            r = requests.get(self.website)
            if r.status_code != 200: raise "Keine Verbindung, Code: %d" %(r.status_code)
        except Exception as error:
            self.set_busy(error,settings.SYMBOL_NOCLOUD)
            self.windowmanager.set_window("idle")
            self.renderbusy()
            time.sleep(3)

            return

        self.on_key_left()

    def get_content(self):
        liste = []
        hasfolder = False
        try:
            if len(self.cwd) <= len(self.basecwd):
                self.cwd = self.basecwd
            url = self.baseurl + requests.utils.quote(self.cwd)+ '/'
            self.cwd,listing = htmllistparse.fetch_listing(url, timeout=30)

            self.totalsize = 0
            for listobj in listing:
                if '/' in listobj.name and not hasfolder: hasfolder = True

                try:
                    size = listobj.size
                    self.progress[listobj.name] = get_size(size)
                    self.totalsize += size
                except Exception as error:
                    pass

                liste.append(listobj.name.strip('/'))
                current_folder = os.path.join(settings.AUDIO_BASEPATH_ONLINE,self.cwd)
                current_folder = current_folder[len(self.basecwd):]
                selected_folder = os.path.join(current_folder,listobj.name)
                selected_folder = os.path.join(settings.AUDIO_BASEPATH_ONLINE,selected_folder[1:])

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
                    if (folderconf["CURRENTFILENAME"] != "") and ((folderconf["RESUME"]).lower() == "on"):
                        fn = os.path.join(selected_folder,"livestream.txt")
                        livestream = open(fn, "r")
                        subfiles = livestream.readlines()
                        livestream.close()

                        subfiles2 = [s.strip() for s in subfiles]

                        lastplayedfile =  folderconf["CURRENTFILENAME"]

                        if lastplayedfile in subfiles2:
                            pos = subfiles2.index(lastplayedfile)
                            prozent = (pos + 1) / len (subfiles2) * 100
                            self.progress[listobj.name.strip('/')] = "%2.2d %%"  % (prozent)
                except Exception as error:
                    pass
        except:
            pass
        finally:
            return hasfolder,liste


    def downloadfolder(self):
        try:
            self.downloading = True
            settings.callback_active = True

            destdir = settings.AUDIO_BASEPATH_BASE + self.url[len(settings.ONLINEURL):]

            if not os.path.exists(destdir): os.makedirs(destdir)

            for item in self.items:

                if self.canceled: break;

                url = self.baseurl + requests.utils.quote(self.cwd + '/' + item)
                destination = destdir + '/' + item
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


    async def push_handler(self,button = '*'):
        await asyncio.sleep(1)
        try:
            if self.selector:
                if self.position == 0:
                    directory = os.path.join(settings.AUDIO_BASEPATH_ONLINE,self.cwd[len(self.basecwd):][1:])
                    try:
                        with open(settings.FILE_LAST_ONLINE,"w") as f:
                            f.write(self.url)
                    except Exception as error:
                        print (error)
                    if not os.path.exists(directory): os.makedirs(directory)

                    try:
                        filename = os.path.join(directory,"livestream.txt")
                        with open(filename,"w") as ofile:
                            for item in self.items: ofile.write(self.baseurl + requests.utils.quote(self.cwd + '/' + item) + '\n')
                        foldername = directory[len(settings.AUDIO_BASEPATH_BASE):]
                        playout.pc_playfolder(foldername)
                        self.windowmanager.set_window("idle")
                    except:
                        pass
                elif self.position == 1:
                    self.loop.run_in_executor(None, self.downloadfolder)
                elif self.position == 2 and self.selector:
                    self.menu = self.items
                elif self.position == -1 and self.selector:
                    self.selector = False
                elif self.position == 3:
                    destdir = settings.AUDIO_BASEPATH_BASE + self.url[len(settings.ONLINEURL):]
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
                self.basetitle = self.menu[self.position]
                self.cwd += '/' + self.menu[self.position]
                self.url = self.baseurl + self.cwd

                hasfolder, self.items = self.get_content()

                if hasfolder:
                    self.menu = self.items
                else:
                    self.selector = True
                    try:
                        current_title = "Fortschritt: %s" % (self.progress[self.menu[self.position]])
                    except:
                        current_title = ""
                    self.menu = ["Abspielen", "Herunterladen","informationen","Lokal löschen","","Anzahl Titel :%2.2d " %  (len(self.items)),"Gesamtgröße %s" % (get_size(self.totalsize)),current_title]

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
            if not self.selector or self.position == 0: self.set_busy("Auswahl verarbeiten...",settings.SYMBOL_CLOUD,self.menu[self.position],busyrendertime=2)
            self.loop.create_task(self.push_handler())

    def on_key_left(self):
        pos = self.cwd.rfind("/")
        last = self.cwd[pos+1:]

        self.cwd = self.cwd[:pos]
        self.url = self.baseurl + self.cwd

        pos = self.cwd.rfind("/")

        test, self.menu = self.get_content()

        try:
            self.basetitle = self.cwd[pos+1:]
        except:
            self.basetitle = self.windowname

        try:
            self.position = self.menu.index(last)
        except:
            self.position = -1

    def render(self):
        if self.canceled or self.downloading:
            self.renderbusy()
        else:
            super().render()
