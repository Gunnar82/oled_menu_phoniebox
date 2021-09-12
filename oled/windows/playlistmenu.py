""" Playlist menu """
import settings
import integrations.playout as playout
import time
from ui.menubase import MenuBase

class Playlistmenu(MenuBase):
    def __init__(self, windowmanager, musicmanager):
        self.musicmanager = musicmanager
        super().__init__(windowmanager, "Playlist")

    def activate(self):
        self.menu = self.musicmanager.playlist()
        self.song = -1
        cnt = 0 
        while self.song < 0 and cnt < 20:
            status = self.musicmanager.status()
            self.song = int(status['song']) + 1 if ("song" in status) else -1
            cnt += 1
            time.sleep(0.1)
        if self.song > 4:
            self.counter = 5
            self.page = self.song -4
        else:
            self.counter = self.song + 1

    def turn_callback(self,direction,key=False):
        if key in ['A','B','C','D']:
            if key == 'A':
                self.page = 0
                self.counter = 2
            elif key == 'B':
                direction = -4
            elif key == 'C':
                direction = 4
            elif key == 'D':
                self.counter = 5
                self.page = len(self.menu) -4

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
