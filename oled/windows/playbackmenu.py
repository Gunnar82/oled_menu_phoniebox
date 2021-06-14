""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import subprocess, re

class Playbackmenu(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=10)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=8)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=16)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager)
        self._activepbm = False
        self.musicmanager = musicmanager
        self._volume = -1
        self._time = -1
        self._elapsed = -1
        self._playlistlength = -1
        self._song = -1
        self._duration = -1
        self._state = "starting"
        self.job_t = -1
        self.job_i = -1
        self.job_s = -1
        self.counter = 1

    def linux_job_remaining(self, job_name):
        cmd = ['sudo', 'atq', '-q', job_name]
        dtQueue = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
        regex = re.search('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', dtQueue)
        if regex:
            dtNow = datetime.datetime.now()
            dtQueue = datetime.datetime.strptime(dtNow.strftime("%d.%m.%Y") + " " + regex.group(5), "%d.%m.%Y %H:%M:%S")

            # subtract 1 day if queued for the next day
            if dtNow > dtQueue:
                dtNow = dtNow - datetime.timedelta(days=1)

            return int(round((dtQueue.timestamp() - dtNow.timestamp()) / 60, 0))
        else:
            return -1


    def to_min_sec(self, seconds):
        mins = int(float(seconds) // 60)
        secs = int(float(seconds) - (mins*60))
        return "%2.2d:%2.2d" % (mins,secs)


    def activate(self):
        self._activepbm = True
        self.loop.create_task(self._generatenowplaying())
        self.loop.create_task(self._linuxjob())
        self.counter = 1

    def deactivate(self):
        self._activepbm = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()


            #Trennleiste waagerecht
            draw.rectangle((0,49,128,49),outline="white",fill="white")
            #Trennleisten senkrecht
            draw.rectangle((19,49,19,64),outline="white",fill="white")
            draw.rectangle((55,49,55,64),outline="white",fill="white")
            draw.rectangle((90,49,90,64),outline="white",fill="white")

            #volume
            draw.text((1, 51 ), str(self._volume), font=Playbackmenu.fontsmall, fill="white")

            #Buttons
            if self.musicmanager.source == "mpd":
                try:
                    if self._state == "play":
                        #elapsed
                        draw.text((25, 51 ), self.to_min_sec(self._elapsed), font=Playbackmenu.fontsmall, fill="white")#play
                    else:
                        draw.text((25, 51 ), self._state, font=Playbackmenu.fontsmall, fill="white")

                except KeyError:
                    print ("err")


            #Widgets
            if not self.musicmanager.mopidyconnection.connected:
                draw.text((18, 2), "\uf071", font=Playbackmenu.faicons, fill="white")

            try:
                if float(self._duration) >= 0:
                    timelinepos = int(float(self._elapsed) / float(self._duration)  * 128) # TODO Device.with
                else:
                    timelinepos = 128 # device.width
            except:
                timelinepos = 128

            #Fortschritssleiste Wiedergabe
            draw.rectangle((0,0,timelinepos,1),outline="white",fill="white")


            #Currently playing song
            #Line 1 2 3


            #paylistpos
            draw.text((60, 51 ), "%2.2d/%2.2d" % (int(self._song), int(self._playlistlength)), font=Playbackmenu.fontsmall, fill="white")

            #shutdowntimer ? aktiv dann Zeit anzeigen
            if self.job_t >= 0:
                draw.text((95, 51 ), "%2.2d" % (int(self.job_t)), font=Playbackmenu.fontsmall, fill="white")


            #draw.text((10,10),"CONTROLS", font=Idle.bigfong, fill="white")
            #draw.text((18, 2), "\uf071", font=Playbackmenu.faicons, fill="white")

            #selection line
            draw.line((10+(self.counter)*20, 42, 30+(self.counter)*20, 42), width=2, fill="white")

            draw.text((10, 20), "\uf048", font=Playbackmenu.faiconsbig, fill="white") #prev
            if self._state == "play":
                draw.text((30, 20), "\uf04c", font=Playbackmenu.faiconsbig, fill="white") #pause
            elif self._state == "pause":
                draw.text((30, 20), "\uf04b", font=Playbackmenu.faiconsbig, fill="white") #play
            else:
                draw.text((30, 20), "\uf04d", font=Playbackmenu.faiconsbig, fill="white") #play
            draw.text((50, 20), "\uf062", font=Playbackmenu.faiconsbig, fill="white") #menu
            draw.text((70, 20), "\uf0a8", font=Playbackmenu.faiconsbig, fill="white") #menu
            draw.text((90, 20), "\uf051", font=Playbackmenu.faiconsbig, fill="white") #next


    async def _linuxjob(self):

        while self.loop.is_running() and self._activepbm:
            self.job_t = self.linux_job_remaining("t")
            self.job_s = self.linux_job_remaining("s")
            self.job_i = self.linux_job_remaining("i")

            await asyncio.sleep(20)


    async def _generatenowplaying(self):
        namex = 0
        albumx = 0
        titlex = 0
        oldname = ""
        oldtitle = ""
        oldalbum = ""
        filename = ""

        while self.loop.is_running() and self._activepbm:

            playing = self.musicmanager.nowplaying()
            status = self.musicmanager.status()
            filename = playing['file'] if ("file" in playing) else ""
            #print (playing)
            #print(status)


            self._volume = status['volume'] if ("volume" in status) else -1
            self._elapsed = status['elapsed'] if ("elapsed" in status) else -1
            self._time = status['time'] if ("time" in status) else -1
            self._playlistlength = status['playlistlength'] if ("playlistlength" in status) else -1
            self._song = str(int(status['song']) + 1) if ("song" in status) else -1
            self._duration = status['duration'] if ("duration" in status) else -1
            self._state = status['state'] if ("state" in status) else "unknown"
            
            await asyncio.sleep(0.25)

    def push_callback(self):
        if self.counter == 1:
            os.system("/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerpause")
        elif self.counter == 2:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 3:
            self.windowmanager.set_window("idle")
             

        #self._showcontrols = False
        #self.windowmanager.set_window("mainmenu")
        #elif self.counter == 1:
        #    self.musicmanager.previous()
        #elif self.counter == 2:
        #    self.musicmanager.playpause()
        #elif self.counter == 3:
        #    self.musicmanager.next()

    def turn_callback(self, direction):
        if (self.counter + direction <= 4 and self.counter + direction >= 0):
            self.counter += direction
            
        if self.counter == 0 and direction < 0:
            self.counter = 1
            os.system("/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerprev")

        if self.counter == 4 and direction > 0:
            self.counter = 3
            os.system("/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playernext")
        #os.system("mpc volume {}{} > /dev/null".format(plus,direction))
        #if self.counter + direction <= 0 and self.counter + direction >= 0:
            #self.counter += direction
