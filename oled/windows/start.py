""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas

from datetime import datetime

import settings
import logging
import config.loglevel
logger = logging.getLogger("oled.start")
logger.setLevel(config.loglevel.LOGLEVEL)

import config.colors as colors
import config.symbols as symbols
import config.bluetooth as cbluetooth

from integrations.functions import get_oledversion, get_battload_color



class Start(WindowBase):

    def __init__(self, windowmanager,loop, mopidyconnection,bluetooth):
        super().__init__(windowmanager, loop)
        self.bluetooth = bluetooth
        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.startup = datetime.now()
        self.conrasthandle = False
        self.check_bt = 0


    def activate(self):
        self.bluetooth.enable_dev_local()

        if (cbluetooth.BLUETOOTH_AUTOCONNECT):
            self.set_busy("Verbinde...",symbols.SYMBOL_BLUETOOTH_OFF,self.bluetooth.selected_bt_name, busyrendertime = 5)
            self.busy = True
            self.renderbusy()

            self.bluetooth.enable_dev_bt()

    def render(self):
        self.set_busy("Wird gestartet...",busytext2=get_oledversion())

        if "x728" in settings.INPUTS:
            color = get_battload_color()
            self.busysymbol = symbols.SYMBOL_BATTERY
            self.busytext2 = "%d%% geladen" % (settings.battcapacity)
        else:
            color = colors.COLOR_WHITE

        self.renderbusy(symbolcolor=color, textcolor2=color)


        if self.mopidyconnection.connected and ((datetime.now() - self.startup).total_seconds() >= settings.START_TIMEOUT):
            logger.debug("start: init")
            self.windowmanager.set_window("idle")




    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        pass
