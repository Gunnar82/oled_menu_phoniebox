""" Playlist menu """
from ui.menubase import MenuBase

class Playlistmenu(MenuBase):
    def __init__(self, windowmanager, musicmanager):
        self.musicmanager = musicmanager
        super().__init__(windowmanager, "Playlists")

    def activate(self):
        self.menu = []

    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            self.windowmanager.set_window("idle")
