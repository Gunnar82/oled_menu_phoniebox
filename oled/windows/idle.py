""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
import settings
from luma.core.render import canvas
from PIL import ImageFont
import os
import time

import integrations.bluetooth
import integrations.playout as playout
from integrations.functions import *
from integrations.logging import *
import RPi.GPIO as GPIO
import locale
import time



class Idle(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_NORMAL)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_SMALL)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=8)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=12)
    faiconsxl = ImageFont.truetype(settings.FONT_ICONS, size=30)

    def __init__(self, windowmanager, nowplaying):
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        super().__init__(windowmanager)
        active = False
        self.nowplaying = nowplaying
        self.timeout=False
        self.oldtitle = ""
        self.oldname = ""
        self.oldalbum = ""
        self.namex = 0
        self.titlex = 0
        self.albumx = 0
        self.LocalOutputEnabled = False
        self.BluetoothFound = False
        self.window_on_back = "playlistmenu"


        #self.loop.create_task(find_dev_bt())



    def activate(self):
        self.titlex = 0
        self.namex = 0
        self.albumx = 0
        self.oldname = ""
        self.oldtitle = ""
        self.oldalbum = ""
        self.oldsong = ""

        active = True


    def deactivate(self):

        active = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()

            ####setting idle text / Icon on Song Number Changed
            if (self.oldsong != self.nowplaying._song) and ((datetime.datetime.now() - settings.lastinput).total_seconds() >= 5):
                if (self.oldsong != ""):
                    self.busytext = " Titel %2.2d von %2.2d " % (int(self.nowplaying._song), int(self.nowplaying._playlistlength))
                    self.busysymbol = settings.SYMBOL_CHANGING_SONG
                    self.changerendertimeonhint = True
                    self.busy = True


                self.oldsong = self.nowplaying._song


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


            #shutdowntimer ? aktiv dann Zeit anzeigen
            if settings.job_t >= 0:
                draw.text((xpos3 + 2, lineposy + 2 ), "%2.2d" % (int(settings.job_t)), font=Idle.fontsmall, fill="BLUE")
            elif settings.X728_ENABLED:
                draw.text((xpos3 + 2, lineposy + 2), settings.battsymbol, font=Idle.faicons, fill=fn.get_battload_color())

            if settings.X728_ENABLED:
                #battery load line
                try:
                    pos = int(settings.battcapacity/100*settings.DISPLAY_WIDTH)
                    draw.rectangle((0,3,pos,3),outline=fn.get_battload_color(),fill=fn.get_battload_color())
                except:
                    print ("err")

            #volume
            draw.text((1, lineposy + 2 ), str(self.nowplaying._volume), font=Idle.fontsmall, fill="white")

            #Zeitanzeige
            try:
                if self.nowplaying._state == "play":
                    #elapsed
                    _spos = fn.to_min_sec(self.nowplaying._elapsed)
                    _xpos = int((xpos1 + xpos2) / 2 ) - int(Idle.fontsmall.getsize(_spos)[0]/2)

                    draw.text((_xpos, lineposy + 2 ),_spos, font=Idle.fontsmall, fill="white")
                else:
                    _spos = self.nowplaying._state
                    _xpos = int((xpos1 + xpos2) / 2 ) - int(Idle.fontsmall.getsize(_spos)[0]/2)

                    draw.text((_xpos, lineposy + 2), _spos, font=Idle.fontsmall, fill="white") #other than play
                    if self.nowplaying._statex != self.nowplaying._state:
                        self.nowplaying._statex = self.nowplaying._state

            except KeyError:
                pass

            #Currently playing song
            #Line 1 2 3
            if float(self.nowplaying._duration) >= 0:
                timelinepos = int(float(self.nowplaying._elapsed) / float(self.nowplaying._duration)  * settings.DISPLAY_WIDTH) # TODO Device.with
            else:
                timelinepos = settings.DISPLAY_WIDTH # device.width
            #Fortschritssleiste Wiedergabe
            draw.rectangle((0,0,timelinepos,1),outline=settings.COLOR_BLUE, fill=settings.COLOR_BLUE)

            #Position in Playlist
            _spos = "%2.2d/%2.2d" % (int(self.nowplaying._song), int(self.nowplaying._playlistlength))
            _xpos = int((xpos3 + xpos2) / 2) - int(Idle.fontsmall.getsize(_spos)[0]/2)

            draw.text((_xpos, lineposy + 2 ),_spos , font=Idle.fontsmall, fill="white")


            if (settings.battcapacity >= 0 and settings.battcapacity <= settings.X728_BATT_EMERG): 
                playout.savepos()
                playout.pc_shutdown()

                return

            if ((self.nowplaying._state == "stop") or (settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or (settings.battcapacity <= settings.X728_BATT_LOW) or (settings.DISPLAY_HEIGHT > 64)):
                if (settings.battcapacity >= 0):
                    text = "Batterie: %d%%%s" % (settings.battcapacity, ", lädt." if settings.battloading else " ") if settings.battcapacity > settings.X728_BATT_LOW else "Batterie laden! %d%%" % (settings.battcapacity)
                    mwidth = Idle.font.getsize(text)
                    ungerade = (time.time() % 2) // 1
                    fill = "black" if ungerade and  settings.battcapacity <= settings.X728_BATT_LOW else  fn.get_battload_color()
                    draw.text(((settings.DISPLAY_WIDTH/2) - (mwidth[0]/2),10), text, font=Idle.font, fill=fill)
                if settings.job_i >= 0 or settings.job_t >= 0:
                    if settings.job_i >= settings.job_t:
                        aus = settings.job_i
                    else:
                        aus = settings.job_t
                    draw.text((20,30), "AUS in " +  str(aus) + "min", font=Idle.font, fill="white")
                else:
                    text = now.strftime("%a, %d.%m.%y %H:%M")
                    mwidth = Idle.font.getsize(text)
                    draw.text(((settings.DISPLAY_WIDTH/2) - (mwidth[0]/2),30), "%s" % (text), font=Idle.font, fill="white")

                if settings.DISPLAY_HEIGHT <= 64:
                    return

            #Titel Scrollbar
            if self.nowplaying._playingtitle == self.oldtitle:
                if Idle.font.getsize(self.nowplaying._playingtitle[self.titlex:])[0] > 127:
                    self.titlex += 1
                else:
                    self.titlex = 0
            else:
                self.titlex = 0

                self.oldtitle = self.nowplaying._playingtitle

                if (datetime.datetime.now() - settings.lastinput).total_seconds() >= settings.DARK_TIMEOUT:
                     settings.lastinput = datetime.datetime.now() - datetime.timedelta(seconds=settings.CONTRAST_TIMEOUT)

           ###name Scrollbar
            if self.nowplaying._playingname == self.oldname and Idle.font.getsize(self.nowplaying._playingname[self.namex:])[0] > 127:
                self.namex += 1
            else:
                self.namex = 0
                self.oldname = self.nowplaying._playingname

            ####album scrollbar
            if self.nowplaying._playingalbum == self.oldalbum and Idle.font.getsize(self.nowplaying._playingalbum[self.albumx:])[0] > 115:
                self.albumx += 1
            else:
                self.albumx = 0
                self.oldalbum = self.nowplaying._playingalbum


            draw.text((1, settings.DISPLAY_HEIGHT - 3*settings.FONT_HEIGHT_NORMAL ), self.nowplaying._playingalbum[self.albumx:self.albumx+19], font=Idle.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 4*settings.FONT_HEIGHT_NORMAL ), self.nowplaying._playingname[self.namex:], font=Idle.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 5*settings.FONT_HEIGHT_NORMAL ), self.nowplaying._playingtitle[self.titlex:], font=Idle.font, fill="white")


    async def _find_dev_bt(self):
        await asyncio.sleep(30)

        if integrations.bluetooth.check_dev_bt():
            self.BluetoothFound = True
            #integrations.bluetooth.enable_dev_bt()
        else:
            if not self.LocalOutputEnabled:
    
                integrations.bluetooth.enable_dev_local()
    
                self.LocalOutputEnabled = True

    def push_callback(self,lp=False):
        if lp:
            self.windowmanager.set_window("shutdownmenu")
        else:
            self.windowmanager.set_window("playbackmenu")


    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                self.busysymbol = settings.SYMBOL_VOL_UP
                playout.pc_volup(3)
            elif key == 'down' or key == '8':
                self.busysymbol = settings.SYMBOL_VOL_DN

                playout.pc_voldown(3)
            elif key == 'left' or key =='4':
                self.busysymbol = settings.SYMBOL_PREV

                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,-1))
                else:
                    playout.pc_prev()
            elif key == 'right' or key == '6':
                self.busysymbol = settings.SYMBOL_NEXT
                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,1))
                else:
                    playout.pc_next()
            elif key == 'A':
                settings.audio_basepath = settings.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = fn.get_folger_from_file(settings.FILE_LAST_MUSIC)
                self.windowmanager.set_window("foldermenu")
            elif key == 'B':
                settings.audio_basepath = settings.AUDIO_BASEPATH_HOERBUCH 
                settings.currentfolder = fn.get_folger_from_file(settings.FILE_LAST_HOERBUCH)
                self.windowmanager.set_window("foldermenu")
            elif key == 'C':
                settings.audio_basepath = settings.AUDIO_BASEPATH_RADIO
                settings.currentfolder = fn.get_folger_from_file(settings.FILE_LAST_RADIO)
                self.windowmanager.set_window("foldermenu")
            elif key =='D':
                self.windowmanager.set_window("shutdownmenu")
            elif key =='9':
                self.windowmanager.set_window("pinmenu")
            elif key == '5':
                 self.windowmanager.clear_window()
            elif key == '0':
                self.busysymbol = settings.SYMBOL_VOL_MUTE
                playout.pc_mute()
            elif key in ['1', '3', '7']:

                if key == '1':
                    what = settings.FILE_LAST_HOERBUCH
                elif key == '3':
                    what = settings.FILE_LAST_RADIO
                elif key == '7':
                    what = settings.FILE_LAST_MUSIC

                if playout.checkfolder(what) != 0:
                    self.busysymbol = settings.SYMBOL_ERROR
                    time.sleep(5)
                else:
                    playout.playlast_checked(what)



        else:
            if (direction > 0):
                self.busysymbol = settings.SYMBOL_VOL_UP
                playout.pc_volup()
            else:
                self.busysymbol = settings.SYMBOL_VOL_DN
                playout.pc_voldown()
