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

from integrations.logging_config import *

logger = setup_logger(__name__)


class Radiomenu(ListBase):

    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager, loop, "Auswahl")
        #self.timeoutwindow="folderinfo"
        self.timeout = False
        self.loop = loop


    def activate(self):
        stations = self.get_online_stations()
        logger.debug(f"activate stations :{stations}") 
        self.menu = []
        for station in stations: self.menu.append([station['name'], station['url']])


    def playfolder(self,folder):
        try:
            self.set_window_busy()
            selected_element = self.menu[self.position]

            foldername = os.path.join(cfg_file_folder.AUDIO_BASEPATH_RADIO,selected_element[0])
            logger.debug(f"Radio path: {foldername}")
            try:
                if not os.path.exists(foldername): os.makedirs(foldername)
            except Exception as error:
                self.append_busyerror(error)
                logger.error(f"radiomenu: error {error}")

            self.append_busytext("Abspielen:")
            self.append_busytext(selected_element[0])
            livestream = os.path.join(foldername,"livestream.txt")
            logger.debug(f"creating file {livestream}")
            with open(livestream,"w") as fname:
                fname.write(selected_element[1])

            basename = foldername[len(cfg_file_folder.AUDIO_BASEPATH_BASE):]
            logger.debug(f"stripped folder: {basename}")
            playout.pc_playfolder(basename)
            self.windowmanager.set_window("idle")
        except Exception as error:
            self.append_busyerror(error)
        finally:
            self.set_window_busy(False)


    def push_handler(self):
        set_window = True
        try:

            self.set_window_busy()

            """if self.position  == -2:
                settings.currentfolder = settings.audio_basepath
                self.windowmanager.set_window("mainmenu")
            elif self.position == -1:
                self.append_busytext("Eine Ebene höher...")
                set_window = False
                self.on_key_left()
            else:"""
            if self.position >= 0:
                #folder = self.folders[self.position-1]
                #fullpath = os.path.join(settings.currentfolder,folder)
                #settings.currentfolder = fullpath
                self.append_busytext("Auswahl...")
                thefile = os.listdir(settings.current_selectedfolder)
                self.loop.run_in_executor(None,self.playfolder,settings.current_selectedfolder)
        except Exception as error:
            self.append_busyerror(error)
        finally:
            if set_window: self.set_window_busy(False,wait=5)

            #self.mopidyconnection.loadplaylist(self.mopidyconnection.playlists[self.counter-1])
            #self.windowmanager.set_window("idle")


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