"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
import sys
from subprocess import call
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
import windows.start

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
    loadedwins.append(shutdownscreen)

    loadedwins.append(windows.start.Start(windowmanager, mopidy))

    for window in loadedwins:
        windowmanager.add_window(window.__class__.__name__.lower(), window)

    #Load start window
#    windowmanager.set_window("playbackmenu")

    windowmanager.set_window("start")


    #Rotary encoder setup
    def turn_callback(direction):
        windowmanager.turn_callback(direction)

    def push_callback():
        windowmanager.push_callback()

    #RotaryEncoder(loop, turn_callback, push_callback)

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
        if haspowercontroller:
            if pc.ready:
                pc.shutdown()

        print("Shutting down system")
        call("sudo systemctl poweroff", shell=True)

    if shutdownscreen.execreboot:
        print("Shutting down system")
        call("/home/pi/oledctrl/reboot.sh", shell=True)


if __name__ == '__main__':
    main()
    RotaryEncoder.cleanup()
    sys.exit(0)
