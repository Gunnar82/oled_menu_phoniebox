import sqlite3
import threading

import time
import os
import json


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

        self.save_user_setting('startup',time.monotonic())
        self.save_user_setting('shutdowntime',time.monotonic()- 1)

    def create_connection(self):
        """Erstellt eine Verbindung, wenn sie nicht existiert (pro Thread)."""
        if not hasattr(self.local, "conn"):  # Prüft, ob der Thread bereits eine Verbindung hat
            self.local.conn = sqlite3.connect(self.db_file, check_same_thread=True)
            self.local.cursor = self.local.conn.cursor()

    def create_db(self):
        """Erstellt die SQLite-Datenbank und die Tabelle, falls notwendig."""
        self.create_connection()

        # Tabelle erstellen (falls nicht vorhanden), jetzt auch mit "file" Feld
        self.local.cursor.execute('''
        CREATE TABLE IF NOT EXISTS playback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_song TEXT,
            mfile TEXT,
            folder TEXT UNIQUE,
            pos INTEGER,
            playlist_length INTEGER,
            elapsed text,
            mstatus TEXT,
            time_played TIMESTAMP
        )''')


        self.local.cursor.execute('''
        CREATE TABLE IF NOT EXISTS radiostations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT,
            station_url TEXT,
            station_uuid TEXT UNIQUE
        )''')

        """Erstellt die Tabelle für Einstellungen, falls sie nicht existiert."""
        self.local.cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        )
        """)


        self.local.conn.commit()

    def store_playback_info(self, current_song, mfile, mfolder, pos, elapsed, status, playlist_length):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""
        self.create_connection()

        # Einfügen der Wiedergabeinformationen (jetzt auch mit "playlist_length")
        self.local.cursor.execute('''
        INSERT INTO playback (current_song, mfile, folder, pos, elapsed, playlist_length, mstatus, time_played)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(folder) DO UPDATE SET
            current_song=excluded.current_song,
            mfile=excluded.mfile,
            folder=excluded.folder,
            pos=excluded.pos,
            elapsed=excluded.elapsed,
            playlist_length=excluded.playlist_length,
            mstatus=excluded.mstatus,
            time_played=excluded.time_played''', (json.dumps(current_song), mfile, mfolder, pos, elapsed, playlist_length, json.dumps(status), time.strftime('%Y-%m-%d %H:%M:%S')))
        self.local.conn.commit()


    def get_playback_info(self, folder):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.create_connection()

        self.local.cursor.execute('SELECT pos, elapsed FROM playback WHERE folder = ? AND playlist_length > 0;', (folder ,))
        result = self.local.cursor.fetchone()
        return result if result else (0, 0)



    def get_folder_info(self, folder):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.create_connection()

        self.local.cursor.execute('SELECT round( AVG(1.0 * pos / playlist_length) *100,1) FROM playback WHERE folder LIKE ? AND playlist_length > 0;', (folder + '%',))
        result = self.local.cursor.fetchone()
        return result[0] if result[0] is not None  else 0

    def get_latest_folder(self, folder="",mfile=None):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.create_connection()

        if mfile:sql = "select file from playback Where file LIKE '%s' || '%%' ORDER BY time_played DESC LIMIT 1;" % (mfile)
        else: sql = "select folder from playback Where folder LIKE '%s' || '%%' ORDER BY time_played DESC LIMIT 1;" %(folder)
        try:
            self.local.cursor.execute(sql)
            result = self.local.cursor.fetchone()
            return result[0] if result[0] is not None  else folder
        except Exception as error:
            return mfile if mfile else folder


    def get_radio_stations(self):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        self.create_connection()

        self.local.cursor.execute('SELECT id, station_name, station_url FROM radiostations ORDER BY id ASC;')
        result = self.local.cursor.fetchall()
        return result if result else (0, 'N/A', 'N/A')


    def get_station_id_name_from_url(self,url):
        """Gibt die pos und elapsed für das angegebene folder zurück."""
        try:
            self.create_connection()
            sql = "SELECT id, station_name FROM radiostations WHERE station_url = '%s' ORDER BY id ASC;" % (url)
            self.local.cursor.execute(sql)
            result = self.local.cursor.fetchone()
            return result if result else (-1, 'N/A')
        except Exception as error:
            return (-1, 'N/A')



    def update_radiostations(self,stations):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""
        self.create_connection()

        # Einfügen der Wiedergabeinformationen (jetzt auch mit "playlist_length")
        sql = ('''
        INSERT INTO radiostations (station_name, station_url, station_uuid)
        VALUES (?, ?, ?)
        ON CONFLICT(station_uuid) DO UPDATE SET
            station_name = excluded.station_name,
            station_url = excluded.station_url
        ''')
        self.local.cursor.executemany(sql, stations)
        self.local.conn.commit()

    def delete_radiostations(self):
        """Speichert Wiedergabeinformationen in der Datenbank, einschließlich Dateipfad."""
        self.create_connection()

        self.local.cursor.execute("DELETE FROM radiostations")
        self.local.cursor.execute("DELETE FROM sqlite_sequence WHERE name='radiostations'")  # Reset der ID
        self.local.conn.commit()


    def load_user_settings(self):
        """Lädt alle Einstellungen aus der Datenbank und setzt sie als Attribute."""
        self.create_connection()

        self.local.cursor.execute("SELECT setting_key, setting_value FROM settings")
        settings = self.local.cursor.fetchall()
        return [(key, json.loads(value)) for key, value in settings]  # JSON zurück in Python-Typen umwandeln

    def save_user_setting(self, key, value):
        """Speichert oder aktualisiert eine Einstellung in der DB."""
        self.create_connection()

        json_value = json.dumps(value)  # Konvertiert in JSON

        self.local.cursor.execute("""
        INSERT OR REPLACE INTO settings (setting_key, setting_value)
        VALUES (?, ?)
        """, (key, json_value))
        self.local.conn.commit()

    def close_connection(self):
        """Schließt die Verbindung für diesen Thread."""
        if hasattr(self.local, "conn"):
            self.local.conn.close()
            del self.local.conn
            del self.local.cursor

    def __del__(self):
        self.close_connection()
        