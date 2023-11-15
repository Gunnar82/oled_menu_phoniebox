""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings, colors

from datetime import datetime

class Ende(WindowBase):

    def __init__(self, windowmanager, loop):
        super().__init__(windowmanager, loop)
        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
        self.fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
        self.timeout = False
        self.window_on_back = "none"
        self.power_timer = False
        self._rendertime = 5

        self.windowmanager = windowmanager
        self.timeout = False
        self.startup = datetime.now()

    def activate(self):
        self.power_timer = settings.job_t >= 0
        
        self.set_busy("System wird","\uf011",settings.shutdown_reason)
        self.renderbusy()


    def render(self):
        if self.power_timer:
            self.set_busy("GPI Case Timer aktiv!","\uf0a2", "AUS in %2.2d min " % settings.job_t)

    def push_callback(self,lp=False):
        pass

    def deactivate(self):
            self.power_timer = False

