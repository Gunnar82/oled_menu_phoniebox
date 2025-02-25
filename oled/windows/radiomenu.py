""" Playlist menu """
from ui.listbase import ListBase
import settings

import config.colors as colors
import config.symbols as symbols

import os 
import integrations.functions as functions
import integrations.playout as playout
from integrations.webrequest import WebRequest
import xml.etree.ElementTree as ET
import time

import config.file_folder as cfg_file_folder
import config.online as cfg_online
import config.user_settings as csettings

from integrations.logging_config import *

logger = setup_logger(__name__)


class Radiomenu(ListBase):

    def __init__(self, windowmanager,loop,musicmanager):
        super().__init__(windowmanager, loop, "Auswahl")
        #self.timeoutwindow="folderinfo"
        self.musicmanager = musicmanager
        self.timeout = False
        self.loop = loop
        self.busysymbol = symbols.SYMBOL_CLOUD

    def activate(self):
        if not csettings.UPDATE_RADIO:
            self.set_busyinfo("Radio Update deaktiviert",wait=5)
        else:
            try:
                self.set_window_busy()
                #Stationen Online auslesen
                self.append_busytext("Online Stationen auslesen...")
                stations = self.get_online_stations()
                logger.debug(f"activate stations :{stations}")
                self.append_busytext("Stationen in Datenbank schreiben...") 
                #Stationen in lokales Dateisystem schreiben
                self.musicmanager.update_radiostations(stations)
                self.append_busytext("Abgeschlossen...")
            except Exception as error:
                self.append_busyerror(f"Fehler: {error}")
            finally:
                self.set_window_busy(False,wait=4)

        #Nach Abschluss zu Radio wechseln
        try:
            self.menu = []
            for station in self.musicmanager.get_radio_stations():
                self.menu.append([station[1],"e","",station[2]])
        except Exception as error:
            print (error)


    def push_handler(self):
        set_window = True
        try:
            self.set_window_busy()

            if self.position  == -2:
                settings.currentfolder = settings.audio_basepath
                self.windowmanager.set_window("mainmenu")
            elif self.position == -1:
                self.append_busytext("Eine Ebene höher...")
                set_window = False
                self.on_key_left()
            else:
                self.append_busytext("Starte...")
                self.append_busytext(self.menu[self.position][0])
                url = self.menu[self.position][3]
                self.musicmanager.playliststart([url])

        except Exception as error:
            logger.debug(f"{error}")
            self.append_busyerror(error)
        finally:
            self.set_window_busy(False)


    def get_online_stations(self):
        try:
            url = "%sradio.php" % (cfg_online.ONLINE_SAVEPOS)
            logger.debug(f"Radio-URL: {url}")
    
            # Zertifikatsprüfung nur bei HTTPS-URLs deaktivieren
            response = WebRequest(url)
        except Exception as e:
            # Fehler bei der HTTP-Anfrage abfangen
            logger.info(f"Error fetching {url}: {e}")
            return []

        return self.parse_stations(response.get_response_text())

    def parse_stations(self,xml_data):
        # Erstelle eine leere Liste für die Ergebnisse
        stations_list = []

        # Parsen der XML-Daten
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            logger.info(f"Fehler beim Parsen der XML-Daten: {e}")
            return [], []

        # Iteriere über alle 'station'-Elemente im XML
        for station in root.findall('station'):
            # Extrahiere 'name' und 'url' aus jedem 'station'-Element
            name = station.find('name').text if station.find('name') is not None else 'Unbekannt'
            url = station.find('url').text if station.find('url') is not None else 'Unbekannt'
            stationuuid = station.find('stationuuid').text if station.find('stationuuid') is not None else 'Unbekannt'

            logger.debug(f"station {url}, {name}, {stationuuid}")
            # Füge das Ergebnis als Dictionary in die Liste ein
            stations_list.append((name, url,stationuuid))

        return stations_list