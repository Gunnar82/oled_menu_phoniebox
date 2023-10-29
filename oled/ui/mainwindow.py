""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
import settings, colors, symbols
from luma.core.render import canvas
from PIL import ImageFont
import os
import RPi.GPIO as GPIO
import locale
import time

import integrations.bluetooth
import integrations.playout as playout

from integrations.functions import get_battload_color, to_min_sec, get_folder, get_folder_of_livestream, get_folder_from_file

from integrations.logging import *



class MainWindow(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_NORMAL)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_SMALL)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_SMALL)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=12)
    faiconsxl = ImageFont.truetype(settings.FONT_ICONS, size=30)

    def __init__(self, windowmanager, nowplaying):
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        super().__init__(windowmanager)
        active = False
        self.nowplaying = nowplaying
        self.timeout=False
        self.namex = 0
        self.titlex = 0
        self.albumx = 0

    def render(self,draw):
        now = datetime.datetime.now()


        #Trennleiste waagerecht
        lineposy = settings.DISPLAY_HEIGHT - settings.FONT_HEIGHT_SMALL - 5
        draw.rectangle((0,lineposy,settings.DISPLAY_WIDTH,lineposy),outline="white",fill="white")

        #Trennleisten senkrecht3
        xpos1 = int(settings.DISPLAY_WIDTH/6)
        draw.rectangle((xpos1,lineposy,xpos1,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")
        xpos2 = int(3.5*settings.DISPLAY_WIDTH/6)
        draw.rectangle((xpos2,lineposy,xpos2,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")
        xpos3 = int(5*settings.DISPLAY_WIDTH/6)
        draw.rectangle((xpos3,lineposy,xpos3,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")

        #Zeitanzeige
        try:
            if self.nowplaying._state == "play":
                #elapsed
                _spos = to_min_sec(self.nowplaying._elapsed)
                _xpos = int((xpos1 + xpos2) / 2 ) - int(self.fontsmall.getsize(_spos)[0]/2)

                draw.text((_xpos, lineposy + 2 ),_spos, font=self.fontsmall, fill="white")
            else:
                _spos = self.nowplaying._state
                _xpos = int((xpos1 + xpos2) / 2 ) - int(self.fontsmall.getsize(_spos)[0]/2)

                draw.text((_xpos, lineposy + 2), _spos, font=self.fontsmall, fill="white") #other than play
                if self.nowplaying._statex != self.nowplaying._state:
                    self.nowplaying._statex = self.nowplaying._state

        except KeyError:
            pass


        #volume
        draw.text((1, lineposy + 2 ), str(self.nowplaying._volume), font=self.fontsmall, fill="white")

        #Zeitanzeige
        try:
            if self.nowplaying._state == "play":
                #elapsed
                _spos = to_min_sec(self.nowplaying._elapsed)
                _xpos = int((xpos1 + xpos2) / 2 ) - int(self.fontsmall.getsize(_spos)[0]/2)

                draw.text((_xpos, lineposy + 2 ),_spos, font=self.fontsmall, fill="white")
            else:
                _spos = self.nowplaying._state
                _xpos = int((xpos1 + xpos2) / 2 ) - int(self.fontsmall.getsize(_spos)[0]/2)

                draw.text((_xpos, lineposy + 2), _spos, font=self.fontsmall, fill="white") #other than play
                if self.nowplaying._statex != self.nowplaying._state:
                    self.nowplaying._statex = self.nowplaying._state

        except KeyError:
            pass



        if "x728" in settings.INPUTS:
            #battery load line
            try:
                pos = int(settings.battcapacity/100*settings.DISPLAY_WIDTH)
                draw.rectangle((0,3,pos,3),outline=get_battload_color(),fill=get_battload_color())
            except:
                log(lERROR,"Battery Error")

        #Currently playing song

        if float(self.nowplaying._duration) >= 0:
            timelinepos = int(float(self.nowplaying._elapsed) / float(self.nowplaying._duration)  * settings.DISPLAY_WIDTH) # TODO Device.with
        else:
            timelinepos = settings.DISPLAY_WIDTH # device.width
        #Fortschritssleiste Wiedergabe
        draw.rectangle((0,0,timelinepos,1),outline=colors.COLOR_BLUE, fill=colors.COLOR_BLUE)

        #Position in Playlist
        _spos = "%2.2d/%2.2d" % (int(self.nowplaying._song), int(self.nowplaying._playlistlength))
        _xpos = int((xpos3 + xpos2) / 2) - int(self.fontsmall.getsize(_spos)[0]/2)

        draw.text((_xpos, lineposy + 2 ),_spos , font=self.fontsmall, fill="white")
        #shutdowntimer ? aktiv dann Zeit anzeigen
        xpause = 0
        if 'http://' in self.nowplaying.filename or 'https://' in self.nowplaying.filename:
            draw.text((xpos3 + 5, lineposy + 2), symbols.SYMBOL_CLOUD, font=self.faicons, fill="white")
            xpause, ypause = self.faicons.getsize(symbols.SYMBOL_CLOUD)

        if settings.job_t >= 0:
            draw.text((xpos3 + 5 + 1.2 * xpause, lineposy + 2 ), "%2.2d" % (int(settings.job_t)), font=self.fontsmall, fill="white")
        elif "x728" in settings.INPUTS:
            draw.text((xpos3 + 5 + 1.2 * xpause, lineposy + 2), settings.battsymbol, font=self.faicons, fill=get_battload_color())


    async def _find_dev_bt(self):
        await asyncio.sleep(30)

        if integrations.bluetooth.check_dev_bt():
            self.BluetoothFound = True
            #integrations.bluetooth.enable_dev_bt()
        else:
            if not self.LocalOutputEnabled:
    
                integrations.bluetooth.enable_dev_local()
    
                self.LocalOutputEnabled = True
