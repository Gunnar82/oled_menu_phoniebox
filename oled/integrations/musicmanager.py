""" Manages music status and control commands for Mopidy and AirPlay """
import eyed3
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
                for idx, a in enumerate(playlist):
                    if a.startswith("file"): 
                        a = a[a.find(":")+1:]

                    a = a.strip()
                    fullpath = settings.AUDIO_BASEPATH_BASE + "/" + a

                    if not (a.startswith("http")): #stream
                        try:
                            audiofile = eyed3.load(fullpath)
                            if  (audiofile.tag.title != None):
                                a = str(audiofile.tag.title)
                                if  (audiofile.tag.artist != None):
                                    a += " | " + str(audiofile.tag.artist)

                            audiofile.close()
                        except:
                            pass
                        #a = a[a.rfind("/") + 1:] #filename only
                    playlist[idx] = a
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
