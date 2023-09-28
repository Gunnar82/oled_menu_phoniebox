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
        self.items = []
        self.timeout = False
        self.contrasthandle = False
        self.canceled = False
        self.downloading = False


    def activate(self):
        self.selector = False
        self.download = False
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
        self.baseurl = self.website[:self.website.find('/',9)]
        self.basecwd= self.website[self.website.find('/',9):]
        self.cwd = self.basecwd

        test, self.menu = self.get_content()

        self.position = -1

    def get_content(self):
        liste = []
        hasfolder = False
        try:
            if len(self.cwd) < len(self.basecwd): self.cwd = self.basecwd
            url = self.baseurl + requests.utils.quote(self.cwd)+ '/'
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
        if self.downloading:
            self.canceled = True
        elif self.position == -1 or  self.position == -2 :
            self.windowmanager.set_window("mainmenu")
        else:
            if not self.selector: self.set_busy("Auswahl verarbeiten...",settings.SYMBOL_CLOUD,self.menu[self.position],busyrendertime=2)
            self.loop.create_task(self.push_handler())

    async def push_handler(self,button = '*'):
        await asyncio.sleep(1)
        try:
            if self.selector:
                if self.position == 0:
                    directory = os.path.join(settings.AUDIO_BASEPATH_ONLINE,self.cwd[len(self.basecwd):][1:])

                    if not os.path.exists(directory): os.makedirs(directory)

                    try:
                        filename = os.path.join(directory,"livestream.txt")
                        ofile = open(filename,"w")

                        for item in self.items: ofile.write(self.baseurl + requests.utils.quote(self.cwd + '/' + item) + '\n')
                        ofile.close()
                        foldername = directory[len(settings.AUDIO_BASEPATH_BASE):]
                        playout.pc_playfolder(foldername)
                        self.windowmanager.set_window("idle")
                    except:
                        pass
                elif self.position == 1:
                    window_on_back = self.window_on_back
                    self.window_on_back = ""
                    try:
                        self.downloading = True
                        self.changerender = True
                        self.busyrendertime = 0.1
                        settings.callback_active = True

                        destdir = settings.AUDIO_BASEPATH_BASE + self.url[len(self.website):]

                        if not os.path.exists(destdir): os.makedirs(destdir)

                        for item in self.items:

                            if self.canceled: raise Exception("Abbruch")

                            url = self.baseurl + requests.utils.quote(self.cwd + '/' + item)
                            destination = destdir + '/' + item
                            self.busyrendertime = 0.1
                            self.busytext1="Download %2.2d von %2.2d" %(self.items.index(item) + 1,len(self.items) )
                            self.busytext2=item
                            r = requests.get(url)
                            if r.status_code == 200:
                                with open(destination,'wb') as f:
                                    f.write(r.content)
                            await asyncio.sleep(0.3)
                    except Exception as error:
                        self.busyrendertime = 5
                        self.busytext1=error
                        self.busytext2 = error
                        self.busysymbol = settings.SYMBOL_CLOUD
                        await asyncio.sleep(3)
                    finally:
                        print ("finally")
                        self.window_on_back = window_on_back
                        await asyncio.sleep(0.3)
                        self.canceled = False
                        self.downloading = False
                        settings.callback_active = False
                        self.changerender = False
                        

            else:
                self.cwd += '/' + self.menu[self.position]
                self.url = self.baseurl + self.cwd

                hasfolder, self.items = self.get_content()

                if hasfolder:
                    self.menu = self.items
                else:
                    self.selector = True
                    self.menu = ["Abspielen", "Herunterladen"]

                    return

        except:
            pass
        finally:
            self.position = -1


        #self.windowmanager.set_window("idle")




