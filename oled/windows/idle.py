""" IDLE screen """
import datetime
import asyncio
from ui.mainwindow import MainWindow
import settings
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



class Idle(MainWindow):

    def __init__(self, windowmanager, nowplaying):
        super().__init__(windowmanager,nowplaying)
        self.changerender = True
        self.window_on_back = "playlistmenu"

    def activate(self):
        self.titlex = 0
        self.namex = 0
        self.albumx = 0
        self.oldsong = ""

        active = True


    def deactivate(self):

        active = False

    def render(self):
        with canvas(self.device) as draw:
            super().render(draw)

            now = datetime.datetime.now()

            #####IDLE RENDER

            if (settings.battcapacity >= 0 and settings.battcapacity <= settings.X728_BATT_EMERG and not settings.battloading):
                self.set_busy("Batterie leer", busytext2 = "AUS in %ds" % ((settings.lastinput - now).total_seconds() + 120))
                self.busy = True
                self.contrasthandle = False
                self.rendertime = self._rendertime
                self.keep_busy = True
                self.busyrendertime = 0.5

                if ((datetime.datetime.now() - settings.lastinput).total_seconds() > 120):
                    log(lINFO,"X728: Shutting down: Low Battery (EMERG)")
                    playout.savepos()
                    playout.pc_shutdown()


                return

            else:
                self.busyrendertime = 3
                self.contrasthandle = True

            ####setting idle text / Icon on Song Number Changed
            if (self.oldsong != self.nowplaying._song) and ((datetime.datetime.now() - settings.lastinput).total_seconds() >= 5):
                if (self.oldsong != ""):
                    playout.savepos()
                    log(lDEBUG,"Titelwechsel erkannt")
                    self.set_busy ("Titelwechsel", settings.SYMBOL_CHANGING_SONG, "%2.2d von %2.2d " % (int(self.nowplaying._song), int(self.nowplaying._playlistlength)))
                    self.busy = True

                self.oldsong = self.nowplaying._song



            #shutdowntimer ? aktiv dann Zeit anzeigen
            if settings.job_t >= 0:
                draw.text((xpos3 + 2, lineposy + 2 ), "%2.2d" % (int(settings.job_t)), font=Idle.fontsmall, fill="BLUE")
            elif settings.X728_ENABLED:
                draw.text((xpos3 + 2, lineposy + 2), settings.battsymbol, font=Idle.faicons, fill=get_battload_color())



            if ((self.nowplaying._state == "stop") or (settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or (settings.battcapacity <= settings.X728_BATT_LOW) or (settings.DISPLAY_HEIGHT > 64)):
                if (settings.battcapacity >= 0):
                    text = "Batterie: %d%%%s" % (settings.battcapacity, ", lädt." if settings.battloading else " ") if settings.battcapacity > settings.X728_BATT_LOW else "Batterie laden! %d%%" % (settings.battcapacity)
                    mwidth = Idle.font.getsize(text)
                    ungerade = (time.time() % 2) // 1
                    fill = "black" if ungerade and  settings.battcapacity <= settings.X728_BATT_LOW else  get_battload_color()
                    draw.text(((settings.DISPLAY_WIDTH/2) - (mwidth[0]/2),10), text, font=Idle.font, fill=fill)
                if settings.job_i >= 0 or settings.job_t >= 0:
                    if settings.job_i >= settings.job_t:
                        aus = settings.job_i
                    else:
                        aus = settings.job_t

                    text = "AUS in %2.2d min" %(aus)
                else:
                    text = now.strftime("%a, %d.%m.%y %H:%M")

                mwidth = Idle.font.getsize(text)

                draw.text(((settings.DISPLAY_WIDTH/2) - (mwidth[0]/2),30), "%s" % (text), font=Idle.font, fill="white")

                if settings.DISPLAY_HEIGHT <= 64:
                    return

            #Titel Scrollbar
            if Idle.font.getsize(self.nowplaying._playingtitle)[0] > settings.DISPLAY_WIDTH:
                self.titlex += 1
                if self.titlex >= len (self.nowplaying._playingtitle): self.titlex = 0
            else:
                self.titlex = 0


           ###name Scrollbar
            if Idle.font.getsize(self.nowplaying._playingname)[0] > settings.DISPLAY_WIDTH:
                self.namex += 1
                if namex >= len(self.nowplaying._playingname):
                    self.namex = 0
            else:
                self.namex = 0

            ####album scrollbar
            if Idle.font.getsize(self.nowplaying._playingalbum)[0] > settings.DISPLAY_WIDTH:
                self.albumx += 1
                if self.albumx >= len (self.nowplaying._playingalbum): self.albumx = 0

            else:
                self.albumx = 0

            draw.text((1, settings.DISPLAY_HEIGHT - 3*settings.FONT_HEIGHT_NORMAL ), self.nowplaying._playingalbum[self.albumx:], font=Idle.font, fill="white")
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
                self.set_busy("lauter",settings.SYMBOL_VOL_UP)
                playout.pc_volup(5)
            elif key == 'down' or key == '8':
                self.set_busy("leiser",settings.SYMBOL_VOL_DN)
                playout.pc_voldown(5)
            elif key == 'left' or key =='4':
                self.set_busy("zurück",settings.SYMBOL_PREV)
                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (get_folder(cfolder,-1))
                else:
                    log (lDEBUG,"idle: prev")
                    playout.pc_prev()
            elif key == 'right' or key == '6':
                self.set_busy("weiter",settings.SYMBOL_NEXT)
                if self.nowplaying._playingalbum == "Livestream":
                    cfolder = get_folder_of_livestream(self.nowplaying._playingfile)
                    playout.pc_playfolder (get_folder(cfolder,1))
                else:
                    log (lDEBUG,"idle: next")
                    playout.pc_next()
            elif key == 'A':
                settings.audio_basepath = settings.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = get_folder_from_file(settings.FILE_LAST_MUSIC)
                self.windowmanager.set_window("foldermenu")
            elif key == 'B':
                settings.audio_basepath = settings.AUDIO_BASEPATH_HOERBUCH 
                settings.currentfolder = get_folder_from_file(settings.FILE_LAST_HOERBUCH)
                self.windowmanager.set_window("foldermenu")
            elif key == 'C':
                settings.audio_basepath = settings.AUDIO_BASEPATH_RADIO
                settings.currentfolder = get_folder_from_file(settings.FILE_LAST_RADIO)
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
            elif key == 'START':
                playout.pc_toggle()

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
            elif key == 'GPI_PWR_OFF':
                self.windowmanager.set_window("ende")

        else:
            if (direction > 0):
                self.set_busy("lauter",settings.SYMBOL_VOL_UP)
                playout.pc_volup()
            else:
                self.set_busy("leiser",settings.SYMBOL_VOL_DN)
                playout.pc_voldown()
