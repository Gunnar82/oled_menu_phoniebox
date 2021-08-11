""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.bluetooth
from datetime import datetime

class Start(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=35)

    def __init__(self, windowmanager, mopidyconnection):
        super().__init__(windowmanager)
        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.startup = datetime.now()
        self.conrasthandle = False

    def render(self):
        with canvas(self.device) as draw:
            if self.mopidyconnection.connected and ((datetime.now() - self.startup).total_seconds() >= settings.START_TIMEOUT):
                #print ("init")
                self.windowmanager.set_window("playlistmenu") #idle")
            draw.text((25, 3), text="Wird gestartet...", font=Start.font, fill="white")
            draw.text((50, 25), text="\uf251", font=Start.fontawesome, fill="white")

    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
