""" playbackmenu """
import datetime
import asyncio
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os

from ui.mainwindow import MainWindow
import integrations.playout as playout
from integrations.functions import to_min_sec,get_folder_of_livestream, get_folder

import RPi.GPIO as GPIO

class Playbackmenu(MainWindow):
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XL)

    def __init__(self, windowmanager, nowplaying):
        super().__init__(windowmanager,nowplaying)
        self.nowplaying = nowplaying
        self._volume = -1
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
        self.descr.append([ "Zurück / Vor", "\uf07e" ])
        self.descr.append([ "Stop", "\uf04d" ])
        self.descr.append([ "Play / Pause","\uf04c", "\uf04b" ])
        self.descr.append([ "Hauptmenü", "\uf062" ])
        self.descr.append([ "Zurück", "\uf0a8" ])
        self.descr.append([ "Wiedergabeliste", "\uf03c" ])

        self.symwidth,self.symheight = Playbackmenu.faiconsbig.getsize(self.descr[1][1])
        self.window_on_back = "idle"

    def activate(self):
        self._activepbm = True
        self.counter = 2
        self.skipselected = False

    def deactivate(self):
        self._activepbm = False

    def render(self):
        with canvas(self.device) as draw:
            super().render(draw)
            now = datetime.datetime.now()

            drawtext = "Titelwechsel aktiv" if self.skipselected else self.descr[self.counter][0]
            mwidth = Playbackmenu.font.getsize(drawtext)

            draw.text((int(settings.DISPLAY_WIDTH / 2) - int(mwidth[0]/2),settings.DISPLAY_HEIGHT - 4 * settings.FONT_HEIGHT_XL), text=drawtext, font=Playbackmenu.font, fill="white")

            i = 0

            startx = int(settings.DISPLAY_WIDTH/2) - int(len(self.descr) / 2 * (self.symwidth * 1.3))

            while (i < len(self.descr)):
                xpos = startx + i * (self.symwidth*1.3)
                draw.text((xpos, settings.DISPLAY_HEIGHT - 3 * settings.FONT_HEIGHT_XL - (2 if (i == self.counter) else 0) ), self.descr[i][1], font=Playbackmenu.faiconsbig, fill=settings.COLOR_SELECTED if (i == self.counter) else settings.COLOR_WHITE ) #prev

                i += 1

    def push_callback(self,lp=False):
        if self.counter == 1:
            playout.pc_stop()
        elif self.counter == 2:
            playout.pc_toggle()
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
                    cfolder = get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (get_folder(cfolder,-1))
                else:
                    playout.pc_prev()

            else:
                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (get_folder(cfolder,1))
                else:
                    playout.pc_next()

        else:
            if (self.counter + direction < len(self.descr) and self.counter + direction >= 0):
                self.counter += direction
            
        #os.system("mpc volume {}{} > /dev/null".format(plus,direction))
        #if self.counter + direction <= 0 and self.counter + direction >= 0:
            #self.counter += direction
