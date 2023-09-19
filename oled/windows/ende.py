""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.bluetooth
from datetime import datetime

class Ende(WindowBase):

    def __init__(self, windowmanager):
        super().__init__(windowmanager)
        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
        self.fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
        self.timeout = False
        self.window_on_back = "none"

        self.windowmanager = windowmanager
        self.timeout = False
        self.startup = datetime.now()

    def activate(self):
        self.busytext1 = "wird"
        self.busytext2 = settings.shutdown_reason
        self.busysymbol = "\uf011"
        self.renderbusy()


    def render(self):
        with canvas(self.device) as draw:
            mwidth,mheight = self.font.getsize(self.busytext1)
            draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, 2), text=self.busytext1, font=self.font, fill='white')

            mwidth,mheight = self.fontawesome.getsize(self.busysymbol)
            draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, (settings.DISPLAY_HEIGHT - mheight) / 2), text=self.busysymbol, font=self.fontawesome, fill='red') #sanduhr

            if (self.busytext2 != ""):
                mwidth,mheight = self.font.getsize(self.busytext2)
                draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, settings.DISPLAY_HEIGHT - mheight - 2), text=self.busytext2, font=self.font, fill='white') #    sanduhr


    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        if key =='GPI_PWR_OFF':
            self.busysymbol = "\uf0a2"
            self.busytext1 = 'GPI Case Timer aktiv!'
            self.busytext2 = 'AUS in %2.2d min ' % settings.job_t
        elif key =='GPI_PWR_ON':
            self.windowmanager.set_window("idle")

