#funktionen für download.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote
import os
import settings

from integrations.logging_config import *

logger = setup_logger(__name__)



def check_url_reachability(url):
    try:
        logger.debug(f"Check URL: {url}")
        # Timeout auf 5 Sekunden setzen, um nicht zu lange zu warten
        response = requests.get(url, timeout=5)
        # Rückgabewert: Statuscode der Anfrage
        return response.status_code
    except requests.exceptions.RequestException as e:
        # Falls ein Fehler auftritt (z.B. URL nicht erreichbar), Rückgabe 0
        logger.warning(f"Fehler beim Erreichen der URL: {e}")
        return 0


def split_url(url):
    parsed_url = urlparse(url)

    # Wert 1: Schema und Host (inkl. Port, falls vorhanden)
    schema_and_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Wert 2: URI (Pfad und Query-Parameter, falls vorhanden)
    uri = parsed_url.path + ('?' + parsed_url.query if parsed_url.query else '')

    return schema_and_host, unquote(uri)

def get_files_and_dirs_from_listing(url, allowed_extensions,get_filesize=True):
    """Extrahiere Dateien und Verzeichnisse aus dem HTTP-Listing."""
    try:
        logger.debug(f"Verzeichnis-URL: {url}")
        if not url.endswith('/'): url += '/'
        parsed_url = urlparse(url)

        # Zertifikatsprüfung nur bei HTTPS-URLs deaktivieren
        if parsed_url.scheme == 'https':
            response = requests.get(url, verify=False)
        else:
            response = requests.get(url)  # Keine Zertifikatsprüfung für HTTP

        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Fehler bei der HTTP-Anfrage abfangen
        logger.info(f"Error fetching {url}: {e}")
        return [], [], 0

    soup = BeautifulSoup(response.text, 'html.parser')

    files = []
    directories = []
    total_size = 0

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('?') and not href.startswith('/'):
            if href.endswith('/'):
                # Unterverzeichnis gefunden
                directories.append(unquote(href).strip('/')) # trailing slash entfernen
            elif any(href.endswith(ext) for ext in allowed_extensions):
                # Datei gefunden
                files.append(unquote(href))

                #Wenn Dateigröße abgefragt werden soll
                if get_filesize:
                    file_url = urljoin(url, href)
                    try:
                        file_response = requests.head(file_url)
                        file_response.raise_for_status()
                        # Dateigröße aus dem Header holen, falls vorhanden
                        file_size = int(file_response.headers.get('content-length', 0))
                        total_size += file_size
                    except requests.RequestException as e:
                        logger.info(f"Fehler beim Abrufen der Dateigröße für {file_url}: {e}")
                        continue
    return files, directories, total_size

def construct_url(cwd, base_url):
    # cwd kodieren und an die URL anhängen
    encoded_cwd = quote(cwd)
    return urljoin(base_url, encoded_cwd)

def get_unquoted_uri(url):
    parsed_url = urlparse(url)
    return unquote(parsed_url.path)

def stripitem(rawitem):
    return rawitem.rstrip('\u2302').rstrip()


def construct_url_from_local_path(base_url, local_path, filename=""):
    encoded_path = quote(local_path)
    encoded_filename = quote(stripitem(filename))
    full_path = urljoin(base_url, encoded_path)
    if not full_path.endswith('/'): full_path += '/'
    return urljoin(full_path, encoded_filename)

def get_parent_directory_of_url(url):
    parsed_url = urlparse(url)
    logger.debug(f"get_parent_directory: {url}")
    try:
        # Entferne den letzten Teil des Pfads, um den übergeordneten Ordner zu bekommen
        parent_path = '/'.join(parsed_url.path.rstrip('/').split('/')[:-1]) + '/'
        return urljoin(url, parent_path)
    except:
        logger.error(f"url parse error: {url}")
        return url

def get_parent_directory(path):
    logger.debug(f"parent directory of {path}")
    # Entferne das letzte Slash, falls vorhanden
    if path.endswith('/'):
        path = path.rstrip('/')
    parent_path = os.path.dirname(path)
    logger.debug(f"parent directory is {parent_path}")
    return  parent_path

def create_or_modify_folder_conf(directory,latestplayed):
    filename = os.path.join(directory,"folder.conf")
    folderconf = {}
    folderconf["CURRENTFILENAME"] = ""
    folderconf["ELAPSED"] = "ON"
    folderconf["PLAYSTATUS"] = "Playing"
    folderconf["SHUFFLE"] = "OFF"
    folderconf["RESUME"] = "ON"
    folderconf["LOOP"] = "OFF"
    folderconf["SINGLE"] = "OFF"

    try:
        folder_conf_file = open(filename,"r")
        lines = folder_conf_file.readlines()
        for line in lines:
            _key, _val = line.split('=',2)
            folderconf[_key] = _val.replace("\"","").strip()
    except Exception as error:
            logger.error (f"folder_conf: {error}")
            return

    if latestplayed[0] == "POS":
        folderconf["CURRENTFILENAME"] = "%s%s" % (latestplayed[5],latestplayed[1])
        folderconf["ELAPSED"] = latestplayed[2]
    logger.info (filename)

    try:
        with open(filename,"w") as folder_conf_file:
            for key in folderconf:
                folder_conf_file.write ("%s=\"%s\"\n" % (key,folderconf[key]))
    except Exception as error:
        logger.error (error)

def get_current_directory(path):
    cur_dir = os.path.basename(os.path.normpath(path))
    logger.debug(f"aktueller Verzeichnisname von {path} ist {cur_dir}")
    return cur_dir

def get_relative_path(base_path, absolute_path):
    rel_path = os.path.relpath(absolute_path, start=base_path)
    logger.debug(f"relpath of abspath {absolute_path}is {rel_path}")
    return rel_path