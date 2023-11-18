""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import asyncio

import settings

import config.colors as colors

from datetime import datetime

class Ende(WindowBase):

    def __init__(self, windowmanager, loop):
        super().__init__(windowmanager, loop)
        self.loop = loop
        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
        self.fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
        self.timeout = False
        self.window_on_back = "none"
        self.power_timer = False
        self._rendertime = 5

        self.windowmanager = windowmanager
        self.timeout = False
        self.startup = datetime.now()

    async def gpicase_timer(self):
        while self.loop.is_running() and self.power_timer:
            self.set_busy("GPI Case Timer aktiv!","\uf0a2", "AUS in %2.2d min " % settings.job_t,busyrendertime=0.5)
            await asyncio.sleep(3)

    def activate(self):
        self.power_timer = settings.job_t >= 0

        if self.power_timer:
            self.loop.create_task(self.gpicase_timer())
        else:
            self.set_busy("System wird","\uf011",settings.shutdown_reason,busyrendertime=1)
        self.renderbusy()

    def render(self):
        self.renderbusy()

    def push_callback(self,lp=False):
        pass

    def deactivate(self):
            self.power_timer = False

