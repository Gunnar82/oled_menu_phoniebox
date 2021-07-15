"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import os

from subprocess import call
import integrations.bluetooth
from integrations.display import get_display
from integrations.rotaryencoder import RotaryEncoder
from integrations.powercontroller import PowerController

from integrations.mopidy import MopidyControl
from integrations.musicmanager import Musicmanager
from ui.windowmanager import WindowManager
import windows.idle
import windows.info
import windows.headphone
import windows.mainmenu
import windows.playbackmenu
import windows.playlistmenu
import windows.radiomenu
import windows.foldermenu
import windows.shutdownmenu
import windows.folderinfo
import windows.start
import windows.ende

import settings

#Systemd exit
def gracefulexit(signum, frame):
    sys.exit(0)
signal.signal(signal.SIGTERM, gracefulexit)

def main():
    loop = asyncio.get_event_loop()

    #Display = real hardware or emulator (depending on settings)
    display = get_display()

    #screen = windowmanager
    windowmanager = WindowManager(loop, display)

    #Software integrations
    mopidy = MopidyControl(loop)
    #def airplay_callback(info, nowplaying):
    #    musicmanager.airplay_callback(info, nowplaying)
    #shairport = ShairportMetadata(airplay_callback)
    musicmanager = Musicmanager(mopidy)

    #Import all window classes and generate objects of them
    loadedwins = []
    idlescreen = windows.idle.Idle(windowmanager, musicmanager)
    playbackm = windows.playbackmenu.Playbackmenu(windowmanager,musicmanager)
    shutdownscreen = windows.shutdownmenu.Shutdownmenu(windowmanager, mopidy)
    loadedwins.append(idlescreen)
    loadedwins.append(playbackm)
    loadedwins.append(windows.mainmenu.Mainmenu(windowmanager))
    loadedwins.append(windows.info.Infomenu(windowmanager))
    loadedwins.append(windows.headphone.Headphonemenu(windowmanager))
    loadedwins.append(windows.playlistmenu.Playlistmenu(windowmanager, mopidy))
    loadedwins.append(windows.radiomenu.Radiomenu(windowmanager, mopidy))
    loadedwins.append(windows.foldermenu.Foldermenu(windowmanager))
    loadedwins.append(windows.folderinfo.FolderInfo(windowmanager))
    loadedwins.append(windows.ende.Ende(windowmanager))
    loadedwins.append(shutdownscreen)

    loadedwins.append(windows.start.Start(windowmanager, mopidy))

    for window in loadedwins:
        windowmanager.add_window(window.__class__.__name__.lower(), window)

    #Load start window
#    windowmanager.set_window("shutdownmenu")

    windowmanager.set_window("start")


    #Rotary encoder setup
    def turn_callback(direction,_key=False):
        windowmanager.turn_callback(direction, key=_key)

    def push_callback(_lp=False):
        windowmanager.push_callback(lp=_lp)

    #RotaryEncoder(loop, turn_callback, push_callback
    haspowercontroller = True
    try:
        pc = PowerController(loop, turn_callback, push_callback)
    except:
        haspowercontroller = False

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    finally:
        loop.close()

    if shutdownscreen.execshutdown:
        settings.shutdown_reason="heruntergefahren"
    elif shutdownscreen.execreboot:
        settings.shutdown_reason="neugestartet"

    windowmanager.set_window("ende")

    if shutdownscreen.execshutdown:
        if haspowercontroller:
            if pc.ready:
                pc.shutdown()

        print("Shutting down system")
        os.system("%s -c=shutdown" % (settings.PLAYOUT_CONTROLS))

    if shutdownscreen.execreboot:
        print("Reboot down system")
        os.system("%s -c=reboot" % 	(settings.PLAYOUT_CONTROLS))



if __name__ == '__main__':
    main()
    RotaryEncoder.cleanup()
    sys.exit(0)
