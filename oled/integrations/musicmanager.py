""" Manages music status and control commands for Mopidy and AirPlay """

import settings
import os
import config.file_folder as cfg_file_folder
from integrations.functions import list_files_in_directory, get_file_content


class Musicmanager():
    def __init__(self, mopidyconnection,sqlite):
        self.mopidyconnection = mopidyconnection
        self.client = mopidyconnection.client
        self.sqlite = sqlite
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
            self.save_playback()
            return self.mopidyconnection.playpause()


    def play(self,position = None):
        if self.source == "mpd":
            return self.mopidyconnection.play(position)

    def stop(self):
        if self.source == "mpd":
            self.save_playback()
            return self.mopidyconnection.stop()

    def previous(self):
        if self.source == "mpd":
            self.save_playback()
            return self.mopidyconnection.previous()

    def next(self):
        if self.source == "mpd":
            self.save_playback()
            return self.mopidyconnection.next()


    def loadplaylist(self, name):
        try:
            #self.client.clear()
            #self.client.load(name)
            #self.client.play()
            rootdir =  "/home/pi/RPi-Jukebox-RFID/shared/audiofolders/"
            recursive = ""
            for file in os.listdir(rootdir):
                d = os.path.join(rootdir, file)
                if os.path.isdir(d):
                    recursive = "-v='recursive'"
            run_command("sudo /home/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh -d=\"%s\" %s" % (name,recursive))

            self.loadedplaylist = name
            print(f"Loaded and playing Playlist {name}")
        except musicpd.ConnectionError:
            self._connectionlost()

    def play_latest_folder(self,folder='Hörspiele'):
        latest = self.sqlite.get_latest_folder(folder)

        if latest:
            fullpath = os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,latest)
            self.playfolderstart(fullpath,latest)

    def get_latest_folder(self, folder='Hörspiele'):
        return self.sqlite.get_latest_folder(folder)


    def playfolderstart(self,fullfolder,foldername):
        pos, mtime = self.sqlite.get_playback_info(foldername)

        songs = list_files_in_directory(fullfolder)
        mysongs = []
        for song in songs:
            addsong = os.path.join(foldername, song)
            if addsong.endswith('.mp3'):
                mysongs.append(addsong)
            elif addsong.endswith('livestream.txt'):
                mysongs.append(get_file_content(os.path.join(cfg_file_folder.AUDIO_BASEPATH_BASE,addsong)))
        mysongs.sort()

        self.playliststart(mysongs,[int(pos),mtime])

    def playliststart(self,songs = None,seekto = None):
        try:
            self.stop()
            self.client.clear()
            for song in songs:
                self.client.add(song)
            print (seekto)
            if seekto:
                if isinstance(seekto[0],str):
                    for idx, song in enumerate(songs):
                        if song == seekto[0]:
                            print ("gefunden")
                            self.client.seek(idx,int(float(seekto[1])))
                            return
                else:
                    print (seekto)
                    self.client.seek(seekto[0],int(float(seekto[1])))
                    return

            self.play()
            return
        except Exception as error:
            print (error)

    def save_playback(self):
        """Überwacht die Wiedergabe von MPD und speichert die Informationen in der DB."""
        # Holen der aktuellen Wiedergabeinformationen
        current_song = self.client.currentsong()
        status = self.client.status()

        playlist_length = self.client.status().get('playlistlength', 0)
        if current_song:
            artist = current_song.get('artist', 'Unbekannt')
            album = current_song.get('album', 'Unbekannt')
            title = current_song.get('title', 'Unbekannt')
            mfile = current_song.get('file', 'Unbekannt')
            pos = current_song.get('pos','N/A')
            elapsed = status.get('elapsed','N/A')
            mfolder = get_parent_folder(mfile)

            # Speicherung in der Datenbank (jetzt auch mit Playlist-Länge)
            if status['state'] != 'stop':
                self.sqlite.store_playback_info(artist, album, title, mfile, mfolder, pos, elapsed, playlist_length)
            else:
                print ("state stop - Keine Speicherung")

    def get_folder_info(self,folder):
        return self.sqlite.get_folder_info(folder)


    def get_radio_stations(self):
        return self.sqlite.get_radio_stations()

    def update_radiostations(self,stations):
        return self.sqlite.update_radiostations(stations)


    def delete_radiostations(self,):
        return self.sqlite.delete_radiostations()
