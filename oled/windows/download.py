""" Playlist menu """
import settings

import time
import requests
import htmllistparse
import os
import asyncio

from ui.listbase import ListBase
import time
import integrations.playout as playout




class DownloadMenu(ListBase):
    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, "Download")
        self.loop = loop
        self.window_on_back = "idle"
        self.progress = {}

    def activate(self):
        self.website = settings.ONLINEURL
        self.set_busy("Verbinde Online",settings.SYMBOL_CLOUD,self.website,busyrendertime=5)
        self.renderbusy()
        time.sleep(3)
        try:
            r = requests.get(self.website)
            if r.status_code != 200: raise "nicht 200"
        except:
            self.set_busy("Keine Verbindung möglich",settings.SYMBOL_NOCLOUD)
            self.windowmanager.set_window("idle")
            self.renderbusy()
            time.sleep(3)

            return
        self.baseurl = self.website[:self.website.rfind('/')]
        self.basecwd= self.website[self.website.rfind('/'):]

        self.cwd = self.basecwd

        test, self.menu = self.get_content()

        self.position = -1

    def get_content(self):
        liste = []
        hasfolder = False
        try:
            if len(self.cwd) < len(self.basecwd): self.cwd = self.basecwd
            url = self.baseurl + requests.utils.quote(self.cwd)
            self.cwd,listing = htmllistparse.fetch_listing(url, timeout=30)
            for listobj in listing:    #menu.append(entry)
                if '/' in listobj.name and not hasfolder: hasfolder = True

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

                        #for s in subfiles:
                        #    s = s.strip()
                        #    protocol = s[:s.index('://')]
                        #    uri = requests.utils.quote(s[s.index('://') + 3:])
                        #    url = protocol + '://' + uri
                        #    subfiles2.append(url)

                        lastplayedfile =  folderconf["CURRENTFILENAME"]

                        if lastplayedfile in subfiles2:
                            pos = subfiles2.index(lastplayedfile)
                            prozent = (pos + 1) / len (subfiles2)
                            self.progress[listobj.name.strip('/')] = prozent * 100


                except:
                    pass
        except:
            pass
        finally:
            return hasfolder,liste



    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)

        if key == 'left':
            pos = self.cwd.rfind("/")
            self.cwd = self.cwd[:pos]
            test, self.menu = self.get_content()

        if self.position >= 0:
            self.title = "%2.2d / %2.2d" %(self.position + 1,len(self.menu))
        else:
            self.title = "Online"

    def push_callback(self,lp=False):
        if self.position == -1 or  self.position == -2 :
            self.windowmanager.set_window("mainmenu")
        else:
            self.set_busy("Auswahl verarbeiten...",settings.SYMBOL_CLOUD,self.menu[self.position])
            self.loop.create_task(self.push_handler())

    async def push_handler(self):
        await asyncio.sleep(1)
        try:
            self.cwd += '/' + self.menu[self.position]
            self.url = self.baseurl + self.cwd

            hasfolder, items = self.get_content()

            if hasfolder:
                self.menu = items
            else:
                directory = os.path.join(settings.AUDIO_BASEPATH_ONLINE,self.cwd[len(self.basecwd):][1:])

                if not os.path.exists(directory): os.makedirs(directory)

                try:
                    filename = os.path.join(directory,"livestream.txt")
                    ofile = open(filename,"w")

                    for item in items: ofile.write(self.baseurl + requests.utils.quote(self.cwd + '/' + item) + '\n')
                    ofile.close()
                    foldername = directory[len(settings.AUDIO_BASEPATH_BASE):]
                    playout.pc_playfolder(foldername)

                except:
                    pass
        except:
            pass


        #self.windowmanager.set_window("idle")




