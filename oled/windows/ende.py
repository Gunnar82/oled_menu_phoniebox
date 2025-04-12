""" Start screen """
from ui.mainwindow import MainWindow
from luma.core.render import canvas
from PIL import ImageFont

import asyncio
import time
import settings
import config.symbols as symbols
import config.shutdown_reason as SR
import integrations.playout as playout


from integrations.logging_config import *

logger = setup_logger(__name__)


import config.colors as colors

from datetime import datetime

class Ende(MainWindow):

    def __init__(self, windowmanager, loop,usersettings, nowplaying,musicmanager):
        super().__init__(windowmanager, loop, usersettings, nowplaying)
        self.loop = loop
        self.musicmanager = musicmanager
#        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
        self.fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
        self.wait4track = -1
        self.wait4end = False
        self.timeout = False
        self.window_on_back = "none"
        self.handle_key_back = False
        self.power_timer = False
        self._rendertime = 1

        self.windowmanager = windowmanager
        self.timeout = False
        self.startup = datetime.now()

        self.drawsymbol = symbols.SYMBOL_POWER
        self.drawline1 = ""
        self.drawline2 = ""
        self.drawline3 = ""
        self.mwidth,self.mheight = self.fontawesome.getsize(self.drawsymbol)


    async def timer(self):
        try:
            self.power_timer = settings.job_t >= 0 and not settings.shutdown_reason == SR.SR6

            if settings.shutdown_reason == SR.SR6:
                settings.shutdown_reason == SR.SR5
                self.windowmanager.clear_window()
                self.musicmanager.stop()
                await asyncio.sleep(60)


            if not (self.power_timer):
                # keine Poweroff-Timer
                logger.debug(f"no powertimer")
                self.drawsymbol =  symbols.SYMBOL_BELL_WHITE

                self.drawline1 = "Systemstatus:"
                self.drawline2 = settings.shutdown_reason

                wait4track = False

                if self.wait4track != -1:
                    #wait4 track ist aktiviert
                    wait4track = True
                    self.drawline3 = "Titelende: %d" % (self.wait4track)


                if self.wait4end:
                    #wait4end ist aktiviert
                    self.drawline3 = "STOP"

                self.drawsymbol = symbols.SYMBOL_POWER
                self.mwidth,self.mheight = self.fontawesome.getsize(self.drawsymbol)

                while self.loop.is_running() and (settings.shutdown_reason == SR.SR4):
                    check = int(self.wait4track)
                    wait4end = self.wait4end and self.nowplaying._state == "stop"

                    if self.wait4track >= 0 and int(self.nowplaying._song) > check and self.nowplaying._state != "stop":
                        #track wurde erreicht
                        break

                    if wait4end:
                        break

                    await asyncio.sleep(1)

                settings.shutdown_reason = SR.SR5
                self.do_shutdown()
            else:
                while self.loop.is_running() and self.power_timer:
                    self.drawline1 = "Poweroff Timer aktiv!"
                    self.drawline2 = f"AUS in min {settings.job_t} min"
                    if "gpicase" in settings.INPUTS: self.drawline3 = "start > pause; X,Y > AUS"
                    elif "keypad4x4" in settings.INPUTS: self.drawline3 = "# > pause; A,B,C,D > AUS"
                    await asyncio.sleep(3)

        except Exception as error:
            logger.debug(f"timer:{error}")

    def activate(self):
        print (settings.shutdown_reason)
        if not self.drawline2 == SR.SR4:
            self.loop.create_task(self.timer())


    def render(self):
        with canvas(self.device) as draw:
            super().render(draw)

            draw.text((1, settings.DISPLAY_HEIGHT - 3*settings.IDLE_LINE_HEIGHT ), self.drawline3 , font=self.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 4*settings.IDLE_LINE_HEIGHT ), self.drawline2, font=self.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 5*settings.IDLE_LINE_HEIGHT ), self.drawline1, font=self.font, fill="white")

            draw.text(((settings.DISPLAY_WIDTH - self.mwidth )/ 2, 20), self.drawsymbol, font=self.fontawesome, fill=colors.COLOR_RED)


    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        if key.lower() in ['start','#','key_pause']:
            self.musicmanager.playpause()
        elif key in ['X','Y','A','B','C','D',]:
            playout.savepos_online(self.nowplaying)
            self.musicmanager.stop()
            logger.info("Stopping event loop")
            time.sleep(1)
            self.loop.stop()


    def deactivate(self):
        super().deactivate()
        self.power_timer = False


    def do_shutdown(self):
        playout.savepos_online(self.nowplaying)
        self.musicmanager.stop()
        logger.info("timer: Stopping event loop")
        time.sleep(2)
        self.loop.stop()

