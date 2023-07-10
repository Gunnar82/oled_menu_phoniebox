"""Start file for Werkstattradio OLED controller"""
import asyncio
import signal
import sys
import os

from subprocess import call
import integrations.bluetooth
from integrations.display import get_display


import settings

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
import windows.pin

import settings

if settings.KEYBOARD_ENABLED:
    from integrations.keyboard import KeyboardCtrl



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

    ###processing nowplaying
    import integrations.nowplaying as nowplaying

    _nowplaying = nowplaying.nowplaying(loop,musicmanager,windowmanager)


    #Import all window classes and generate objects of them
    loadedwins = []
    idlescreen = windows.idle.Idle(windowmanager, _nowplaying)
    playbackm = windows.playbackmenu.Playbackmenu(windowmanager,_nowplaying)
    shutdownscreen = windows.shutdownmenu.Shutdownmenu(windowmanager, mopidy,"Powermenü")
    loadedwins.append(idlescreen)
    loadedwins.append(playbackm)
    loadedwins.append(windows.mainmenu.Mainmenu(windowmanager,"Hauptmenü"))
    loadedwins.append(windows.info.Infomenu(windowmanager))
    loadedwins.append(windows.headphone.Headphonemenu(windowmanager,"Audioausgabe"))
    loadedwins.append(windows.playlistmenu.Playlistmenu(windowmanager, musicmanager))
    loadedwins.append(windows.foldermenu.Foldermenu(windowmanager))
    loadedwins.append(windows.folderinfo.FolderInfo(windowmanager))
    loadedwins.append(windows.ende.Ende(windowmanager))
    loadedwins.append(windows.wlan.Wlanmenu(windowmanager))
    loadedwins.append(shutdownscreen)
    loadedwins.append(windows.firewall.Firewallmenu(windowmanager))
    loadedwins.append(windows.start.Start(windowmanager, mopidy))
    loadedwins.append(windows.pin.PinMenu(windowmanager))

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

    ####keyboard control
    if settings.KEYBOARD_ENABLED:
        from integrations.keyboard import KeyboardCtrl

        mKeyboard = KeyboardCtrl(loop, turn_callback, push_callback)

    ### KEYPAD 4x4 MCP23017 I2C

    if settings.KEYPAD_ENABLED:
        from integrations.keypad_4x4_i2c import keypad_4x4_i2c

        mKeypad = keypad_4x4_i2c(loop, settings.KEYPAD_ADDR, settings.KEYPAD_INTPIN, turn_callback, push_callback)

    ###Rotaryencoder Setup
    if settings.ROTARYENCODER_ENABLED:
        from integrations.rotaryencoder import RotaryEncoder

        print ("Rotaryconctroller")
        rc = RotaryEncoder(loop, turn_callback, push_callback)


    ####Powercontroller Init
    haspowercontroller = False
    if settings.POWERCONTROLLER_ENABLED:
        from integrations.powercontroller import PowerController

        haspowercontroller = True
        try:
            print ("Poweronctroller")
            pc = PowerController(loop, turn_callback, push_callback)
            haspowercontroller = False
        except:
            haspowercontroller = False

    ######Status LED
#    if settings.STATUS_LED_ENABLED:
#        import integrations.statusled as statusled
#        led = statusled.statusled(loop,musicmanager)

    ####x728V2.1
    if settings.X728_ENABLED:
        import integrations.x728v21 as x728v21
        x728 = x728v21.x728(loop)


    if settings.GPIOControl:
        from integrations.gpiocontrol import GPIOControl
        gpioc = GPIOControl(loop, turn_callback, push_callback)


    ###main
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")
    finally:
        loop.close()

    if shutdownscreen.execshutdown:
        settings.shutdown_reason=settings.SR2
    elif shutdownscreen.execreboot:
        settings.shutdown_reason=settings.SR3
    else:
        settings.shutdown_reason=settings.SR1

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
    if settings.ROTARYENCODER_ENABLED:
        RotaryEncoder.cleanup()
    sys.exit(0)
