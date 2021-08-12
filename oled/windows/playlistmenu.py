""" Playlist menu """
import settings
import integrations.playout as playout

from ui.menubase import MenuBase

class Playlistmenu(MenuBase):
    def __init__(self, windowmanager, musicmanager):
        self.musicmanager = musicmanager
        super().__init__(windowmanager, "Playlists")

    def activate(self):
        self.menu = self.musicmanager.playlist()
        song = -1 
        while song < 0:
            print ("-1")
            status = self.musicmanager.status()
            song = int(status['song']) + 1 if ("song" in status) else -1

        if song > 4:
            self.counter = 5
            self.page = song -4
        else:
            self.counter = song + 1

    def push_callback(self,lp=False):
        if self.counter < 2 and self.page == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            playout.pc_play(self.page + self.counter-2 + 1) # 1 based

    def on_key_left(self):
        self.windowmanager.set_window("playbackmenu")
