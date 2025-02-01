#funktionen für download.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote, unquote
import os
import settings


from integrations.webrequest import WebRequest

from integrations.logging_config import *

import integrations.playout as playout

logger = setup_logger(__name__)


def check_url_reachability(url):
    try:
        logger.debug(f"Check URL: {url}")
        # Timeout auf 5 Sekunden setzen, um nicht zu lange zu warten
        response = WebRequest(url)
        # Rückgabewert: Statuscode der Anfrage
        return response.get_response_code()
    except Exception as e:
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


def construct_url(cwd, base_url,is_folder=True):
    # cwd kodieren und an die URL anhängen
    if is_folder and not base_url.endswith('/'): base_url += '/'
    encoded_cwd = quote(cwd)
    logger.debug(f"construct_url: base_url: {base_url}, cwd: {cwd}")
    return urljoin(base_url, encoded_cwd)

def get_unquoted_uri(url):
    parsed_url = urlparse(url)
    return unquote(parsed_url.path)

def stripitem(rawitem):
    stripitem = rawitem.rstrip('\u2302').strip()
    logger.debug(f"stripitem: raw:{rawitem}, strip: {stripitem}")
    return stripitem


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
    folderconf = os.environ.copy()
    if latestplayed[0] == "POS":
        folderconf["CURRENTFILENAME"] = "%s%s" % (latestplayed[5],latestplayed[1])
        folderconf["ELAPSED"] = latestplayed[2]
    print (directory)
    playout.pc_enableresume(directory,env=folderconf)



def get_current_directory(path):
    cur_dir = os.path.basename(os.path.normpath(path))
    logger.debug(f"aktueller Verzeichnisname von {path} ist {cur_dir}")
    return cur_dir

def get_relative_path(base_path, absolute_path):
    rel_path = os.path.relpath(absolute_path, start=base_path)
    logger.debug(f"relpath of abspath {absolute_path}is {rel_path}")
    return rel_path

def uri_exists_locally(url, base_url, base_path):
    parsed_url = urlparse(url)
    uri_path = unquote(parsed_url.path)
    logger.debug(f"check {url} in {base_path}")

    # Entferne den Basis-Pfad von der URI
    base_path_from_url = urlparse(base_url).path
    if uri_path.startswith(base_path_from_url):
        uri_path = uri_path[len(base_path_from_url):]

    # Erstelle den lokalen Pfad mit dem Basis-Pfad
    local_path = os.path.join(base_path, uri_path.lstrip('/'))
    logger.debug(f"local path: {local_path}")
    
    return os.path.exists(local_path)


def directories_to_list(directories):
    return [[directory] for directory in directories]

def get_first_or_self(selected_item):

    if isinstance(selected_item, list):
        logger.debug(f"get_first_or_self: list {selected_item}")
        return selected_item[0] if selected_item else ""  # Gibt das erste Feld zurück, wenn Liste nicht leer
    else:
        logger.debug(f"get_first_or_self: string {selected_item}")
        return selected_item

def find_element_or_formatted_position(nested_list, element):
    formatted_element = f"{element} \u2302"  # Erstelle den formatierten String
    logger.debug(f"Suche nach {element} oder {formatted_element}")
    for outer_index, inner_list in enumerate(nested_list):
        if element in inner_list or formatted_element in inner_list:
            inner_index = inner_list.index(element) if element in inner_list else inner_list.index(formatted_element)
            logger.debug(f"gefunden in {outer_index}, {inner_index}")
            return outer_index, inner_index
    logger.debug(f"nicht gefunden")

    return -1, -1  # Element nicht gefunden

def parse_size(size_str):
    """Konvertiert einen String wie '1.2 MB' oder '300 KB' in Bytes."""
    size_str = size_str.strip().upper()
    size_units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3,
                  'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3}
    
    # Extrahiere die Zahl und die Einheit aus dem String
    number = ''.join(filter(lambda x: x.isdigit() or x in {'.', ','}, size_str))  # Nimmt nur Ziffern, '.' und ',' für Dezimalzahlen
    unit = ''.join(filter(str.isalpha, size_str))  # Nimmt nur alphabetische Zeichen (die Einheit)

    # Fallback auf Bytes, wenn keine Einheit angegeben ist
    if not unit:
        unit = 'B'

    # Ersetze das Komma durch einen Punkt für die Umwandlung in float
    number = number.replace(',', '.')  

    # Konvertiere die Zahl in float (für Größen wie 1.5 MB)
    try:
        number = float(number)
    except ValueError:
        return 0

    # Konvertiere basierend auf der Einheit
    if unit in size_units:
        return int(number * size_units[unit])
    else:
        return 0