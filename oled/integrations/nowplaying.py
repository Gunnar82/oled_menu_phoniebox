#  MBTechWorks.com 2016
#  Pulse Width Modulation (PWM) demo to cycle brightness of an LED

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
import settings
import asyncio
from  integrations.functions import get_timeouts
import datetime

import config.symbols as symbols
import config.file_folder as cfg_file_folder
import config.online as cfg_online

class nowplaying:
    filename = ""
    oldtitle = ""
    output_symbol = symbols.SYMBOL_SPEAKER
    input_is_stream = False
    input_is_online = False

    async def _generatenowplaying(self):
        try:
            self.filename = ""
            _playingtitle = ""
            while self.loop.is_running():
                playing = self.musicmanager.nowplaying()
                status = self.musicmanager.status()
                self.filename = playing['file'] if ("file" in playing) else ""

                try:
                    if "title" in playing:
                        title = playing['title']
                    else:
                        title = filename[filename.rfind("/")+1:]
                except:
                    title = "n/a"

                if title != self.oldtitle:
                    if self.oldtitle != "":
                        if (datetime.datetime.now() - settings.lastinput).total_seconds() >= settings.DARK_TIMEOUT:
                            settings.lastinput = datetime.datetime.now() - datetime.timedelta(seconds=settings.CONTRAST_TIMEOUT)
                    self.oldtitle = title
                    

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
                        if self._playingfile.startswith(('https:','http:')):
                            self.input_is_stream = True
                    else:
                        self._playingfile = ""
                        self.input_is_stream = False
                except:
                    self.input_is_stream = False


                try:
                    if self._playingfile.startswith(cfg_online.ONLINE_URL):
                        self.input_is_online = True
                    else:
                        self.input_is_online = False
                except:
                    self.input_is_online = False

                self._volume = status['volume'] if ("volume" in status) else -1
                self._elapsed = status['elapsed'] if ("elapsed" in status) else -1
                self._time = status['time'] if ("time" in status) else -1
                self._playlistlength = status['playlistlength'] if ("playlistlength" in status) else -1
                self._song = str(int(status['song']) + 1) if ("song" in status) else -1
                self._duration = status['duration'] if ("duration" in status) else -1
                self._state = status['state'] if ("state" in status) else "unknown"
                await asyncio.sleep(self.windowmanager.looptime)
        except:
            pass

    async def _linuxjob(self):

        while self.loop.is_running():
            get_timeouts()

            if ((settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or ("x728" in settings.INPUTS and settings.battcapacity <= settings.X728_BATT_LOW)):
                if not "statusled" in settings.INPUTS:
                    self.windowmanager.show_window()

            await asyncio.sleep(20)


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
        self._playingname = ""
        self._playingtitle = ""
        self._playingalbum = ""
        self._playingfile = ""
        self._volume = -1
        self._time = -1
        self._elapsed = -1
        self._playlistlength = -1
        self._song = -1
        self._duration = -1
        self._state = "starting"
        self._statex = "unknown"


