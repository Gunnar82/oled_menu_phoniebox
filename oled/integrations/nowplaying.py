#  MBTechWorks.com 2016
#  Pulse Width Modulation (PWM) demo to cycle brightness of an LED

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
import settings
import asyncio
from  integrations.functions import get_timeouts
import integrations.playout as playout
import time

import config.symbols as symbols
import config.file_folder as cfg_file_folder
import config.online as cfg_online

import config.user_settings as csettings

from integrations.logging_config import *

logger = setup_logger(__name__)


class nowplaying:
    """Class to manage the currently playing music information."""
    filename = ""
    __oldtitle = ""
    __titlechanged = False
    output_symbol = symbols.SYMBOL_SPEAKER
    input_is_stream = False
    input_is_online = False

    _playingname = ""
    _playingtitle = ""
    _playingalbum = ""
    _playingfile = ""
    _volume = -1
    _time = -1
    _elapsed = -1
    _playlistlength = -1
    _song = -1
    _duration = -1
    _state = "starting"
    _statex = "unknown"


    async def _generatenowplaying(self):
        """Continuously generate now playing information."""
        while self.loop.is_running():
            await self.loop.run_in_executor(None,self.generatenowplaying)
            await asyncio.sleep(self.windowmanager.looptime)


    def generatenowplaying(self):
        """Fetch current playing music information and update internal state."""
        try:
            _playingtitle = ""
            playing = self.musicmanager.nowplaying()
            self.filename = playing.get('file',"")

            try:
                if "title" in playing:
                    title = playing['title']
                else:
                    title = filename[filename.rfind("/")+1:]
            except:
                title = "n/a"

            if title != self.__oldtitle:
                if self.__oldtitle:
                    if (time.monotonic() - settings.lastinput) >= csettings.DARK_TIMEOUT:
                        settings.lastinput = time.monotonic() - csettings.CONTRAST_TIMEOUT
                self.__oldtitle = title

            self._playingtitle = title

            try:
                if "name" in playing:
                    name = playing['name']
                elif "artist" in playing:
                    name = playing['artist']
                else:
                    name = "n/v"
            except:
                name = "n/a"

            self._playingname = name
            try:
                if "album" in playing:
                    album = playing['album']
                elif not playing['file'].startswith('http'):
                    album = filename[:filename.rfind('/')] #.split("/")[0]
                    album = album.replace('/',' - ')
                elif playing['file'].startswith('http'):
                    album = "Livestream"
                else:
                    album = ""
            except:
                album = ""

            self._playingalbum = album

            try:
                if ("file" in playing):
                    self._playingfile = playing['file']
                    self.input_is_stream = self._playingfile.startswith('https:','http:')
                else:
                    self._playingfile = ""
                    self.input_is_stream = False
            except:
                self.input_is_stream = False



            try:
                self.input_is_online = self._playingfile.startswith(cfg_online.ONLINE_URL)
            except Exception as error:
                self.input_is_online = False

            status = self.musicmanager.status()


            self._volume = status.get('volume',-1)
            self._elapsed = status.get('elapsed', -1)
            self._duration = status.get('duration',-1)
            self._time = status.get('time', -1)
            self._playlistlength = status.get('playlistlength', -1)
            self._song = str(int(status.get('song', -1)) + 1)
            self._state = status.get('state', "unknown")
        except Exception as error:
            logger.debug (f"nowplaying error: {error}")

    async def _linuxjob(self):
        while self.loop.is_running():
            get_timeouts()
            if ((settings.job_t >=0 and settings.job_t <= 5) or
                    (settings.job_i >= 0 and settings.job_i <= 5) or
                    ("x728" in settings.INPUTS and settings.battcapacity <= settings.X728_BATT_LOW)):
                if not "statusled" in settings.INPUTS:
                    self.windowmanager.show_window()
            await asyncio.sleep(20)


    async def _savepos_status(self):
        oldfilename = ""
        oldstate = "stop"
        oldstate = "none"

        while self.loop.is_running():
            try:
                if ((oldfilename != self.filename and self.filename and self._state != "stop" and oldstate != "stop") or
                        (oldstate != self._state and self._state in ["pause", "play"])):
                    oldfilename = self.filename
                    oldstate = self._state
                    self.__titlechanged = True
                    self.loop.run_in_executor(None,self.do_savestate)

            except Exception as error:
                logger.error (f"_savepos_status: {error}")

            await asyncio.sleep(1)

    def do_savestate(self):
        """Speichern der Aktuellen Postion ggf. online"""
        if self.input_is_stream and self.input_is_online:
            logger.debug("saving online position")
            playout.savepos_online(self)

        playout.savepos()

    def is_title_changed(self):
        """Wenn Titelwechsel und noch nicht abgefragt, true"""
        logger.debug(f"is_title_changed: {self.__titlechanged}")
        if self.__titlechanged:
            self.__titlechanged = False
            return True
        return False

    async def _output(self):

        while self.loop.is_running():
            self.output_symbol = symbols.SYMBOL_SPEAKER if  self.bluetooth.output_status(settings.ALSA_DEV_LOCAL) == "enabled" else symbols.SYMBOL_HEADPHONE
            await asyncio.sleep(5)


    def __init__(self,loop,musicmanager,windowmanager,bluetooth):
        self.bluetooth = bluetooth
        self.loop = loop
        self.musicmanager = musicmanager
        self.windowmanager = windowmanager

        self.loop.create_task(self._generatenowplaying())
        self.loop.create_task(self._linuxjob())
        self.loop.create_task(self._output())
        self.loop.create_task(self._savepos_status())


