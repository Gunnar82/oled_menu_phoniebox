""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import subprocess, re
import integrations.bluetooth
import integrations.playout
import RPi.GPIO as GPIO



class Idle(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=10)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=8)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=12)

    def __init__(self, windowmanager, musicmanager):
        super().__init__(windowmanager)
        self._active = False
        self.musicmanager = musicmanager
        self._playingname = ""
        self._playingtitle = ""
        self._playingalbum = ""
        self._volume = -1
        self._time = -1
        self._elapsed = -1
        self._playlistlength = -1
        self._song = -1
        self._duration = -1
        self._state = "starting"
        self._statex = "unknown"
        self.job_t = -1
        self.job_i = -1
        self.job_s = -1
        self.Type="Default"
        self.LocalOutputEnabled = False
        self.BluetoothFound = False
        self.loop.create_task(self._find_dev_bt())
        if settings.STATUS_LED_ENABLED:
            GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
            GPIO.setup(settings.STATUS_LED_PIN, GPIO.OUT)
            if settings.STATUS_LED_ALWAYS_ON:
                GPIO.output(settings.STATUS_LED_PIN, 1) 


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
        self._active = True
        self.loop.create_task(self._generatenowplaying())
        self.loop.create_task(self._linuxjob())

    def deactivate(self):
        self._active = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()

            if self.BluetoothFound == True:
                draw.text((115,5), "\uf293", font=Idle.faiconsbig, fill="white")
            else:
                draw.text((115,5), "\uf294", font=Idle.faiconsbig, fill="white")




            #Trennleiste waagerecht
            draw.rectangle((0,49,128,49),outline="white",fill="white")
            #Trennleisten senkrecht
            draw.rectangle((19,49,19,64),outline="white",fill="white")
            draw.rectangle((55,49,55,64),outline="white",fill="white")
            draw.rectangle((95,49,95,64),outline="white",fill="white")

            #volume
            draw.text((1, 51 ), str(self._volume), font=Idle.fontsmall, fill="white")

            #Buttons
            if self.musicmanager.source == "mpd":
                try:
                    if self._state == "play":
                        #elapsed
                        draw.text((25, 51 ), self.to_min_sec(self._elapsed), font=Idle.fontsmall, fill="white")
                        if self._statex != self._state:
                            self._statex = self._state
                            if settings.STATUS_LED_ENABLED and not settings.STATUS_LED_ALWAYS_ON:
                                GPIO.output(settings.STATUS_LED_PIN, 0) 
                    else:
                        draw.text((25, 51), self._state, font=Idle.fontsmall, fill="white") #other than play
                        if self._statex != self._state:
                            self._statex = self._state
                            if settings.STATUS_LED_ENABLED:
                                GPIO.output(settings.STATUS_LED_PIN, 1) 

                except KeyError:
                    pass
            

            #Widgets
            if not self.musicmanager.mopidyconnection.connected:
                draw.text((18, 2), "\uf071", font=Idle.faicons, fill="white")

            #Current time
            #draw.text((62, -1), now.strftime("%H:%M"), font=Idle.clockfont, fill="white")

            #Currently playing song
            #Line 1 2 3
            if float(self._duration) >= 0:
                timelinepos = int(float(self._elapsed) / float(self._duration)  * 128) # TODO Device.with
            else:
                timelinepos = 128 # device.width
            #Fortschritssleiste Wiedergabe
            draw.rectangle((0,0,timelinepos,1),outline="white",fill="white")


            #paylistpos
            draw.text((60, 51 ), "%2.2d/%2.2d" % (int(self._song), int(self._playlistlength)), font=Idle.fontsmall, fill="white")

            #shutdowntimer ? aktiv dann Zeit anzeigen
            if self.job_t >= 0:
                draw.text((100, 51 ), "%2.2d" % (int(self.job_t)), font=Idle.fontsmall, fill="white")


            if ((self._state == "stop") or (self.job_t >=0 and self.job_t <= 5) or (self.job_i >= 0 and self.job_i <=5)):
                if self.job_i >= 0:
                    draw.text((1,1), "i: " +  str(self.job_i) + "m", font=Idle.bigfont, fill="white") 
                if self.job_t >= 0:
                    draw.text((64,1), "t: " +  str(self.job_t) + "m", font=Idle.bigfont, fill="white") 
                return


            draw.text((1, 5), self._playingalbum, font=Idle.font, fill="white")
            draw.text((1, 19), self._playingname, font=Idle.font, fill="white")
            draw.text((1, 32), self._playingtitle, font=Idle.font, fill="white")




    async def _linuxjob(self):

        while self.loop.is_running() and self._active:
            self.job_t = self.linux_job_remaining("t")
            self.job_s = self.linux_job_remaining("s")
            self.job_i = self.linux_job_remaining("i")

            await asyncio.sleep(20)


    async def _find_dev_bt(self):
        await asyncio.sleep(30)

        if integrations.bluetooth.check_dev_bt():
            self.BluetoothFound = True
            #integrations.bluetooth.enable_dev_bt()
        else:
            if not self.LocalOutputEnabled:
    
                integrations.bluetooth.enable_dev_local()
    
                self.LocalOutputEnabled = True


    async def _generatenowplaying(self):
        namex = 0
        albumx = 0
        titlex = 0
        oldname = ""
        oldtitle = ""
        oldalbum = ""
        filename = ""

        while self.loop.is_running() and self._active:

            playing = self.musicmanager.nowplaying()
            status = self.musicmanager.status()
            filename = playing['file'] if ("file" in playing) else ""
            #print (playing)
            #print(status)


            try:
                if "name" in playing:
                    name = playing['name']
                elif "artist" in playing:
                    name = playing['artist']
                else:
                    name = "n/v"
            except:
                name = "n/a"

            if name == oldname and Idle.font.getsize(name[namex:])[0] > 127:
                namex += 1
            else:
                namex = 0
                oldname = name

            self._playingname = name[namex:]

            try:
                if "album" in playing:
                    album = playing['album']
                elif not playing['file'].startswith('http'):
                    album = filename[:filename.rfind('/')] #.split("/")[0]
                    album = album.replace('/',' - ')
                elif playing['file'].startswith('http'):
                    album = "WebRadio"
                else:
                    album = ""
            except:
                album = ""

            if album == oldalbum and Idle.font.getsize(album[albumx:])[0] > 115:
                albumx += 1
            else:
                albumx = 0
                oldalbum = album

            self._playingalbum = album[albumx:albumx+19]


            try:
                if "title" in playing:
                    title = playing['title']
                else:
                    title = filename[filename.rfind("/")+1:]
            except:
                title = "n/a"

            self._volume = status['volume'] if ("volume" in status) else -1
            self._elapsed = status['elapsed'] if ("elapsed" in status) else -1
            self._time = status['time'] if ("time" in status) else -1
            self._playlistlength = status['playlistlength'] if ("playlistlength" in status) else -1
            self._song = str(int(status['song']) + 1) if ("song" in status) else -1
            self._duration = status['duration'] if ("duration" in status) else -1
            self._state = status['state'] if ("state" in status) else "unknown"
            
            if title == oldtitle and Idle.font.getsize(title[titlex:])[0] > 127:
                titlex += 1
            else:
                titlex = 0
                oldtitle = title
            self._playingtitle = title[titlex:]
        

            await asyncio.sleep(1)

    def push_callback(self,lp=False):
        if lp:
            self.windowmanager.set_window("shutdownmenu")
        else:
            self.windowmanager.set_window("playbackmenu")


                #self._showcontrols = False
            #self.windowmanager.set_window("mainmenu")
        #elif self.counter == 1:
        #    self.musicmanager.previous()
        #elif self.counter == 2:
        #    self.musicmanager.playpause()
        #elif self.counter == 3:
        #    self.musicmanager.next()

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up':
                os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumeup")
            elif key == 'down':
                os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumedown")
            elif key == 'left':
                integrations.playout.pc_prev()
            else:
                integrations.playout.pc_next()
        else:
            if (direction > 0):
                os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumeup")
            else:
                os.system("sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=volumedown")