#  MBTechWorks.com 2016
#  Pulse Width Modulation (PWM) demo to cycle brightness of an LED

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
import settings
import asyncio
from  integrations.functions import  ping_test
import integrations.playout as playout
from integrations.webrequest import WebRequest

import time
from pathlib import Path

import config.symbols as symbols
import config.file_folder as cfg_file_folder
import config.online as cfg_online

from integrations.logging_config import *

logger = setup_logger(__name__)
#logger = setup_logger(__name__,lvlDEBUG)


class nowplaying:
    """Class to manage the currently playing music information."""
    filename = ""
    __oldtitle = ""
    __titlechanged = False
    __onlinestate = False
    output_symbol = symbols.SYMBOL_SPEAKER

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




    def __init__(self,loop,musicmanager,windowmanager,bluetooth,usersettings):
        self.usersettings = usersettings
        self.bluetooth = bluetooth
        self.loop = loop
        self.musicmanager = musicmanager
        self.windowmanager = windowmanager

        self.loop.create_task(self._generatenowplaying())
        self.loop.create_task(self.__systemabfrage())
        self.loop.create_task(self._savepos_status())


    async def _generatenowplaying(self):
        """Continuously generate now playing information."""
        while self.loop.is_running():
            self.loop.run_in_executor(None,self.generatenowplaying)
            await asyncio.sleep(self.windowmanager.looptime)


    def generatenowplaying(self):
        """Fetch current playing music information and update internal state."""
        try:
            logger.debug("generatenowplaying started")
            _playingtitle = ""
            playing = self.musicmanager.nowplaying()
            logger.debug(f"playing: {playing}")
            self.filename = playing.get("file","")

            try:
                if "title" in playing:
                    title = playing['title']
                else:
                    title = self.filename[self.filename.rfind("/")+1:]
            except Exception as error:
                logger.debug(f"itle error : {error}")
                title = n/a

            if title != self.__oldtitle:
                #if self.__oldtitle:
                    #if (time.monotonic() - settings.lastinput) >= self.usersettings.DARK_TIMEOUT:
                        #settings.lastinput = time.monotonic() - self.usersettings.CONTRAST_TIMEOUT
                self.__oldtitle = title

            self._playingtitle = title

            try:
                if "name" in playing:
                    name = playing['name']
                elif "artist" in playing:
                    name = playing['artist']
                else:
                    name = os.path.dirname(os.path.dirname(self.filename)).replace('/',' . ')
            except:
                name = "n/a"

            self._playingname = name

            try:
                if "album" in playing:
                    album = playing['album']
                elif not playing['file'].startswith('http'):
                    album = Path(self.filename).parent.name
                elif playing['file'].startswith('http'):
                    album = "Livestream"
                else:
                    album = ""
            except Exception as error:
                album = ""

            self._playingalbum = album

            try:
                if ("file" in playing):
                    self._playingfile = playing["file"]
                else:
                    self._playingfile = ""
            except:
                pass


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
        finally:
            logger.debug("generatenowplaying ends")


    async def _savepos_status(self):
        oldfilename = ""
        oldstate = "stop"
        oldstate = "none"
        last_online_save = time.monotonic()
        while self.loop.is_running():
            try:
                if ((oldfilename != self.filename and self.filename and self._state != "stop" and oldstate != "stop") or
                        (oldstate != self._state and self._state in ["pause", "play"])):
                    oldfilename = self.filename
                    oldstate = self._state
                    self.__titlechanged = True
                    self.loop.run_in_executor(None,self.do_savestate,False)

                if time.monotonic() - last_online_save > 60 and self._state in ["play","playing"]:
                    last_online_save = time.monotonic()
                    self.loop.run_in_executor(None,self.do_savestate,True)



            except Exception as error:
                logger.error (f"_savepos_status: {error}")

            await asyncio.sleep(1)

    def do_savestate(self,only_online):
        """Speichern der Aktuellen Postion ggf. online"""
        if self.input_is_online():
            logger.debug("saving online position")
            playout.savepos_online(self)
        else:
            self.musicmanager.save_playback()

    def is_title_changed(self):
        """Wenn Titelwechsel und noch nicht abgefragt, true"""
        logger.debug(f"is_title_changed: {self.__titlechanged}")
        if self.__titlechanged:
            self.__titlechanged = False
            return True
        return False

    async def __systemabfrage(self):

        while self.loop.is_running():
            try:
                self.output_symbol = symbols.SYMBOL_SPEAKER if not self.bluetooth.output_is_bluez() else symbols.SYMBOL_HEADPHONE
            except:
                self.output_symbol = symbols.SYMBOL_SPEAKER

            await self.loop.run_in_executor(None,self.check_online_state)
            await asyncio.sleep(10)

    def check_online_state(self):
        if self.usersettings.ONLINE_URL_TEST:
            try:
                url = "http://localhost:8080/savepos/online.php"  # Beispiel-URL
                request = WebRequest(url, method="get")
                state = False
                response_code = request.get_response_code()
                logger.debug(f"check_online_state: response_code {response_code}")
                if response_code == 200:
                    response = request.get_response_text()
                    lines = response.strip().splitlines()
                    kv_pairs = dict(line.split("=", 1) for line in lines if "=" in line)

                    # Prüfe auf online=yes
                    if kv_pairs.get("online", "").lower() == "yes":
                        logger.debug(f"check_online_state: response {response}")
                        logger.debug("check_online_state: online=true")
                        state = True
            except Exception as error:
                logger.debug(f"check_online_state: {error}")
                state = False
        else:
            state = ping_test()

        logger.debug(f"is_online: {state}")
        self.__onlinestate = state


    def is_device_online(self):
        return self.__onlinestate



    def input_is_stream(self):
        try:
             return self._playingfile.startswith(('https:','http:'))
        except Exception as error:
            logger.debug(f"input_is_online: error: {error}")
            return False

    def input_is_online(self):
        try:
            return self._playingfile.startswith(cfg_online.ONLINE_URL)
        except Exception as error:
            return False
