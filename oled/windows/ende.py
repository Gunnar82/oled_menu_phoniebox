""" Start screen """
from ui.mainwindow import MainWindow
from luma.core.render import canvas
from PIL import ImageFont

import asyncio
import time
import settings
import integrations.playout as playout

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
        self.timeout = False
        self.window_on_back = "none"
        self.handle_key_back = False
        self.power_timer = False
        self._rendertime = 1

        self.windowmanager = windowmanager
        self.timeout = False
        self.startup = datetime.now()

        self.drawsymbol = "\uf011"
        self.drawline1 = ""
        self.drawline2 = ""
        self.drawline3 = ""

    async def gpicase_timer(self):
        self.power_timer = settings.job_t >= 0

        if not self.power_timer:
            self.drawsymbol =  "\uf0a2"
            self.drawline1 = f"System wird {settings.shutdown_reason}"
            self.drawsymbol = "\uf011"
            self.mwidth,self.mheight = self.fontawesome.getsize(self.drawsymbol)

            await asyncio.sleep(1)

            if self.nowplaying.input_is_online:
                playout.savepos_online(self.nowplaying)
            playout.savepos()
            logger.info("Stopping event loop")
            await assyncio.sleep(1)
            self.loop.stop()

        else:

            while self.loop.is_running() and self.power_timer:
                self.drawline1 = "GPI Case Timer aktiv!"
                self.drawline2 = f"AUS in min {settings.job_t} min"
                self.drawline3 = "start > pause; X,Y > AUS"
                await asyncio.sleep(3)

    def activate(self):
        super().activate()
        self.loop.create_task(self.gpicase_timer())


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
        if key == 'start':
            playout.pc_toggle()
        elif key in ['X','Y']:
            if self.nowplaying.input_is_online:
                playout.savepos_online(self.nowplaying)
            playout.savepos()
            #self.mopidyconnection.stop()
            logger.info("Stopping event loop")
            playout.pc_shutdown()
            time.sleep(1)
            self.loop.stop()


    def deactivate(self):
        super().deactivate()
        self.power_timer = False

