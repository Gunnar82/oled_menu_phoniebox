""" playbackmenu """
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

    def __init__(self, windowmanager, nowplaying):
        super().__init__(windowmanager)
        self._activepbm = False
        self.nowplaying = nowplaying
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
        self.descr.append([ "Zurück / Vor", "\uf048\uf051" ])
        self.descr.append([ "Stop", "\uf04d" ])
        self.descr.append([ "Play / Pause","\uf04c", "\uf04b" ])
        self.descr.append([ "Hauptmenü", "\uf062" ])
        self.descr.append([ "Zurück", "\uf0a8" ])
        self.descr.append([ "Wiedergabeliste", "\uf0ca" ])

    def activate(self):
        self._activepbm = True
        self.counter = 2
        self.skipselected = False

    def deactivate(self):
        self._activepbm = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()
            mwidth = Playbackmenu.font.getsize(self.descr[self.counter][0])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter][0], font=Playbackmenu.font, fill="white")


            #Trennleiste waagerecht
            draw.rectangle((0,settings.DISPLAY_HEIGHT -15,128,settings.DISPLAY_HEIGHT - 15),outline="white",fill="white")
            #Trennleisten senkrecht
            draw.rectangle((16,settings.DISPLAY_HEIGHT -15,16,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")
            draw.rectangle((65,settings.DISPLAY_HEIGHT -15,65,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")
            draw.rectangle((105,settings.DISPLAY_HEIGHT -15,105,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")

            #volume
            draw.text((1, settings.DISPLAY_HEIGHT -14 ), str(self.nowplaying._volume), font=Playbackmenu.fontsmall, fill="white")


            #Buttons
            try:
                if self.nowplaying._state == "play":
                    #elapsed
                    _spos = fn.to_min_sec(self.nowplaying._elapsed)
                    _xpos = 41 - int(Playbackmenu.fontsmall.getsize(_spos)[0]/2)

                    draw.text((_xpos, settings.DISPLAY_HEIGHT -14  ),_spos, font=Playbackmenu.fontsmall, fill="white")
                else:
                    _spos = self.nowplaying._state
                    _xpos = 41 - int(Playbackmenu.fontsmall.getsize(_spos)[0]/2)

                    draw.text((_xpos, settings.DISPLAY_HEIGHT -14 ), _spos, font=Playbackmenu.fontsmall, fill="white") #other than play


            except KeyError:
                pass

            try:
                if float(self.nowplaying._duration) >= 0:
                    timelinepos = int(float(self.nowplaying._elapsed) / float(self.nowplaying._duration)  * 128) # TODO Device.with
                else:
                    timelinepos = 128 # device.width
            except:
                timelinepos = 128

            #Fortschritssleiste Wiedergabe
            draw.rectangle((0,0,timelinepos,1),outline="white",fill="white")


            #Currently playing song
            #Line 1 2 3


           #paylistpos
            _spos = "%2.2d/%2.2d" % (int(self.nowplaying._song), int(self.nowplaying._playlistlength))
            _xpos = 85 - int(Playbackmenu.fontsmall.getsize(_spos)[0]/2)
            draw.text((_xpos, settings.DISPLAY_HEIGHT -14 ),_spos , font=Playbackmenu.fontsmall, fill="white")


            #shutdowntimer ? aktiv dann Zeit anzeigen
            if settings.job_t >= 0:
                draw.text((108, settings.DISPLAY_HEIGHT -14 ), "%2.2d" % (int(settings.job_t)), font=Playbackmenu.fontsmall, fill="white")


            #selection line

            fillcolor = "white"
            bgcolor = "black"

            i = 0

            if (self.skipselected):
                draw.line((8, 42, 20, 42), width=2, fill=settings.COLOR_SELECTED)

            while (i < len(self.descr)):
                draw.text((5 + i*21, 18 if (i == self.counter) else 20 ), self.descr[i][1], font=Playbackmenu.faiconsbig, fill=settings.COLOR_SELECTED if (i == self.counter) else fillcolor ) #prev
                i += 1

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
                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,-1))
                else:
                    playout.pc_prev()

            else:
                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,1))
                else:
                    playout.pc_next()

        else:
            if (self.counter + direction < len(self.descr) and self.counter + direction >= 0):
                self.counter += direction
            
        #os.system("mpc volume {}{} > /dev/null".format(plus,direction))
        #if self.counter + direction <= 0 and self.counter + direction >= 0:
            #self.counter += direction
