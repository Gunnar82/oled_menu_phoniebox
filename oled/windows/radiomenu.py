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

    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop, "Auswahl")
        #self.timeoutwindow="folderinfo"
        self.timeout = False
        self.loop = loop
        self.busysymbol = symbols.SYMBOL_CLOUD

    def activate(self):
        if not csettings.UPDATE_RADIO:
            self.set_busyinfo("Radio Update deaktiviert",wait=5)
        else:
            self.set_window_busy()
            #Stationen Online auslesen
            stations = self.get_online_stations()
            logger.debug(f"activate stations :{stations}")
 
            #Stationen in lokales Dateisystem schreiben
            for station in stations:
                self.create_local_station(station['name'], station['url'])

            self.set_window_busy(False,wait=4)

        #Nach Abschluss zu Radio wechseln
        self.windowmanager.set_window("foldermenu")

    def create_local_station(self,folder,url):
        try:
            self.append_busytext(f"Erstelle: {folder}")

            foldername = os.path.join(cfg_file_folder.AUDIO_BASEPATH_RADIO,folder)
            logger.debug(f"Radio path: {foldername}")
            try:
                if not os.path.exists(foldername): os.makedirs(foldername)
            except Exception as error:
                self.append_busyerror(error)
                logger.error(f"radiomenu: error {error}")

            livestream = os.path.join(foldername,"livestream.txt")
            logger.debug(f"creating file {livestream}")
            with open(livestream,"w") as fname:
                fname.write(url)
        except Exception as error:
            self.append_busyerror(error)

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
            logger.debug(f"station {url}, {name}")
            # Füge das Ergebnis als Dictionary in die Liste ein
            stations_list.append({'name': name, 'url': url})

        return stations_list