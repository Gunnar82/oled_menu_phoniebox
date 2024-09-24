""" Start screen """
from ui.listbase import ListBase
from luma.core.render import canvas

from datetime import datetime

import settings
import time

from integrations.logging_config import *

logger = setup_logger(__name__)


import config.colors as colors
import config.symbols as symbols
import config.bluetooth as cbluetooth
import config.firewall as cfirewall

from integrations.functions import get_oledversion, get_battload_color, enable_firewall



class Start(ListBase):
    icon = "\uf001 \uf02d \uf02c"
    def __init__(self, windowmanager,loop, mopidyconnection,bluetooth):
        super().__init__(windowmanager, loop, "Programmstart")
        self.bluetooth = bluetooth
        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.startup = time.monotonic()
        self.conrasthandle = False
        self.check_bt = 0
        self.hide_buttons = True
        self.init_finished = False
        self.symbolentrylinewidth,self.symbolentrylineheight = self.faiconsbig.getsize(self.icon)


    def activate(self):

        logger.debug("activate: startet")
        self.clear_window()
        self.bluetooth.enable_dev_local()
        self.loop.run_in_executor(None,self.exec_init)


    def exec_init(self):
        try:
            logger.debug("exec_init: startet")
            self.menu.append([self.icon,self.symbol])
            self.menu.append("Wird gestartet...")
            oled_version = get_oledversion()
            logger.info(f"exec_init: oled_version: {oled_version}")
            self.menu.append(f"Version: {oled_version}")

            if (cfirewall.AUTO_ENABLED):
                logger.info("auto_enable firewall EIN")
                self.menu.append("Aktiviere Firewall...")
                enable_firewall()
            else:
                logger.info("auto_enable firewall False")
                self.menu.append("Übespringe Firewall...")

            if (cbluetooth.BLUETOOTH_AUTOCONNECT):
                logger.info("bluetooth autoconnect")
                self.menu.append("Verbinde Bluetooth...")
                self.menu.append(f"Suche Gerät: {self.bluetooth.selected_bt_name}")

                self.bluetooth.enable_dev_bt()
            else:
                logger.info("bluetooth autoconnect AUS")
                self.menu.append("Überspringe Bluetooth...")

        except Exception as error:
            logger.error(f"exec_init: {error}")
            self.menu.append(f"Fehler {error}")
        finally:
            time.sleep(5)
            self.init_finished = True

    def render(self):
        self.position = len(self.menu) - 1
        super().render()
        if "x728" in settings.INPUTS:
            color = get_battload_color()
            self.busysymbol = symbols.SYMBOL_BATTERY
            self.busytext2 = "%d%% geladen" % (settings.battcapacity)
        else:
            color = colors.COLOR_WHITE

        if self.mopidyconnection.connected and ((time.monotonic() - self.startup) >= settings.START_TIMEOUT) and self.init_finished:
            logger.debug("start: init")
            self.windowmanager.set_window("idle")



    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        pass
