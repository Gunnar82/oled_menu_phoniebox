""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
import settings

import config.colors as colors
import config.symbols as symbols

from luma.core.render import canvas
from PIL import ImageFont
import os
import RPi.GPIO as GPIO
import locale
import time

import integrations.bluetooth
import integrations.playout as playout

from integrations.functions import get_battload_color, to_min_sec, get_folder, get_folder_of_livestream, get_folder_from_file

from integrations.logging_config import *

logger = setup_logger(__name__)


class MainWindow(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_NORMAL)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_SMALL)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_SMALL)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=12)
    faiconsxl = ImageFont.truetype(settings.FONT_ICONS, size=30)

    def __init__(self, windowmanager, loop, usersettings, nowplaying):
        super().__init__(windowmanager, loop, usersettings)
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        active = False
        self.nowplaying = nowplaying
        self.timeout=False
        self.namex = 0
        self.titlex = 0
        self.albumx = 0

    def render(self,draw):
        now = datetime.datetime.now()

        #Trennleiste waagerecht
        lineposy = settings.MAINWINDOW_LINEPOS_Y
        draw.rectangle((0,lineposy,settings.DISPLAY_WIDTH,lineposy),outline="white",fill="white")

        #Trennleisten senkrecht3
        xpos1 = int(1.3*settings.DISPLAY_WIDTH/6)
        draw.rectangle((xpos1,lineposy,xpos1,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")
        xpos2 = int(3*settings.DISPLAY_WIDTH/6)
        draw.rectangle((xpos2,lineposy,xpos2,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")
        xpos3 = int(5*settings.DISPLAY_WIDTH/6)
        draw.rectangle((xpos3,lineposy,xpos3,settings.DISPLAY_HEIGHT -4),outline="white",fill="white")

        #Zeitanzeige
        try:
            if self.nowplaying._state == "play":
                #elapsed
                if settings.DISPLAY_WIDTH > 600:
                    _spos = to_min_sec(self.nowplaying._elapsed) + "|" + to_min_sec(self.nowplaying._duration)
                else:
                    _spos = to_min_sec(self.nowplaying._duration)

                _xpos = int((xpos1 + xpos2) / 2 ) - int(self.fontsmall.getsize(_spos)[0]/2)

                draw.text((_xpos, lineposy + settings.MAINWINDOW_LINESPACE ),_spos, font=self.fontsmall, fill="white")
            else:
                _spos = self.nowplaying._state
                _xpos = int((xpos1 + xpos2) / 2 ) - int(self.fontsmall.getsize(_spos)[0]/2)

                draw.text((_xpos, lineposy + settings.MAINWINDOW_LINESPACE), _spos, font=self.fontsmall, fill="white") #other than play
                if self.nowplaying._statex != self.nowplaying._state:
                    self.nowplaying._statex = self.nowplaying._state

        except KeyError:
            pass


        #volume
        draw.text((1, lineposy + settings.MAINWINDOW_LINESPACE ), str(self.nowplaying._volume), font=self.fontsmall, fill="white")
        draw.text((settings.MAINWINDOW_OUTPUTSYMBOL_X, lineposy + settings.MAINWINDOW_LINESPACE ), str(self.nowplaying.output_symbol), font=self.faicons, fill="white")


        if "x728" in settings.INPUTS:
            #battery load line
            try:
                pos = int(settings.battcapacity/100*settings.DISPLAY_WIDTH)
                draw.rectangle((0,3,pos,3),outline=get_battload_color(),fill=get_battload_color())
            except:
                logger.error("Battery Error")

        #Currently playing song

        if float(self.nowplaying._duration) >= 0:
            timelinepos = float(self.nowplaying._elapsed) / float(self.nowplaying._duration)
        else:
            timelinepos = 1 # device.width

        #Fortschritssleiste Wiedergabe
        self.render_progressbar_draw(draw,timelinepos,color1=colors.COLOR_BLUE,color2=colors.COLOR_BLACK)

        #Position in Playlist
        _spos = "%2.2d/%2.2d" % (int(self.nowplaying._song), int(self.nowplaying._playlistlength))
        _xpos = int((xpos3 + xpos2) / 2) - int(self.fontsmall.getsize(_spos)[0]/2)

        draw.text((_xpos, lineposy + settings.MAINWINDOW_LINESPACE ),_spos , font=self.fontsmall, fill="white")

        xpos3 += settings.MAINWINDOW_LINESPACE # Position für Symbol
        lineposy += settings.MAINWINDOW_LINESPACE


        if not self.nowplaying.is_device_online():
            #Teste ob Gerät online ist, wenn nein, zeige Symbol
            draw.text((xpos3, lineposy), symbols.SYMBOL_NOCLOUD, font=self.faicons, fill=colors.COLOR_ORANGE)
        elif self.nowplaying.input_is_online():
            #Teste ob aktuelle Wiedergabe, wenn online, zeige Symbol
            draw.text((xpos3, lineposy), symbols.SYMBOL_CLOUD, font=self.faicons, fill="white")
        elif settings.job_t >= 0:
            #Wenn Shutdowntimer, dann anzeigen
            draw.text((xpos3, lineposy), "%2.2d" % (int(settings.job_t)), font=self.fontsmall, fill="white")
        elif "x728" in settings.INPUTS:
            #wenn Batterie, dann anzeigen
            draw.text((xpos3, lineposy), symbols.SYMBOL_BATTERY, font=self.faicons, fill=get_battload_color())

