#!/usr/bin/python3
"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import os,shutil
import time
import importlib
from subprocess import call
import integrations.bluetooth
import integrations.functions as fn
import integrations.playout as playout

import settings

import config.file_folder as cfg_file_folder


from integrations.logging_config import *

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
       logger.error(f"usersettings Fehler: {error}")
       sys.exit (-1)

file_folder_py = "/home/pi/oledctrl/oled/config/file_folder.py"
file_folder_py_sample = f"{file_folder_py}.sample"


online_py = "/home/pi/oledctrl/oled/config/online.py"
online_py_sample = f"{online_py}.sample"

settings_py = "/home/pi/oledctrl/oled/settings.py"
settings_py_sample = f"{settings_py}.sample"

check_or_create_config(cfg_file_folder.FILE_USER_SETTINGS,cfg_file_folder.FILE_USER_SETTINGS_SAMPLE)
check_or_create_config(online_py,online_py_sample)
check_or_create_config(settings_py,settings_py_sample)
check_or_create_config(file_folder_py,file_folder_py_sample)



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
    print (lib)
    idisplay = importlib.import_module(lib)
    idisplay.set_fonts()
except Exception as error:
   raise ("DISPLAY init FAILED: %s" % (error))


from integrations.mopidy import MopidyControl
from integrations.musicmanager import Musicmanager
from ui.windowmanager import WindowManager
import windows.idle
import windows.info
import windows.headphone
import windows.bluetooth
import windows.mainmenu
import windows.playbackmenu
import windows.playlistmenu
import windows.foldermenu
import windows.shutdownmenu
import windows.folderinfo
import windows.start
import windows.ende
import windows.download as wdownload
import windows.lock as wlock
import windows.system as wsystem
import windows.snake as wsnake
import integrations.bluetooth as bluetooth

#Systemd exit
def gracefulexit(signum, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, gracefulexit)

def main():
    loop = asyncio.get_event_loop()


    objbluetooth = bluetooth.BluetoothOutput()


    #shutdown reason default
    settings.shutdown_reason = settings.SR1

    #Display = real hardware or emulator (depending on settings)
    display = idisplay.get_display()

    #screen = windowmanager
    windowmanager = WindowManager(loop, display)

    #Software integrations
    mopidy = MopidyControl(loop)
    #def airplay_callback(info, nowplaying):
    #    musicmanager.airplay_callback(info, nowplaying)
    #shairport = ShairportMetadata(airplay_callback)
    musicmanager = Musicmanager(mopidy)

    ###processing nowplaying
    import integrations.nowplaying as nowplaying

    _nowplaying = nowplaying.nowplaying(loop,musicmanager,windowmanager,objbluetooth)

    #Rotary encoder setup
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
    idlescreen = windows.idle.Idle(windowmanager, loop, _nowplaying)
    playbackm = windows.playbackmenu.Playbackmenu(windowmanager, loop, _nowplaying)
    shutdownscreen = windows.shutdownmenu.Shutdownmenu(windowmanager, loop, mopidy,"Powermenü")
    loadedwins.append(idlescreen)
    loadedwins.append(playbackm)
    loadedwins.append(windows.mainmenu.Mainmenu(windowmanager,loop,"Hauptmenü"))
    loadedwins.append(windows.info.Infomenu(windowmanager,loop))
    loadedwins.append(windows.headphone.Headphonemenu(windowmanager,loop,objbluetooth,"Audioausgabe"))
    loadedwins.append(windows.bluetooth.Bluetoothmenu(windowmanager,loop,objbluetooth,"Bluetoothmenu"))
    loadedwins.append(windows.playlistmenu.Playlistmenu(windowmanager, loop, musicmanager))
    loadedwins.append(windows.foldermenu.Foldermenu(windowmanager,loop))
    loadedwins.append(windows.folderinfo.FolderInfo(windowmanager, loop))
    loadedwins.append(windows.ende.Ende(windowmanager, loop,_nowplaying))
    loadedwins.append(shutdownscreen)
    loadedwins.append(windows.start.Start(windowmanager, loop, mopidy,objbluetooth))
    loadedwins.append(wdownload.DownloadMenu(windowmanager,loop))
    loadedwins.append(wsnake.SnakeGame(windowmanager,loop))
    loadedwins.append(wlock.Lock(windowmanager,loop,_nowplaying))
    loadedwins.append(wsystem.SystemMenu(windowmanager,loop,"Systemeinstellungen"))
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
        from integrations.inputs.keypad_4x4_i2c import keypad_4x4_i2c

        mKeypad = keypad_4x4_i2c(loop, settings.KEYPAD_ADDR, settings.KEYPAD_INTPIN, turn_callback, push_callback)


    ###Rotaryencoder Setup
    if "rotaryenc" in settings.INPUTS:
        from integrations.inputs.rotaryencoder import RotaryEncoder

        print ("Rotaryconctroller")
        rc = RotaryEncoder(loop, turn_callback, push_callback)


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


    #### pirateaudio init
    if "pirateaudio" in settings.INPUTS:
        from integrations.inputs.pirateaudio import PirateAudio
        pirateaudio = PirateAudio(loop, turn_callback, push_callback)

# end init inputs

    ######Status LED
    if "statusled" in settings.INPUTS:
        import integrations.statusled as statusled
        led = statusled.statusled(loop,musicmanager)

    ####x728V2.1
    if "x728" in settings.INPUTS:
        import integrations.x728v21 as x728v21
        x728 = x728v21.x728(loop)


    ###main
    try:
        loop.run_forever()
        modipy.stop()
    except (KeyboardInterrupt, SystemExit):
        logger.error("main Loop exiting")
    finally:
        loop.close()

    ###GPICase
    if "gpicase " in settings.INPUTS:
        mypygame.quit()

    if settings.shutdown_reason == settings.SR2:
        if haspowercontroller:
            if pc.ready:
                pc.shutdown()

        print("Shutting down system")
        playout.pc_shutdown()

    if settings.shutdown_reason == settings.SR3:
        playout.pc_reboot()



if __name__ == '__main__':
    main()
    if "rotaryenc" in settings.INPUTS:
        RotaryEncoder.cleanup()
    sys.exit(0)
