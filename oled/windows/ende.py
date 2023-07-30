""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.bluetooth
from datetime import datetime

class Ende(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.timeout = False
        self.startup = datetime.now()

    def activate(self):
        self.busytext1 = "wird"
        self.busytext2 = settings.shutdown_reason
        self.busysymbol = "\uf011"
        self.renderbusy()

    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
