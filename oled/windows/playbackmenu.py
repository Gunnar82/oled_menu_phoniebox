""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.playout as playout
import os
import integrations.functions as fn

import RPi.GPIO as GPIO

class Playbackmenu(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=10)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=8)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=16)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager)
        self._activepbm = False
        self.musicmanager = musicmanager
        self._volume = -1
        self._playingfile = ""
        self._playingalbum = ""
        self._time = -1
        self._elapsed = -1
        self._playlistlength = -1
        self._song = -1
        self._duration = -1
        self._state = "starting"
        self._statex ="unknown"
        self.counter = 1
        self.skipselected = False
        self.descr = []
        self.descr.append("Zurück / Vor")
        self.descr.append ("Stop")
        self.descr.append ("Play / Pause")
        self.descr.append("Hauptmenü")
        self.descr.append("Zurück")
        self.descr.append("Wiedergabeliste")
         #self.loop.create_task(self._find_dev_bt())
        if settings.STATUS_LED_ENABLED:
            GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD
            GPIO.setup(settings.STATUS_LED_PIN, GPIO.OUT)
            if settings.STATUS_LED_ALWAYS_ON:
                GPIO.output(settings.STATUS_LED_PIN, 1)

    def activate(self):
        self._activepbm = True
        self.loop.create_task(self._generatenowplaying())
        self.counter = 2
        self.skipselected = False

    def deactivate(self):
        self._activepbm = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            mwidth = Playbackmenu.font.getsize(self.descr[self.counter])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter], font=Playbackmenu.font, fill="white")


            #Trennleiste waagerecht
            draw.rectangle((0,49,128,49),outline="white",fill="white")
            #Trennleisten senkrecht
            draw.rectangle((16,49,16,64),outline="white",fill="white")
            draw.rectangle((65,49,65,64),outline="white",fill="white")
            draw.rectangle((105,49,105,64),outline="white",fill="white")

            #volume
            draw.text((1, 51 ), str(self._volume), font=Playbackmenu.fontsmall, fill="white")

            #Buttons
            if self.musicmanager.source == "mpd":
                if True:
                    if self._state == "play":
                        #elapsed
                        _spos = fn.to_min_sec(self._elapsed)
                        _xpos = 41 - int(Playbackmenu.fontsmall.getsize(_spos)[0]/2)

                        draw.text((_xpos, 51 ),_spos, font=Playbackmenu.fontsmall, fill="white")
                        if self._statex != self._state:
                            self._statex = self._state
                            if settings.STATUS_LED_ENABLED and not settings.STATUS_LED_ALWAYS_ON:
                                GPIO.output(settings.STATUS_LED_PIN, 0)
                    else:
                        _spos = self._state
                        _xpos = 41 - int(Playbackmenu.fontsmall.getsize(_spos)[0]/2)

                        draw.text((_xpos, 51), _spos, font=Playbackmenu.fontsmall, fill="white") #other than play
                        if self._statex != self._state:
                            self._statex = self._state
                            if settings.STATUS_LED_ENABLED:
                                GPIO.output(settings.STATUS_LED_PIN, 1)

                #except KeyError:
                #    pass


            #Widgets
            if not self.musicmanager.mopidyconnection.connected:
                draw.text((18, 2), "\uf071", font=Playbackmenu.faicons, fill="white")

            try:
                if float(self._duration) >= 0:
                    timelinepos = int(float(self._elapsed) / float(self._duration)  * 128) # TODO Device.with
                else:
                    timelinepos = 128 # device.width
            except:
                timelinepos = 128

            #Fortschritssleiste Wiedergabe
            draw.rectangle((0,0,timelinepos,1),outline="white",fill="white")


            #Currently playing song
            #Line 1 2 3


           #paylistpos
            _spos = "%2.2d/%2.2d" % (int(self._song), int(self._playlistlength))
            _xpos = 85 - int(Playbackmenu.fontsmall.getsize(_spos)[0]/2)
            draw.text((_xpos, 51 ),_spos , font=Playbackmenu.fontsmall, fill="white")


            #shutdowntimer ? aktiv dann Zeit anzeigen
            if settings.job_t >= 0:
                draw.text((108, 51 ), "%2.2d" % (int(settings.job_t)), font=Playbackmenu.fontsmall, fill="white")


            #draw.text((10,10),"CONTROLS", font=Idle.bigfong, fill="white")
            #draw.text((18, 2), "\uf071", font=Playbackmenu.faicons, fill="white")

            #selection line
            draw.line((10+(self.counter)*20, 42, 30+(self.counter)*20, 42), width=2, fill=settings.COLOR_SELECTED)
            fillcolor = "black" if self.skipselected else "white"
            bgcolor   = "white" if self.skipselected else "black"
            draw.rectangle((7,17,30,40),fill=bgcolor,outline=bgcolor)
            draw.text((5, 20), "\uf048", font=Playbackmenu.faiconsbig, fill=fillcolor) #prev
            draw.text((15, 20), "\uf051", font=Playbackmenu.faiconsbig, fill=fillcolor) #next
            draw.text((30, 20), "\uf04d", font=Playbackmenu.faiconsbig, fill="white") #play
            if self._state == "play":
                draw.text((50, 20), "\uf04c", font=Playbackmenu.faiconsbig, fill="white") #pause
            else: #self._state == "pause":
                draw.text((50, 20), "\uf04b", font=Playbackmenu.faiconsbig, fill="white") #play
            draw.text((70, 20), "\uf062", font=Playbackmenu.faiconsbig, fill="white") #menu
            draw.text((90, 20), "\uf0a8", font=Playbackmenu.faiconsbig, fill="white") #menu
            draw.text((110, 20), "\uf0ca", font=Playbackmenu.faiconsbig, fill="white") #menu


    async def _generatenowplaying(self):
        namex = 0
        albumx = 0
        titlex = 0
        oldname = ""
        oldtitle = ""
        oldalbum = ""
        filename = ""

        while self.loop.is_running() and self._activepbm:

            playing = self.musicmanager.nowplaying()
            status = self.musicmanager.status()
            filename = playing['file'] if ("file" in playing) else ""

            self._playingfile = playing['file'] if ("file" in playing) else ""
            self._playingalbum = "Livestream" if (self._playingfile.startswith('http')) else "" 
            self._volume = status['volume'] if ("volume" in status) else -1
            self._elapsed = status['elapsed'] if ("elapsed" in status) else -1
            self._time = status['time'] if ("time" in status) else -1
            self._playlistlength = status['playlistlength'] if ("playlistlength" in status) else -1
            self._song = str(int(status['song']) + 1) if ("song" in status) else -1
            self._duration = status['duration'] if ("duration" in status) else -1
            self._state = status['state'] if ("state" in status) else "unknown"
            
            await asyncio.sleep(0.25)

    def push_callback(self,lp=False):
        if self.counter == 1:
            os.system("/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerstop")
        elif self.counter == 2:
            os.system("/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerpause")
        elif self.counter == 3:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 4:
            self.windowmanager.set_window("idle")
        elif self.counter == 5:
            self.windowmanager.set_window("playlistmenu")
        elif self.counter == 0:
            if self.skipselected:
                self.skipselected = False
                self.timeout=True
            else:
                self.skipselected = True
                self.timeout=False

        #self._showcontrols = False
        #self.windowmanager.set_window("mainmenu")
        #elif self.counter == 1:
        #    self.musicmanager.previous()
        #elif self.counter == 2:
        #    self.musicmanager.playpause()
        #elif self.counter == 3:
        #    self.musicmanager.next()

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'right' or key == '6':
                direction = 1
            elif key == 'left' or key == '4':
                direction = -1
            elif key == 'down':
                direction = 0
            elif key == '#':
                self.windowmanager.set_window('idle')
            else:
                direction = 0

        if self.skipselected:
            if direction < 0:
                if self._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,-1))
                else:
                    playout.pc_prev()

            else:
                if self._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,1))
                else:
                    playout.pc_next()

        else:
            if (self.counter + direction <= 5 and self.counter + direction >= 0):
                self.counter += direction
            
        #os.system("mpc volume {}{} > /dev/null".format(plus,direction))
        #if self.counter + direction <= 0 and self.counter + direction >= 0:
            #self.counter += direction
