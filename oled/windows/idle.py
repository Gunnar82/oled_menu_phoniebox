""" IDLE screen """
import datetime
import asyncio
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.bluetooth
import integrations.playout as playout
import integrations.functions as fn
import RPi.GPIO as GPIO
import locale
import time

if settings.X728_ENABLED:
    import integrations.x728v21 as x728


class Idle(WindowBase):
    bigfont = ImageFont.truetype(settings.FONT_CLOCK, size=22)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontsmall = ImageFont.truetype(settings.FONT_TEXT, size=10)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=8)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=12)

    def __init__(self, windowmanager, musicmanager):
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
        super().__init__(windowmanager)
        self._active = False
        self.musicmanager = musicmanager
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
        self.timeout=False
        self.LocalOutputEnabled = False
        self.BluetoothFound = False
        self.window_on_back = "playlistmenu"
        self.battsymbol = ""
        self.battcapacity = -1

        #self.loop.create_task(self._find_dev_bt())
        if settings.STATUS_LED_ENABLED:
            GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
            GPIO.setup(settings.STATUS_LED_PIN, GPIO.OUT)
            if settings.STATUS_LED_ALWAYS_ON:
                GPIO.output(settings.STATUS_LED_PIN, 1) 

    async def _linuxjob(self):

        while self.loop.is_running():
            settings.job_t = fn.linux_job_remaining("t")
            settings.job_s = fn.linux_job_remaining("s")
            settings.job_i = fn.linux_job_remaining("i")

            if settings.X728_ENABLED:
                self.battsymbol = x728.getSymbol()
                self.battcapacity = x728.readCapacity()

            if ((settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or (self.battcapacity <= settings.X728_BATT_LOW)):
                self.windowmanager.show_window()

            await asyncio.sleep(20)


    def activate(self):
        self._active = True
        self.loop.create_task(self._generatenowplaying())
        self.loop.create_task(self._linuxjob())


    def deactivate(self):
        self._active = False

    def render(self):
        with canvas(self.device) as draw:
            now = datetime.datetime.now()

            if settings.X728_ENABLED:
                draw.text((110,52), self.battsymbol, font=Idle.faiconsbig, fill="white")



            #Trennleiste waagerecht
            draw.rectangle((0,49,128,49),outline="white",fill="white")
            #Trennleisten senkrecht
            draw.rectangle((16,49,16,64),outline="white",fill="white")
            draw.rectangle((65,49,65,64),outline="white",fill="white")
            draw.rectangle((105,49,105,64),outline="white",fill="white")

            #volume
            draw.text((1, 51 ), str(self._volume), font=Idle.fontsmall, fill="white")

            #Buttons
            if self.musicmanager.source == "mpd":
                try:
                    if self._state == "play":
                        #elapsed
                        _spos = fn.to_min_sec(self._elapsed)
                        _xpos = 41 - int(Idle.fontsmall.getsize(_spos)[0]/2)

                        draw.text((_xpos, 51 ),_spos, font=Idle.fontsmall, fill="white")
                        if self._statex != self._state:
                            self._statex = self._state
                            if settings.STATUS_LED_ENABLED and not settings.STATUS_LED_ALWAYS_ON:
                                GPIO.output(settings.STATUS_LED_PIN, 0) 
                    else:
                        _spos = self._state
                        _xpos = 41 - int(Idle.fontsmall.getsize(_spos)[0]/2)

                        draw.text((_xpos, 51), _spos, font=Idle.fontsmall, fill="white") #other than play
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
            _spos = "%2.2d/%2.2d" % (int(self._song), int(self._playlistlength))
            _xpos = 85 - int(Idle.fontsmall.getsize(_spos)[0]/2)
            draw.text((_xpos, 51 ),_spos , font=Idle.fontsmall, fill="white")

            #shutdowntimer ? aktiv dann Zeit anzeigen
            if settings.job_t >= 0:
                draw.text((108, 51 ), "%2.2d" % (int(settings.job_t)), font=Idle.fontsmall, fill="white")
            else:
                if settings.X728_ENABLED:
                    draw.text((110,52), self.battsymbol, font=Idle.faiconsbig, fill="white")


            if (self.battcapacity >= 0 and self.battcapacity <= 20):
                draw.text((15,10), "Batterie laden!", font=Idle.font, fill="white")
                draw.text((50,30), "%d%%" % (self.battcapacity), font=Idle.font, fill="white")

                return

            if ((self._state == "stop") or (settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5) or (self.battcapacity <= settings.X728_BATT_LOW)):
                if (self.battcapacity >= 0):
                    draw.text((20,10), "Batterie: %d%%" % (self.battcapacity), font=Idle.font, fill="white")

                if settings.job_i >= 0 or settings.job_t >= 0:
                    if settings.job_i >= settings.job_t:
                        aus = settings.job_i
                    else:
                        aus = settings.job_t

                    draw.text((20,30), "AUS in " +  str(aus) + "min", font=Idle.font, fill="white")
                else:
                    draw.text((1,30), "%s" % (now.strftime("%a, %d.%m.%y %H:%M")), font=Idle.font, fill="white")

                return


            draw.text((1, 5), self._playingalbum, font=Idle.font, fill="white")
            draw.text((1, 19), self._playingname, font=Idle.font, fill="white")
            draw.text((1, 32), self._playingtitle, font=Idle.font, fill="white")


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

        while self.loop.is_running() and self.windowmanager.windows["idle"] == self.windowmanager.activewindow:
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


            if title != oldtitle:
                if oldtitle != "":
                    if (datetime.datetime.now() - settings.lastinput).total_seconds() >= settings.DARK_TIMEOUT:
                        settings.lastinput = datetime.datetime.now() - datetime.timedelta(seconds=settings.CONTRAST_TIMEOUT)
                titlex = 0
                oldtitle = title
            else:
                if Idle.font.getsize(title[titlex:])[0] > 127:
                    titlex += 1


            self._playingtitle = title[titlex:]

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
                    album = "Livestream"
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


            self._playingfile = playing['file'] if ("file" in playing) else ""
            self._volume = status['volume'] if ("volume" in status) else -1
            self._elapsed = status['elapsed'] if ("elapsed" in status) else -1
            self._time = status['time'] if ("time" in status) else -1
            self._playlistlength = status['playlistlength'] if ("playlistlength" in status) else -1
            self._song = str(int(status['song']) + 1) if ("song" in status) else -1
            self._duration = status['duration'] if ("duration" in status) else -1
            self._state = status['state'] if ("state" in status) else "unknown"

            await asyncio.sleep(self.windowmanager.looptime)

    def push_callback(self,lp=False):
        if lp:
            self.windowmanager.set_window("shutdownmenu")
        else:
            self.windowmanager.set_window("playbackmenu")


    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                self.busysymbol = settings.SYMBOL_VOL_UP
                playout.pc_volup()
            elif key == 'down' or key == '8':
                self.busysymbol = settings.SYMBOL_VOL_DN

                playout.pc_voldown()
            elif key == 'left' or key =='4':
                self.busysymbol = settings.SYMBOL_PREV

                if self._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,-1))
                else:
                    playout.pc_prev()
            elif key == 'right' or key == '6':
                self.busysymbol = settings.SYMBOL_NEXT
                if self._playingalbum == "Livestream":
                    cfolder = fn.get_folder_of_livestream(self._playingfile)
                    playout.pc_playfolder (fn.get_folder(cfolder,1))
                else:
                    playout.pc_next()
            elif key == 'A':
                settings.audio_basepath = settings.AUDIO_BASEPATH_MUSIC
                settings.currentfolder = settings.AUDIO_BASEPATH_MUSIC
                self.windowmanager.set_window("foldermenu")
            elif key == 'B':
                settings.audio_basepath = settings.AUDIO_BASEPATH_HOERBUCH
                settings.currentfolder = settings.AUDIO_BASEPATH_HOERBUCH
                self.windowmanager.set_window("foldermenu")
            elif key == 'C':
                settings.audio_basepath = settings.AUDIO_BASEPATH_RADIO
                settings.currentfolder = settings.AUDIO_BASEPATH_RADIO
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
                    what = settings.FILE_LAST_HOERSPIELE
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
