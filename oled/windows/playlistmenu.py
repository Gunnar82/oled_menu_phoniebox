""" Playlist menu """
import settings
import integrations.playout as playout
import time
from ui.listbase import ListBase

class Playlistmenu(ListBase):
    def __init__(self, windowmanager, musicmanager):
        self.musicmanager = musicmanager
        super().__init__(windowmanager, "Playlist")

    def activate(self):
        self.window_on_back = "idle"
        self.menu = self.musicmanager.playlist()
        self.song = -1
        cnt = 0 
        while self.song < 0 and cnt < 20:
            status = self.musicmanager.status()
            self.song = int(status['song']) + 1 if ("song" in status) else -1
            cnt += 1
            time.sleep(0.1)
        if self.song > self.displaylines:
            self.counter = self.displaylines + 1
            self.page = self.song - self.displaylines
        else:
            self.counter = self.song + 1

    def turn_callback(self,direction,key=False):
        super().turn_callback(direction,key=key)

        if self.position >= 0:
            self.title = "%2.2d / %2.2d" %(self.position + 1,len(self.menu))
        else:
            self.title = "Playlist"

    def push_callback(self,lp=False):
        if self.counter < 2 and self.page == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            playout.pc_play(self.position + 1) # 1 based

    def on_key_left(self):
        self.windowmanager.set_window("playbackmenu")
