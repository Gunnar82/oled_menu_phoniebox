#!/usr/bin/python3
"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import os
import time
import importlib

from subprocess import call
import integrations.bluetooth
import integrations.functions as fn
import integrations.playout as playout

import settings, file_folder

######
from datetime import datetime
###########################
settings.screenpower = True
settings.shutdown_reason = "changeme"
settings.lastinput = datetime.now()
settings.job_t = -1
settings.job_i = -1
settings.job_s = -1
settings.audio_basepath = file_folder.AUDIO_BASEPATH_MUSIC
settings.currentfolder = settings.audio_basepath
settings.current_selectedfolder=settings.currentfolder
settings.battcapacity = -1
settings.battloading = False
settings.callback_active = False



from integrations.logging import *

displays = ["st7789", "ssd1351", "sh1106", "emulated"]

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
import windows.mainmenu
import windows.playbackmenu
import windows.playlistmenu
import windows.foldermenu
import windows.shutdownmenu
import windows.folderinfo
import windows.start
import windows.wlan
import windows.ende
import windows.firewall
import windows.download as wdownload
import windows.lock as wlock

#Systemd exit
def gracefulexit(signum, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, gracefulexit)

def main():
    loop = asyncio.get_event_loop()

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

    _nowplaying = nowplaying.nowplaying(loop,musicmanager,windowmanager)

    #Rotary encoder setup
    def turn_callback(direction,_key=False):
        windowmanager.turn_callback(direction, key=_key)

    def push_callback(_lp=False):
        windowmanager.push_callback(lp=_lp)


    ###GPICase
    if "gpicase" in settings.INPUTS:
        from integrations.inputs.gpicase import pygameInput

        print ("Using pyGameInput")
        mypygame = pygameInput(loop, turn_callback, push_callback,windowmanager)

    #Import all window classes and generate objects of them
    loadedwins = []
    idlescreen = windows.idle.Idle(windowmanager, _nowplaying)
    playbackm = windows.playbackmenu.Playbackmenu(windowmanager,_nowplaying)
    shutdownscreen = windows.shutdownmenu.Shutdownmenu(windowmanager, loop, mopidy,"Powermenü")
    loadedwins.append(idlescreen)
    loadedwins.append(playbackm)
    loadedwins.append(windows.mainmenu.Mainmenu(windowmanager,loop,"Hauptmenü"))
    loadedwins.append(windows.info.Infomenu(windowmanager))
    loadedwins.append(windows.headphone.Headphonemenu(windowmanager,loop,"Audioausgabe"))
    loadedwins.append(windows.playlistmenu.Playlistmenu(windowmanager, musicmanager))
    loadedwins.append(windows.foldermenu.Foldermenu(windowmanager,loop))
    loadedwins.append(windows.folderinfo.FolderInfo(windowmanager))
    loadedwins.append(windows.ende.Ende(windowmanager))
    loadedwins.append(windows.wlan.Wlanmenu(windowmanager))
    loadedwins.append(shutdownscreen)
    loadedwins.append(windows.firewall.Firewallmenu(windowmanager,loop))
    loadedwins.append(windows.start.Start(windowmanager, mopidy))
    loadedwins.append(wdownload.DownloadMenu(windowmanager,loop))
    loadedwins.append(wlock.Lock(windowmanager))

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
    except (KeyboardInterrupt, SystemExit):
        log(lERROR,"Exiting")
    finally:
        loop.close()

    ###GPICase
    if "gpicase " in settings.INPUTS:
        mypygame.quit()


    windowmanager.set_window("ende")

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
