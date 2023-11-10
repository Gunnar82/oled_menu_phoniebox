""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas

from datetime import datetime

import settings, colors, symbols

import integrations.bluetooth as bluetooth
from integrations.functions import get_battload_color
from integrations.logging import *


class Start(WindowBase):

    def __init__(self, windowmanager,loop, mopidyconnection):
        super().__init__(windowmanager, loop)
        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.startup = datetime.now()
        self.conrasthandle = False
        self.check_bt = 0


    def activate(self):

        if (settings.AUTOCONNECT_DEV_BT_1 and settings.ENABLED_DEV_BT_1):
            self.set_busy("Verbinde...",symbols.SYMBOL_BLUETOOTH_OFF,settings.NAME_DEV_BT_1, busyrendertime = 5)
            self.busy = True
            self.renderbusy()

            bluetooth.enable_dev_bt_1()


        if (settings.AUTOCONNECT_DEV_BT_2 and settings.ENABLED_DEV_BT_2):
            self.set_busy("Verbinde...",symbols.SYMBOL_BLUETOOTH_OFF,settings.NAME_DEV_BT_2, busyrendertime = 5)
            self.busy = True
            self.renderbusy()

            bluetooth.enable_dev_bt_2() 


    def render(self):
        self.set_busy("Wird gestartet...")

        if "x728" in settings.INPUTS:
            color = get_battload_color()
            self.busysymbol = symbols.SYMBOL_BATTERY
            self.busytext2 = "%d%% geladen" % (settings.battcapacity)
        else:
            color = colors.COLOR_WHITE

        self.renderbusy(symbolcolor=color, textcolor2=color)


        if self.mopidyconnection.connected and ((datetime.now() - self.startup).total_seconds() >= settings.START_TIMEOUT):
            log (lDEBUG,"start: init")
            self.windowmanager.set_window("idle")




    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, ud=False):
        pass
