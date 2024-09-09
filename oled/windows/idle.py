""" IDLE screen """
import datetime
import asyncio
from ui.mainwindow import MainWindow
import settings
import logging

from integrations.logging_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


import config.colors as colors
import config.symbols as symbols

import config.file_folder as cfg_file_folder
from luma.core.render import canvas
from PIL import ImageFont
import os
import RPi.GPIO as GPIO
import locale
import time

import integrations.bluetooth
import integrations.playout as playout

from integrations.functions import get_battload_color, to_min_sec, get_folder, get_folder_of_livestream, get_folder_from_file





class Idle(MainWindow):

    def __init__(self, windowmanager, loop, nowplaying):
        super().__init__(windowmanager, loop, nowplaying)
        self.changerender = True
        self.window_on_back = "playlistmenu"

    def activate(self):
        self.titlex = 0
        self.namex = 0
        self.albumx = 0

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
                    logger.info("X728: Shutting down: Low Battery (EMERG)")
                    playout.savepos_online(self.nowplaying)
                    playout.savepos()
                    playout.pc_shutdown()


                return

            else:
                self.busyrendertime = 3
                self.contrasthandle = True

            ####setting idle text / Icon on Song Number Changed
            try:
                if ((now - self.nowplaying.lasttitlechange ).total_seconds() < 3):
                    logger.debug("Titelwechsel erkannt")
                    self.set_busy ("Titelwechsel", symbols.SYMBOL_CHANGING_SONG, "%2.2d von %2.2d " % (int(self.nowplaying._song), int(self.nowplaying._playlistlength)))
                    self.busy = True
            except Exception as error:
                print (error)

            if ((self.nowplaying._state == "stop") or (settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or (0 <= settings.battcapacity <= settings.X728_BATT_LOW) or (settings.DISPLAY_HEIGHT > 64)):
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
                if self.namex >= len(self.nowplaying._playingname):
                    self.namex = 0
            else:
                self.namex = 0

            ####album scrollbar
            if Idle.font.getsize(self.nowplaying._playingalbum)[0] > settings.DISPLAY_WIDTH:
                self.albumx += 1
                if self.albumx >= len (self.nowplaying._playingalbum): self.albumx = 0

            else:
                self.albumx = 0

            draw.text((1, settings.DISPLAY_HEIGHT - 3*settings.IDLE_LINE_HEIGHT ), self.nowplaying._playingalbum[self.albumx:], font=Idle.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 4*settings.IDLE_LINE_HEIGHT ), self.nowplaying._playingname[self.namex:], font=Idle.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 5*settings.IDLE_LINE_HEIGHT ), self.nowplaying._playingtitle[self.titlex:], font=Idle.font, fill="white")




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

    async def change_folder(self,direction):
        await asyncio.sleep(1)
        cfolder = get_folder_of_livestream(self.nowplaying._playingfile)
        dfolder = get_folder(cfolder,direction)

        if not cfolder.endswith(dfolder):
            playout.pc_playfolder (dfolder)

        self.set_busy(dfolder[dfolder.rindex("/")+1:])


    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                playout.pc_volup(5)
                self.set_busy("lauter",symbols.SYMBOL_VOL_UP)
            elif key == 'down' or key == '8':
                playout.pc_voldown(5)
                self.set_busy("leiser",symbols.SYMBOL_VOL_DN)

            elif key in ['left','4']:
                if self.nowplaying.input_is_stream and not self.nowplaying.input_is_online and self.nowplaying._song >= self.nowplaying._playlistlength:
                    self.set_busy("Vorheriger Sender",symbols.SYMBOL_PREV)
                    self.loop.create_task(self.change_folder(-1))
                else:
                    if float(self.nowplaying._elapsed) > 10:
                        self.set_busy("Neustart Track",symbols.SYMBOL_PREV)
                        logger.debug("idle: seek 0")
                        playout.pc_seek0()
                    elif int(self.nowplaying._song) > 1:
                        self.set_busy("Zurück",symbols.SYMBOL_PREV)
                        logger.debug("idle: prev")
                        playout.pc_prev()
                    else:
                        self.set_busy("Erster Titel",symbols.SYMBOL_FAIL)

            elif key in ['right', '6']:
                print (self.nowplaying)
                if self.nowplaying.input_is_stream and not self.nowplaying.input_is_online and self.nowplaying._song <= self.nowplaying._playlistlength:
                    self.set_busy("Nächster Sender",symbols.SYMBOL_NEXT)
                    self.loop.create_task(self.change_folder(1))
                else:
                    if int(self.nowplaying._song) < int(self.nowplaying._playlistlength):
                        self.set_busy("Weiter",symbols.SYMBOL_NEXT)
                        logger.debug("idle: next")
                        playout.pc_next()
                    else:
                        self.set_busy("Letzter Titel",symbols.SYMBOL_FAIL)

            elif key == 'A' or key == 'Y':
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = get_folder_from_file(cfg_file_folder.FILE_LAST_MUSIC)
                self.windowmanager.set_window("foldermenu")
            elif key == 'B':
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_HOERBUCH 
                settings.currentfolder = get_folder_from_file(cfg_file_folder.FILE_LAST_HOERBUCH)
                self.windowmanager.set_window("foldermenu")
            elif key == 'C' or key == 'X':
                settings.audio_basepath = cfg_file_folder.AUDIO_BASEPATH_RADIO
                settings.currentfolder = get_folder_from_file(cfg_file_folder.FILE_LAST_RADIO)
                self.windowmanager.set_window("foldermenu")
            elif key in  ['D','hl']:
                self.windowmanager.set_window("downloadmenu")
            elif key =='0':
                self.windowmanager.set_window("shutdownmenu")
            elif key =='9' or key == 'select':
                self.windowmanager.set_window("lock")
            elif key == '5':
                 self.windowmanager.clear_window()
            #elif key == '0':
            #    self.busysymbol = symbols.SYMBOL_VOL_MUTE
            #    playout.pc_mute()
            elif key == 'start':
                playout.pc_toggle()
            elif key == 'TODO':
                self.windowmanager.windows["downloadmenu"].direct_play_last_folder = True
                self.windowmanager.set_window("downloadmenu")

            elif key in ['1', '3', '7','hr']:
                if key == '1' or key == 'hr':
                    what = cfg_file_folder.FILE_LAST_HOERBUCH
                elif key == '3':
                    what = cfg_file_folder.FILE_LAST_RADIO
                elif key == '7':
                    what = cfg_file_folder.FILE_LAST_MUSIC

                if playout.checkfolder(what) != 0:
                    self.set_busy("Fehler",symbols.SYMBOL_ERROR,what)
                else:
                    try:
                        with open(what) as f:
                            content = f.read()
                    except:
                        content = "Fehler"

                    self.set_busy(what.split("/")[-1],symbols.SYMBOL_PASS,content,busyrendertime=5)
                    self.loop.create_task(self.playlast(what))
        else:
            if (direction > 0):
                self.set_busy("lauter",symbols.SYMBOL_VOL_UP)
                playout.pc_volup()
            else:
                self.set_busy("leiser",symbols.SYMBOL_VOL_DN)
                playout.pc_voldown()

    async def playlast(self,what):
        await asyncio.sleep(1)
        playout.playlast_checked(what)
