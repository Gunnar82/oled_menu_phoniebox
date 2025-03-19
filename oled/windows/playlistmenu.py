""" Playlist menu """
import settings

import config.colors as colors
import config.file_folder as cfg_file_folder

import time
if settings.use_eyed3:
    import eyed3 
import asyncio

from ui.listbase import ListBase

from integrations.logging_config import *

logger = setup_logger(__name__)



class Playlistmenu(ListBase):
    def __init__(self, windowmanager, loop, usersettings,  musicmanager):
        super().__init__(windowmanager, loop, usersettings, "Playlist")
        self.musicmanager = musicmanager


    async def eyed3_playlist(self):

        for idx, a in enumerate(self.playlist):
            if a.startswith("file"):
                a = a[a.find(":")+1:]

            a = a.strip()
            fullpath = cfg_file_folder.AUDIO_BASEPATH_BASE + "/" + a

            if not (a.startswith("http")): #no stream
                try:
                    audiofile = eyed3.load(fullpath)

                    if (audiofile.tag.title != None):
                        try:
                            a = "%2.2d | " % int(audiofile.tag.track_num[0])
                        except:
                            a = " "

                        a += str(audiofile.tag.title)
                        if  (audiofile.tag.artist != None):
                            a += " | " + str(audiofile.tag.artist)
                    else:
                        a = a[a.rfind("/")+1:]

                    audiofile.close()
                except:
                    pass
            a = a[a.rfind("/") + 1:] #filename only
            self.playlist[idx] = a

            self.menu = []
            for itm in self.playlist:
                self.menu.append([itm])

    def activate(self):
        self.window_on_back = "idle"
        self.playlist = self.musicmanager.playlist()

        self.loop.create_task(self.eyed3_playlist())
        try:
            song = -1
            cnt = 0 

            while song < 0 and cnt < 20:
                status = self.musicmanager.status()
                song = int(status['song']) + 1 if ("song" in status) else -1
                cnt += 1
                time.sleep(0.1)
            logger.debug ("Song: %s POS: %s" %(song, self.position))

            self.position = song -1
        except Exception as error:
            logger.debug (f"activate: {error}")
            self.position = - 1



    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)

        if self.position >= 0:
            self.title = "%2.2d / %2.2d" %(self.position + 1,len(self.menu))
        else:
            self.title = "Playlist"

    def push_callback(self,lp=False):
        if self.position == -1 or  self.position == -2 :
            self.windowmanager.set_window("mainmenu")
        else:
            self.musicmanager.play(self.position)

    def on_key_left(self):
        self.windowmanager.set_window("playbackmenu")
