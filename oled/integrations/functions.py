import os
import subprocess, re
import datetime
import settings
import time


from integrations.logging_config import *

logger = setup_logger(__name__)

import config.colors as colors
import config.symbols as symbols
import config.file_folder as cfg_file_folder
import config.services as cfg_services

def get_parent_folder(folder):
    return os.path.dirname(folder)

def has_subfolders(path):
    for file in os.listdir(path):
        d = os.path.join(path, file)
        if os.path.isdir(d):
            return True
    return False


def to_min_sec(seconds):
        mins = int(float(seconds) // 60)
        secs = int(float(seconds) - (mins*60))
        if mins >=60:
            hours = int(float(mins) // 60)
            mins = int(float(mins) - (hours*60))
            return "%d:%2.2d:%2.2d" % (hours,mins,secs)
        else:
            return "%2.2d:%2.2d" % (mins,secs)

def remove_folder_symbol(item):
    return item.lstrip(symbols.SYMBOL_FOLDER).lstrip()


def get_file_content(filepath):
    try:
        # Versuche, die Datei zu öffnen und ihren Inhalt zu lesen
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        # Falls ein Fehler auftritt (z.B. Datei nicht gefunden), gib einen leeren String zurück
        return ""

def get_folder_of_livestream(url):
    basefolder = cfg_file_folder.AUDIO_BASEPATH_RADIO

    for folder in os.listdir(basefolder):
        d = os.path.join(basefolder, folder)
        if os.path.isdir(d):
           filename = os.path.join(d,'livestream.txt')
           try:
               with open(filename, 'r') as file:
                    data = file.read().replace('\n', '')
               if data == url:
                   return d
           except:
               pass

    return "n/a"


def get_folder(folder,direction = 1):
    parent = get_parent_folder(folder)
    entrys = []
    for folders in os.listdir(parent):
        d = os.path.join(parent, folders)
        if os.path.isdir(d):
            entrys.append(d)
    entrys.sort()
    pos = entrys.index(folder)
    pos += direction

    if pos < 0:
        pos = 0
    if pos > len(entrys) -1:
        pos = len(entrys) -1
    rel_path = os.path.relpath(entrys[pos],cfg_file_folder.AUDIO_BASEPATH_BASE)
    return rel_path


def restart_oled():

    print ("restarting  service")

    run_command("sudo systemctl restart oled")


def get_usb_name():
    for file in os.listdir("/tmp/phoniebox"):
        if file.startswith("usb_"):
            return (file.split("_")[1])

def mountusb():
    usbdev=get_usb_name()
    if (usbdev == "n/a"):
        return -1

    if not os.path.ismount(cfg_file_folder.AUDIO_BASEPATH_USB):
        print (usbdev)
        run_command("unionfs-fuse -orw,cow,allow_other /media/pb_import/tmpfs/=rw:/media/pb_import/%s=ro %s" % (usbdev, cfg_file_folder.AUDIO_BASEPATH_USB))
        run_command("mpc update")
    else:
        print ("already mounted")

def umountusb():
    run_command("/home/pi/RPi-Jukebox-RFID/shared/audiofolders/usb/")

def get_folder_from_file(filename):
    try:
        with open (filename) as f:
            lines = f.readlines()
            f.close()
            if (lines[0].startswith("/")):
                path = cfg_file_folder.AUDIO_BASEPATH_BASE + lines[0].rstrip()
            else:
                path = cfg_file_folder.AUDIO_BASEPATH_BASE + "/" + lines[0].rstrip()
            return (path)
    except:
        return cfg_file_folder.AUDIO_BASEPATH_BASE


def get_battload_color():
    if settings.battloading:
        return colors.COLOR_BLUE
    elif settings.battcapacity == -1:
        return "WHITE"
    elif settings.battcapacity >= 70:
        return colors.COLOR_GREEN
    elif settings.battcapacity >= 40:
        return colors.COLOR_YELLOW
    elif settings.battcapacity >= settings.X728_BATT_LOW:
        return colors.COLOR_ORANGE
    else:
        return colors.COLOR_RED



def get_size(size):
    mb = ['B','kB','MB','GB','TB','PB']
    number = 0
    while size > 1024:
        number += 1
        size = size / 1024

    return "%.1f %s" % (size,mb[number])


def get_oledversion():
    version = "0"
    try:
        with open('/home/pi/oledctrl/build_number') as f:
            version = f.readline().strip()
    except Exception as error:
         print (error)
    return "v3-%s" % (version)



def run_command(commands, cwd="/home/pi/oledctrl/", results = None, env=None):
    """Führt einen Shell-Befehl aus und prüft die Ausgabe."""
    try:
        if isinstance(commands,str):
            logger.debug(f"running single command: {commands}")
            subprocess_result = subprocess.Popen(commands,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=cwd,encoding='utf-8',env=env)
            subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
            logger.debug(f"result: {subprocess_result.returncode}: {subprocess_output}")
            if results is not None:
                results.append([subprocess_result.returncode,str(subprocess_output)])
            return (subprocess_result.returncode == 0)

        elif isinstance(commands,list):
            for command in commands:
                logger.debug(f"running multiple commands: {commands}")

                subprocess_result = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd=cwd,encoding='utf-8',env=env)
                subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
                logger.debug(f"result: {subprocess_result.returncode}: {subprocess_output}")
                if results is not None:
                    results.append([subprocess_result.returncode,str(subprocess_output)])

                if subprocess_result.returncode != 0:
                    logger.debug(f"Returncode: {subprocess_result.returncode}, {command} failed")
                    return False
            return True

    except Exception as e:
        logger.exception(str(e))
        return False

def output_command(command, cwd="/home/pi/oledctrl/"):
    try:
        subprocess_result = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)
        subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
        decoded_output = subprocess_output[0].decode('utf-8')
        logger.debug(f"command output decoded: {decoded_output}")
        return decoded_output
    except Exception as e:
        logger.error(f"output_command: {e}")
        return "err"

def get_firewall_state():
    output = output_command("sudo ufw status numbered | grep '\[' | cut -d ']' -f 2")
    output = re.sub(' +',' ', output)
    output = output.replace("ALLOW IN"," allow")
    output = output.replace("DENY IN"," deny")
    output = output.replace("Anywhere","")
    logger.debug(f"firewall_state: {output}")
    return output

def enable_firewall():
    try:
        logger.info("enable firewall")
        run_command(["echo \"y\" | sudo ufw enable","sudo ufw default deny incoming","sudo ufw default allow outgoing"])
        for srv in cfg_services.ufw_services_allow:
            run_command(f"sudo ufw deny {srv}")
        return True

    except Exception as e:
        logger.error(e)
        return False

def disable_firewall():
    logger.info("disable firewall")
    for srv in cfg_services.ufw_services_allow:
        run_command(f"sudo ufw allow {srv}")


def lese_status(dateipfad):
    try:
        with open(dateipfad, 'r') as datei:
            inhalt = datei.read().strip()  # Lies den Inhalt und entferne führende/folgende Leerzeichen

            if inhalt == 'enabled':
                return True
            elif inhalt == 'disabled':
                return False
            else:
                raise ValueError("Datei enthält einen unerwarteten Wert: {}".format(inhalt))
    except FileNotFoundError:
        logger.error(f"Die Datei wurde nicht gefunden: {dateipfad}")
        return False
    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {e}")
        return False

def finde_zeile_nach_wert(dateipfad, suchwert):
    """
    Durchsucht eine Datei nach einem bestimmten Wert und gibt die Zeile zurück, die diesen Wert enthält.
    
    :param dateipfad: Pfad zur Datei, die durchsucht werden soll.
    :param suchwert: Der Wert, nach dem in der Datei gesucht wird.
    :return: Die Zeile, die den Suchwert enthält, oder None, wenn der Wert nicht gefunden wird.
    """
    try:
        with open(dateipfad, 'r') as datei:
            for zeile in datei:
                if suchwert in zeile:
                    return zeile.strip()  # Gibt die Zeile ohne führende und nachfolgende Leerzeichen zurück
        return None  # Gibt None zurück, wenn der Wert nicht gefunden wird
    except FileNotFoundError:
        logger.error(f"Die Datei '{dateipfad}' wurde nicht gefunden.")
    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {e}")


def get_hostapd_file_status():
    return lese_status('/home/pi/oledctrl/oled/config/hotspot')


def get_hostapd_ssid():
    return finde_zeile_nach_wert("/etc/hostapd/hostapd.conf","ssid")

def get_hostapd_psk():
    return finde_zeile_nach_wert("/etc/hostapd/hostapd.conf","wpa_passphrase")


def set_lastinput():
    settings.lastinput = time.monotonic()


def ping_test(host="8.8.8.8", wait=2): # default ip
    """Teste ob das Gerät online ist."""
    return run_command(f"ping -c1 -W {wait} {host}")


def run_as_service():
    """Prüft, ob das Progamm von systemd ausgeführt wird"""
    try:
        return 'INVOCATION_ID' in os.environ
    except:
        return False


def check_results_list(list_of_lists):
    return next((inner_list[1] for inner_list in list_of_lists if inner_list and inner_list[0] != 0), None)


def list_files_in_directory(directory):
    """Gibt eine Liste aller Dateien in einem Verzeichnis zurück."""
    if not os.path.isdir(directory):
        return []
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]