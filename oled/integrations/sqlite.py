import sqlite3
import threading

import time
import os

from integrations.functions import get_parent_folder

import config.file_folder as cfg_file_folder

class sqliteDB:
    def __init__(self):
        self.local = threading.local() 
        try:
            db_file = cfg_file_folder.FILE_MPD_PLAYBACK_DB
        except:
            db_file= "/home/pi/oledctrl/oled/config/mpd_playback.db"

        self.db_file = db_file

        # Datenbank und Tabelle erstellen
        self.create_db()

    def get_connection(self):
        """Stellt sicher, dass jeder Thread eine eigene DB-Verbindung bekommt."""
        if not hasattr(self.local, "conn"):
            self.local.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            self.local.cursor = self.local.conn.cursor()
        return self.local.conn, self.local.cursor

    def create_db(self):
        """Erstellt die SQLite-Datenbank und die Tabelle, falls notwendig."""
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        # Tabelle erstellen (falls nicht vorhanden), jetzt auch mit "file" Feld
        self.cursor.execute('''
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


        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS radiostations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT,
            station_url TEXT,
            station_uuid TEXT UNIQUE
        )''')

        """Erstellt die Tabelle für Einstellungen, falls sie nicht existiert."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        )
        """)


        self.conn.commit()

    def store_playback_info(self, artist, album, title, mfile, mfolder, pos, elapsed, playlist_length):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""

        # Einfügen der Wiedergabeinformationen (jetzt auch mit "playlist_length")
        self.cursor.execute('''
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
        self.conn.commit()


    def get_playback_info(self, folder):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.cursor.execute('SELECT pos, elapsed FROM playback WHERE folder = ? AND playlist_length > 0;', (folder ,))
        result = self.cursor.fetchone()
        return result if result else (0, 0)



    def get_folder_info(self, folder):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.cursor.execute('SELECT round( AVG(1.0 * pos / playlist_length) *100,1) FROM playback WHERE folder LIKE ? AND playlist_length > 0;', (folder + '%',))
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None  else 0

    def get_latest_folder(self, folder="Hörspiel"):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.cursor.execute('select folder from playback Where folder LIKE ? || \'%\' ORDER BY time_played DESC LIMIT 1;', (folder,))
        result = self.cursor.fetchone()
        try:
            return result[0] if result[0] is not None  else folder
        except:
            return folder


    def get_radio_stations(self):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.cursor.execute('SELECT id, station_name, station_url FROM radiostations ORDER BY id ASC;')
        result = self.cursor.fetchall()
        return result if result else (0, 'N/A', 'N/A')



    def update_radiostations(self,stations):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""

        # Einfügen der Wiedergabeinformationen (jetzt auch mit "playlist_length")
        sql = ('''
        INSERT INTO radiostations (station_name, station_url, station_uuid)
        VALUES (?, ?, ?)
        ON CONFLICT(station_uuid) DO UPDATE SET
            station_name = excluded.station_name,
            station_url = excluded.station_url
        ''')
        self.cursor.executemany(sql, stations)
        self.conn.commit()

    def delete_radiostations(self):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""

        self.cursor.execute("DELETE FROM radiostations")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='radiostations'")  # Reset der ID
        self.conn.commit()


    def load_user_settings(self):
        """Lädt alle Einstellungen aus der Datenbank und setzt sie als Attribute."""
        conn, cursor = self.get_connection()
        cursor.execute("SELECT setting_key, setting_value FROM settings")
        return cursor.fetchall()

    def save_user_setting(self, key, value):
        """Speichert oder aktualisiert eine Einstellung in der DB."""
        conn, cursor = self.get_connection()
        cursor.execute("""
        INSERT OR REPLACE INTO settings (setting_key, setting_value)
        VALUES (?, ?)
        """, (key, value))
        conn.commit()

    def __del__(self):
        self.conn.close()
        