import sqlite3
import time
import os

from integrations.functions import get_parent_folder

import config.file_folder as cfg_file_folder

class sqliteDB:
    def __init__(self, client, db_file=cfg_file_folder.FILE_MPD_PLAYBACK_DB):
        self.db_file = db_file
        self.client = client

        # Überprüfen, ob die Datenbank existiert
        if not self.check_db_exists():
            print(f"Die Datenbank {self.db_file} existiert noch nicht. Sie wird jetzt erstellt...")
        else:
            print(f"Die Datenbank {self.db_file} existiert bereits.")

        # Datenbank und Tabelle erstellen
        self.create_db()

    def check_db_exists(self):
        """Prüft, ob die Datenbankdatei existiert."""
        return os.path.exists(self.db_file)

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
        print (result)
        conn.close()
        return result[0] if result[0] is not None  else 0