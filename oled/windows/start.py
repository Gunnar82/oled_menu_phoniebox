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
        self.conrasthandle = False
        self.check_bt = 0

        self.init_finished = False
        self.handle_key_back = False
        self.startup = time.monotonic()
        self.change_type_info()

        self.symbolentrylinewidth,self.symbolentrylineheight = self.faiconsbig.getsize(self.icon)


    def activate(self):

        logger.debug("activate: startet")
        self.clear_window()
        self.bluetooth.enable_dev_local()
        self.loop.run_in_executor(None,self.exec_init)


    def exec_init(self):
        try:
            logger.debug("exec_init: startet")
            self.appendsymbol(self.icon)
            self.appendcomment("Wird gestartet...")
            oled_version = get_oledversion()
            logger.info(f"exec_init: oled_version: {oled_version}")
            self.appendcomment(f"Version: {oled_version}")

            if (cfirewall.AUTO_ENABLED):
                logger.info("auto_enable firewall EIN")
                self.appendcomment("Aktiviere Firewall...")
                enable_firewall()
            else:
                logger.info("auto_enable firewall False")
                self.appendcomment("Übespringe Firewall...")

            if (cbluetooth.BLUETOOTH_AUTOCONNECT):
                logger.info("bluetooth autoconnect")
                self.appendcomment("Verbinde Bluetooth...")
                self.appendcomment(f"Suche Gerät: {self.bluetooth.selected_bt_name}")

                self.bluetooth.enable_dev_bt()
            else:
                logger.info("bluetooth autoconnect AUS")
                self.appendcomment("Überspringe Bluetooth...")

            if "x728" in settings.INPUTS:
                self.appendcomment(f"Batterie {settings.battcapacity}% geladen")

            while not  self.mopidyconnection.connected:
                self.appendcomment(f"modipy verbinden...")
                time.sleep(1)
            self.appendcomment(f"modipy verbunden.")



        except Exception as error:
            logger.error(f"exec_init: {error}")
            self.appendcomment(f"Fehler {error}")
        finally:

            self.appendcomment(f"Initialisierung beendet.")
            self.startup = time.monotonic()

            self.init_finished = True

    def render(self):
        self.set_last_position()
        super().render()

        if (time.monotonic() - self.startup) >= settings.START_TIMEOUT and self.init_finished:
            logger.debug("start: init")
            self.windowmanager.set_window("idle")



    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        pass
