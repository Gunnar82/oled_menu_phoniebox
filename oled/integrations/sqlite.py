import sqlite3
import time
import os

from integrations.functions import get_parent_folder

import config.file_folder as cfg_file_folder

class sqliteDB:
    def __init__(self, client):
        try:
            db_file = cfg_file_folder.FILE_MPD_PLAYBACK_DB
        except:
            db_file= "/home/pi/oledctrl/oled/config/mpd_playback.db"

        self.db_file = db_file
        self.client = client

        # Datenbank und Tabelle erstellen
        self.create_db()


    def create_db(self):
        """Erstellt die SQLite-Datenbank und die Tabelle, falls notwendig."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Tabelle erstellen (falls nicht vorhanden), jetzt auch mit "file" Feld
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS playback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT,
            album TEXT,
            title TEXT,
            file TEXT,
            folder TEXT UNIQUE,
            pos INTEGER,
            playlist_length INTEGER,
            elapsed text,
            time_played TIMESTAMP
        )''')


        cursor.execute('''
        CREATE TABLE IF NOT EXISTS radiostations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT,
            station_url TEXT,
            station_uuid TEXT UNIQUE
        )''')

        conn.commit()
        conn.close()

    def store_playback_info(self, artist, album, title, mfile, mfolder, pos, elapsed, playlist_length):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Einfügen der Wiedergabeinformationen (jetzt auch mit "playlist_length")
        cursor.execute('''
        INSERT INTO playback (artist, album, title, file, folder, pos, elapsed, playlist_length, time_played)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(folder) DO UPDATE SET
            artist=excluded.artist,
            album=excluded.album,
            title=excluded.title,
            file=excluded.file,
            pos=excluded.pos,
            elapsed=excluded.elapsed,
            playlist_length=excluded.playlist_length,
            time_played=excluded.time_played''', (artist, album, title, mfile, mfolder, pos, elapsed, playlist_length, time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

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
                self.store_playback_info(artist, album, title, mfile, mfolder, pos, elapsed, playlist_length)
            else:
                print ("state stop - Keine Speicherung")


    def get_playback_info(self, folder):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT pos, elapsed FROM playback WHERE folder = ? AND playlist_length > 0;', (folder ,))
        result = cursor.fetchone()
        conn.close()
        return result if result else (0, 0)



    def get_folder_info(self, folder):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT round( AVG(1.0 * pos / playlist_length) *100,1) FROM playback WHERE folder LIKE ? AND playlist_length > 0;', (folder + '%',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] is not None  else 0

    def get_latest_folder(self, folder="Hörspiel"):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('select folder from playback Where folder LIKE ? || \'%\' ORDER BY time_played DESC LIMIT 1;', (folder,))
        result = cursor.fetchone()
        conn.close()
        try:
            return result[0] if result[0] is not None  else folder
        except:
            return folder


    def get_radio_stations(self):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id, station_name, station_url FROM radiostations ORDER BY id ASC;')
        result = cursor.fetchall()
        print (result)
        conn.close()
        return result if result else (0, 'N/A', 'N/A')



    def update_radiostations(self,stations):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Einfügen der Wiedergabeinformationen (jetzt auch mit "playlist_length")
        sql = ('''
        INSERT INTO radiostations (station_name, station_url, station_uuid)
        VALUES (?, ?, ?)
        ON CONFLICT(station_uuid) DO UPDATE SET
            station_name = excluded.station_name,
            station_url = excluded.station_url
        ''')
        cursor.executemany(sql, stations)
        conn.commit()
        conn.close()



    def delete_radiostations(self):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM radiostations")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='radiostations'")  # Reset der ID
        conn.commit()
        conn.close()


