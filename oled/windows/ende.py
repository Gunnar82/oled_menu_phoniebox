""" Start screen """
from ui.mainwindow import MainWindow
from luma.core.render import canvas
from PIL import ImageFont

import asyncio
import time
import settings
import integrations.playout as playout
import config.symbols as symbols
import config.shutdown_reason as SR

from integrations.logging_config import *

logger = setup_logger(__name__)


import config.colors as colors

from datetime import datetime

class Ende(MainWindow):

    def __init__(self, windowmanager, loop,nowplaying):
        super().__init__(windowmanager, loop, nowplaying)
        self.loop = loop
#        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
        self.fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
        self.wait4track = -1
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
            self.power_timer = settings.job_t >= 0

            if not (self.power_timer):

                logger.debug(f"no powertimer")
                self.drawsymbol =  symbols.SYMBOL_BELL_WHITE

                self.drawline1 = settings.shutdown_reason
                self.drawline2 = "System wird:"
                if self.wait4track != -1: self.drawline3 = "Titelende: %d" % (self.wait4track)
                self.drawsymbol = symbols.SYMBOL_POWER
                self.mwidth,self.mheight = self.fontawesome.getsize(self.drawsymbol)

                while self.loop.is_running() and (settings.shutdown_reason == SR.SR4 or (self.nowplaying._state != "stop" and self.wait4track == -1)):
                    check = max(0, int(self.wait4track))
                    print (check)
                    if int(self.nowplaying._song) > check:
                        settings.shutdown_reason = SR.SR2
    
                    await asyncio.sleep(1)
                self.do_shutdown()
            else:
                while self.loop.is_running() and self.power_timer:
                    self.drawline1 = "Poweroff Timer aktiv!"
                    self.drawline2 = f"AUS in min {settings.job_t} min"
                    if "gpicase" in settings.INPUTS: self.drawline3 = "start > pause; X,Y > AUS"
                    elif "keypad4x4" in settings.INPUTS: self.drawline3 = "# > pause; A,B,C,D > AUS"
                    await asyncio.sleep(3)

        except Exception as error:
            loger.debug("timer:error")

    def activate(self):
        if not self.drawline1 == SR.SR4:
            self.loop.create_task(self.timer())


    def render(self):
        with canvas(self.device) as draw:
            super().render(draw)

            draw.text((1, settings.DISPLAY_HEIGHT - 3*settings.IDLE_LINE_HEIGHT ), self.drawline1 , font=self.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 4*settings.IDLE_LINE_HEIGHT ), self.drawline2, font=self.font, fill="white")
            draw.text((1, settings.DISPLAY_HEIGHT - 5*settings.IDLE_LINE_HEIGHT ), self.drawline3, font=self.font, fill="white")

            draw.text(((settings.DISPLAY_WIDTH - self.mwidth )/ 2, 20), self.drawsymbol, font=self.fontawesome, fill=colors.COLOR_RED)


    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        if key in ['start','#']:
            playout.pc_toggle()
        elif key in ['X','Y','A','B','C','D',]:
            playout.savepos_online(self.nowplaying)
            playout.savepos()
            #self.mopidyconnection.stop()
            logger.info("Stopping event loop")
            time.sleep(1)
            self.loop.stop()


    def deactivate(self):
        super().deactivate()
        self.power_timer = False


    def do_shutdown(self):
        playout.savepos_online(self.nowplaying)
        playout.savepos()
        logger.info("timer: Stopping event loop")
        time.sleep(2)
        self.loop.stop()
