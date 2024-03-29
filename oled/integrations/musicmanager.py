""" Manages music status and control commands for Mopidy and AirPlay """

import settings

class Musicmanager():
    def __init__(self, mopidyconnection):
        self.mopidyconnection = mopidyconnection
        #self.shairportconnection = shairportconnection
        self.playing = False
        self.source = "mpd"

    #def airplay_callback(self, lis, info):
    #    del lis, info
    #    if self.source == "mpd":
    #        self.source = "airplay"
    #        print("Switched to AirPlay")
    #        if self.mopidyconnection.status["state"] == "play":
    #            self.mopidyconnection.playpause()

    def status(self):
        if self.source == "mpd":
            return self.mopidyconnection.status

    def nowplaying(self):
        if self.source == "mpd":
            return self.mopidyconnection.nowplaying
        elif self.source == "airplay":
            if not self.shairportconnection.connected:
                print("Switched to MPD")
                self.source = "mpd"
            return self.shairportconnection.nowplaying()

    def playlist(self):
        if self.source == "mpd":
            try:
                playlist = self.mopidyconnection.client.playlist().copy()
                return playlist
            except:
                return []
        else:
            return []


    def playpause(self):
        if self.source == "mpd":
            return self.mopidyconnection.playpause()

    def previous(self):
        if self.source == "mpd":
            return self.mopidyconnection.previous()

    def next(self):
        if self.source == "mpd":
            return self.mopidyconnection.next()
