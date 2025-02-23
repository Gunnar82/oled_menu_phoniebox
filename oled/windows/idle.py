""" IDLE screen """
from datetime import datetime
import asyncio
from ui.mainwindow import MainWindow
import settings

import config.colors as colors
import config.symbols as symbols
import config.shutdown_reason as SR

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

from integrations.logging_config import *

logger = setup_logger(__name__)


class Idle(MainWindow):

    def __init__(self, windowmanager, loop, nowplaying,musicmanager):
        super().__init__(windowmanager, loop, nowplaying)
        self.changerender = True
        self.musicmanager = musicmanager
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
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")  # Löscht den Hintergrund
            super().render(draw)

            now = time.monotonic()

            #####IDLE RENDER

            if (settings.battcapacity >= 0 and settings.battcapacity <= settings.X728_BATT_EMERG and not settings.battloading):
                self.set_busyinfo(item=["Batterie leer", "AUS in %ds" % ((settings.lastinput - now) + 120)])
                self.busy = True
                self.contrasthandle = False
                self.rendertime = self._rendertime
                self.keep_busy = True
                self.busyrendertime = 0.5

                if ((now - settings.lastinput) > 120):
                    logger.info("X728: Shutting down: Low Battery (EMERG)")
                    settings.shutdown_reason = SR.SR2
                    self.windowmanager.set_window("ende")


                return

            else:
                self.busyrendertime = 3
                self.contrasthandle = True

            ####setting idle text / Icon on Song Number Changed
            try:
                if self.nowplaying.is_title_changed():
                    logger.debug("Titelwechsel erkannt")
                    self.set_busyinfo(item = ["Titelwechsel", "%2.2d von %2.2d " % (int(self.nowplaying._song), int(self.nowplaying._playlistlength))], symbol = symbols.SYMBOL_CHANGING_SONG)
            except Exception as error:
                logger.debug(f"{error}")

            if ((self.nowplaying._state == "stop") or (settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or (0 <= settings.battcapacity <= settings.X728_BATT_LOW) or (settings.DISPLAY_HEIGHT > 64)):
                if (settings.battcapacity >= 0):
                    text = "Batterie: %d%%%s" % (settings.battcapacity, ", lädt." if settings.battloading else " ") if settings.battcapacity > settings.X728_BATT_LOW else "Batterie laden! %d%%" % (settings.battcapacity)
                    mwidth = Idle.font.getsize(text)
                    ungerade = (now % 2) // 1
                    fill = "black" if ungerade and  settings.battcapacity <= settings.X728_BATT_LOW and not settings.battloading else  get_battload_color()
                    draw.text(((settings.DISPLAY_WIDTH/2) - (mwidth[0]/2),10), text, font=Idle.font, fill=fill)
                if settings.job_i >= 0 or settings.job_t >= 0:
                    if settings.job_i >= settings.job_t:
                        aus = settings.job_i
                    else:
                        aus = settings.job_t

                    text = "AUS in %2.2d min" %(aus)
                else:
                    text = datetime.now().strftime("%a, %d.%m.%y %H:%M")

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

        self.set_busyinfo(dfolder[dfolder.rindex("/")+1:])


    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                playout.pc_volup(5)
                self.set_busyinfo(item="lauter",symbol=symbols.SYMBOL_VOL_UP)
            elif key == 'down' or key == '8':
                playout.pc_voldown(5)
                self.set_busyinfo(item="leiser",symbol=symbols.SYMBOL_VOL_DN)

            elif key in ['left','4']:
                if self.nowplaying.input_is_stream() and not self.nowplaying.input_is_online() and self.nowplaying._song >= self.nowplaying._playlistlength:
                    self.set_busyinfo(item="Vorheriger Sender",symbol=symbols.SYMBOL_PREV)
                    self.loop.create_task(self.change_folder(-1))
                else:
                    if time.monotonic() - settings.lastinput > 10 or float(self.nowplaying._elapsed) > 20:
                        logger.debug("idle: seek 0")
                        self.set_busyinfo(item="Neustart Track",symbol=symbols.SYMBOL_PREV)
                        playout.pc_seek0()
                    elif int(self.nowplaying._song) > 1:
                        self.set_busyinfo(item="Zurück",symbol=symbols.SYMBOL_PREV)
                        logger.debug("idle: prev")
                        self.musicmanager.prev()
                    else:
                        self.set_busyinfo(item="Erster Titel",symbol=symbols.SYMBOL_FAIL)

            elif key in ['right', '6']:
                if self.nowplaying.input_is_stream() and not self.nowplaying.input_is_online() and self.nowplaying._song <= self.nowplaying._playlistlength:
                    self.set_busyinfo(item="Nächster Sender",symbol=symbols.SYMBOL_NEXT)
                    self.loop.create_task(self.change_folder(1))
                else:
                    if int(self.nowplaying._song) < int(self.nowplaying._playlistlength):
                        logger.debug("idle: next")
                        playout.pc_next()
                        self.set_busyinfo(item="Weiter",symbol=symbols.SYMBOL_NEXT)
                    else:
                        self.set_busyinfo(item="Letzter Titel",symbol=symbols.SYMBOL_FAIL)

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
            elif key.lower() in ['start']:
                self.musicmanager.playpause()
            elif key == 'TODO':
                self.windowmanager.windows["downloadmenu"].direct_play_last_folder = True
                self.windowmanager.set_window("downloadmenu")

            elif key in ['1', '3', '7','hr']:
                if key == '1' or key == 'hr':
                    what = 'Hörspiele'
                elif key == '3':
                    what = 'http'
                elif key == '7':
                    what = 'Musik'

                self.loop.create_task(self.playlast(what))
        else:
            if (direction > 0):
                self.set_busyinfo(item="lauter",symbol=symbols.SYMBOL_VOL_UP)
                playout.pc_volup()
            else:
                self.set_busyinfo(item="leiser",symbol=symbols.SYMBOL_VOL_DN)
                playout.pc_voldown()

    async def playlast(self,what):
        await asyncio.sleep(1)
        self.musicmanager.play_latest_folder(what)
