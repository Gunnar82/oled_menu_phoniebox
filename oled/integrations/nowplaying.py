#  MBTechWorks.com 2016
#  Pulse Width Modulation (PWM) demo to cycle brightness of an LED

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
import settings
import asyncio

class nowplaying:
    filename = ""
    oldtitle = ""
    async def _generatenowplaying(self):
        try:
            filename = ""
            _playingtitle = ""

            while self.loop.is_running():
                print ("generate nowplaying")
                playing = self.musicmanager.nowplaying()
                status = self.musicmanager.status()
                filename = playing['file'] if ("file" in playing) else ""

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

                self._playingfile = playing['file'] if ("file" in playing) else ""
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

    def __init__(self,loop,musicmanager,windowmanager):
        self.loop = loop
        self.musicmanager = musicmanager
        self.windowmanager = windowmanager
        self.loop.create_task(self._generatenowplaying())
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

    def startpulse(self,count = 1):
        print (count)
        self.pulsing = count

    def stoppulse(self):
        self.pulsing = 0
        self.pwm.stop()

    def stoploop(self):
        GPIO.cleanup()                     # resets GPIO ports used back to input mode
