""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import integrations.bluetooth
import integrations.functions as fn

from datetime import datetime

class Start(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=20)

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
                self.windowmanager.set_window("idle")
            draw.text((25, 3), text="Wird gestartet...", font=Start.font, fill="white")
            if settings.X728_ENABLED:
                symbol = settings.battsymbol

                draw.text((50, 20), text=symbol, font=Start.fontawesome, fill=fn.get_battload_color())
                draw.text((25, 50), text="%d%% geladen" % (settings.battcapacity), font=Start.font, fill=fn.get_battload_color())
            else:
                draw.text((50, 25), text="\uf251", font=Start.fontawesome, fill="white")


    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
