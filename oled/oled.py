#!/usr/bin/python3
"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import os,shutil
import time
import importlib
from subprocess import call
import argparse

# Funktion zum Argumente parsen
def parse_arguments():
    parser = argparse.ArgumentParser(description="Starte das Programm mit benutzerdefiniertem Log-Level.")
    parser.add_argument('--loglevel-debug', type=str, nargs='*', help='Setze den Debug-Level für bestimmte Module')
    return parser.parse_args()

# Argumente parsen
args = parse_arguments()


from integrations.logging_config import *
from integrations.functions import run_as_service

# Debug-Module global setzen
if args.loglevel_debug:
    configure_debug_modules(args.loglevel_debug)


logger = setup_logger(__name__)


###checke user_settings
def check_or_create_config(filename,samplename):
    try:

        if not os.path.exists(filename):
            logger.info(f"{filename} existiert nicht. Erstelle aus der Vorlage.")
            # Prüfe, ob die Vorlage existiert
            if os.path.exists(samplename):
                # Kopiere die Vorlage in USER_SETTINGS
                shutil.copy(samplename, filename)
                logger.info(f"{filename} wurde aus {samplename} erstellt.")
            else:
                logger.error(f"Vorlage {samplename} existiert nicht.")
    except Exception as error:
       logger.error(f"usersettings Fehler: {filename}: {error}")
       sys.exit (-1)

settings_py = "/home/pi/oledctrl/oled/settings.py"
settings_py_sample = f"{settings_py}.sample"

file_folder_py = "/home/pi/oledctrl/oled/config/file_folder.py"
file_folder_py_sample = f"{file_folder_py}.sample"


online_py = "/home/pi/oledctrl/oled/config/online.py"
online_py_sample = f"{online_py}.sample"

keypad_4x4_i2c_cfg = "/home/pi/oledctrl/oled/config/keypad_4x4_i2c.py"
keypad_4x4_i2c_cfg_sample = f"{keypad_4x4_i2c_cfg}.sample"


mcp_23017_keys_cfg = "/home/pi/oledctrl/oled/config/mcp_23017_keys.py"
mcp_23017_keys_cfg_sample = f"{mcp_23017_keys_cfg}.sample"


mcp_23017_leds_cfg = "/home/pi/oledctrl/oled/config/mcp_23017_leds.py"
mcp_23017_leds_cfg_sample = f"{mcp_23017_leds_cfg}.sample"

statusled_cfg = "/home/pi/oledctrl/oled/config/statusled.py"
statusled_cfg_sample = f"{statusled_cfg}.sample"

rotary_enc_cfg = "/home/pi/oledctrl/oled/config/rotary_enc.py"
rotary_enc_cfg_sample = f"{rotary_enc_cfg}.sample"

check_or_create_config(file_folder_py,file_folder_py_sample)
check_or_create_config(settings_py,settings_py_sample)
check_or_create_config(online_py,online_py_sample)


import settings

import config.user_settings
import config.file_folder as cfg_file_folder
import integrations.functions as fn
import integrations.playout as playout
import config.shutdown_reason as SR


######
from datetime import datetime
###########################
settings.screenpower = True
settings.shutdown_reason = "changeme"
fn.set_lastinput()
settings.job_t = -1
settings.job_i = -1
settings.job_s = -1
settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_MUSIC
settings.currentfolder = settings.audio_basepath
settings.current_selectedfolder=settings.currentfolder
settings.battcapacity = -1
settings.battloading = False
settings.callback_active = False



displays = ["st7789", "ssd1351", "sh1106_i2c", "sh1106_i2c", "emulated","gpicase","gpicase2"]

if not settings.DISPLAY_DRIVER in displays:
    raise Exception("no DISPLAY")

try:
    lib = "integrations.display.%s" % (settings.DISPLAY_DRIVER)
    logger.info(f"Display: {lib}")
    idisplay = importlib.import_module(lib)
    idisplay.set_fonts()
except Exception as error:
    raise Exception(f"DISPLAY init FAILED: {error}")  # Exception verbessern


from integrations.mopidy import MopidyControl
from integrations.musicmanager import Musicmanager
import integrations.sqlite as msqlite
from ui.windowmanager import WindowManager
import windows.idle
import windows.info
import windows.headphone
import windows.mainmenu
import windows.playbackmenu
import windows.playlistmenu
import windows.foldermenu
import windows.shutdownmenu
import windows.folderinfo
import windows.radiomenu
import windows.start
import windows.ende
import windows.getvalue
import windows.download as wdownload
import windows.lock as wlock
import windows.system as wsystem
import windows.snake as wsnake

import integrations.bluetooth
import windows.bluetooth




#Systemd exit
def handle_signal(loop, signal_name):
    print(f"{signal_name} empfangen, beende...")

    loop.stop()
    sys.exit(0)

#signal.signal(signal.SIGTERM, gracefulexit)

def main():
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, handle_signal, loop,"SIGINT")
    loop.add_signal_handler(signal.SIGTERM, handle_signal, loop,"SIGTERM")

    #SQLite Verbindung herstellen
    sqlite = msqlite.sqliteDB()

    #Usersettings DB
    usersettings = config.user_settings.UserSettings(sqlite)

    try:
        bluetooth_enabled = False

        if usersettings.BLUETOOTH_ENABLED:
            bluetooth_enabled = True
            mybluetooth = integrations.bluetooth.BluetoothOutput(usersettings)
            logger.info ("Bluetooth gestartet")
        else:
            mybluetooth = None

    except Exception as error:
        print (error)
        bluetooth_enabled = False
        mybluetooth = None

        logger.error(f"Bluetooth: {error}")


    #shutdown reason default
    settings.shutdown_reason = SR.SR1

    #Display = real hardware or emulator (depending on settings)
    display = idisplay.get_display()

    #screen = windowmanager
    windowmanager = WindowManager(loop, display,usersettings)

    #Software integrations
    mopidy = MopidyControl(loop)
    #def airplay_callback(info, nowplaying):
    #    musicmanager.airplay_callback(info, nowplaying)
    #shairport = ShairportMetadata(airplay_callback)
    musicmanager = Musicmanager(mopidy,sqlite)

    ###processing nowplaying
    import integrations.nowplaying as nowplaying

    _nowplaying = nowplaying.nowplaying(loop,musicmanager,windowmanager,mybluetooth,usersettings)

    #callback_setup
    def turn_callback(direction,_key=False):
        windowmanager.turn_callback(direction, key=_key)

    def push_callback(_lp=False):
        windowmanager.push_callback(lp=_lp)


    ###GPICase
    if "gpicase" in settings.INPUTS:
        from integrations.inputs.gpicase import pygameInput

        print ("Using pyGameInput")
        mypygame = pygameInput(loop, turn_callback, push_callback,windowmanager,_nowplaying)

    #Import all window classes and generate objects of them
    loadedwins = []


    loadedwins.append(windows.start.Start(windowmanager, loop, usersettings, mopidy,mybluetooth))
    loadedwins.append(windows.idle.Idle(windowmanager, loop, usersettings, _nowplaying,musicmanager))
    loadedwins.append(windows.playbackmenu.Playbackmenu(windowmanager, loop, usersettings, _nowplaying,musicmanager))
    loadedwins.append(windows.mainmenu.Mainmenu(windowmanager,loop, usersettings,"Hauptmenü",musicmanager))
    loadedwins.append(windows.info.Infomenu(windowmanager,loop, usersettings,))
    if bluetooth_enabled: loadedwins.append(windows.headphone.Headphonemenu(windowmanager,loop, usersettings,mybluetooth,"Audioausgabe"))
    if bluetooth_enabled: loadedwins.append(windows.bluetooth.Bluetoothmenu(windowmanager,loop, usersettings,mybluetooth,"Bluetoothmenu"))
    loadedwins.append(windows.playlistmenu.Playlistmenu(windowmanager, loop, usersettings, musicmanager))
    loadedwins.append(windows.foldermenu.Foldermenu(windowmanager,loop, usersettings, musicmanager))
    loadedwins.append(windows.radiomenu.Radiomenu(windowmanager,loop, usersettings,musicmanager))
    loadedwins.append(windows.folderinfo.FolderInfo(windowmanager, loop, usersettings,))
    loadedwins.append(windows.getvalue.GetValue(windowmanager, loop, usersettings,))
    loadedwins.append(windows.ende.Ende(windowmanager, loop, usersettings,_nowplaying,musicmanager))
    loadedwins.append(windows.shutdownmenu.Shutdownmenu(windowmanager, loop, usersettings, musicmanager,_nowplaying,"Powermenü"))
    loadedwins.append(wdownload.DownloadMenu(windowmanager,loop, usersettings,musicmanager))
    loadedwins.append(wsnake.SnakeGame(windowmanager,loop, usersettings,))
    loadedwins.append(wlock.Lock(windowmanager,loop, usersettings,_nowplaying,musicmanager))
    loadedwins.append(wsystem.SystemMenu(windowmanager,loop, usersettings,"Systemeinstellungen",musicmanager))
    for window in loadedwins:
        windowmanager.add_window(window.__class__.__name__.lower(), window)

    #Load start window
    windowmanager.set_window("start")


    #init Inputs


    ####keyboard control
    if "keyboard" in settings.INPUTS:
        from integrations.inputs.keyboard import KeyboardCtrl

        mKeyboard = KeyboardCtrl(loop, turn_callback, push_callback)

    ### KEYPAD 4x4 MCP23017 I2C

    if "keypad4x4" in settings.INPUTS:
        check_or_create_config(keypad_4x4_i2c_cfg,keypad_4x4_i2c_cfg_sample)
        import config.keypad_4x4_i2c as keypad_4x4_i2c_config

        from integrations.inputs.keypad_4x4_i2c import keypad_4x4_i2c

        mKeypad = keypad_4x4_i2c(loop, keypad_4x4_i2c_config.KEYPAD_ADDR, keypad_4x4_i2c_config.KEYPAD_INTPIN, turn_callback, push_callback)



    if "mcp_23017_keys" in settings.INPUTS:
        check_or_create_config(mcp_23017_keys_cfg,mcp_23017_keys_cfg_sample)
        import config.mcp_23017_keys as mcp_23017_keys_config

        from integrations.inputs.mcp_23017_keys import mcp_23017_keys

        mMCPKeys = mcp_23017_keys(loop, turn_callback, push_callback, mcp_23017_keys_config)


    ###Rotaryencoder Setup
    if "rotaryenc" in settings.INPUTS:
        check_or_create_config(rotary_enc_cfg,rotary_enc_cfg_sample)
        import config.rotary_enc as rotary_enc_config

        from integrations.inputs.rotaryencoder import RotaryEncoder

        print ("Rotaryconctroller")
        rc = RotaryEncoder(loop, turn_callback, push_callback,clk=rotary_enc_config.PIN_CLK,dt=rotary_enc_config.PIN_DT,sw=rotary_enc_config.PIN_SW)


    ####Powercontroller Init
    haspowercontroller = False
    if "powercontroller" in settings.INPUTS:
        from integrations.inputs.powercontroller import PowerController

        haspowercontroller = True
        try:
            print ("Poweronctroller")
            pc = PowerController(loop, turn_callback, push_callback)
            haspowercontroller = False
        except:
            haspowercontroller = False
            logger.error(f"Power controller init failed: {e}")  # Fehlerbehandlung verbessern

    #### pirateaudio init
    if "pirateaudio" in settings.INPUTS:
        from integrations.inputs.pirateaudio import PirateAudio
        pirateaudio = PirateAudio(loop, turn_callback, push_callback)

# end init inputs



    if "mcp_23017_leds" in settings.OUTPUTS:
        check_or_create_config(mcp_23017_leds_cfg,mcp_23017_leds_cfg_sample)
        import config.mcp_23017_leds as mcp_23017_leds_config

        from integrations.outputs.mcp_23017_leds import mcp_23017_leds

        mMCPLeds = mcp_23017_leds(loop, mcp_23017_keys_config)



    ######Status LED
    if "statusled" in settings.OUTPUTS:
        check_or_create_config(statusled_cfg,statusled_cfg_sample)

        import config.statusled as statusled_config

        import integrations.outputs.statusled as statusled

        led = statusled.statusled(loop,usersettings,musicmanager,pin=statusled_config.STATUS_LED_PIN,always_on=statusled_config.STATUS_LED_ALWAYS_ON)
    else:
        led = None

    ####x728V2.1
    if "x728" in settings.INPUTS:
        import integrations.x728v21 as x728v21
        x728 = x728v21.x728(loop,windowmanager,led,usersettings)


    ###main
    try:
        loop.run_forever()
        mopidy.stop()
    except (KeyboardInterrupt, SystemExit):
        logger.error("main Loop exiting")
        loop.stop()
    finally:
        loop.close()


    ####x728 Cleanup
    if "x728" in settings.INPUTS:
        print ("shutdown x728")
        x728.shutdown()

    ###GPICase
    if "gpicase" in settings.INPUTS:
        mypygame.quit()

    if run_as_service():

        if settings.shutdown_reason in [SR.SR2, SR.SR5]:
            if haspowercontroller:
                if pc.ready:
                    pc.shutdown()

            logger.error(f"Shutting down system: {settings.shutdown_reason}")
            silent=True if settings.shutdown_reason == SR.SR5 else False
            playout.pc_shutdown(silent)

        elif settings.shutdown_reason == SR.SR3:
            playout.pc_reboot()
    else:
        logger.error (f"nicht als Dienst gestartet - nur beenden, eigentlich: {settings.shutdown_reason}")


if __name__ == '__main__':
    main()
    if "rotaryenc" in settings.INPUTS:
        RotaryEncoder.cleanup()
    sys.exit(0)
