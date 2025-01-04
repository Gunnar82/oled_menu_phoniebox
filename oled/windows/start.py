""" Start screen """
from ui.listbase import WindowBase
from luma.core.render import canvas

from datetime import datetime

import settings
import time

from integrations.logging_config import *

logger = setup_logger(__name__)


import config.colors as colors
import config.symbols as symbols

import config.user_settings as csettings

from integrations.functions import get_oledversion, get_battload_color, enable_firewall, run_as_service



class Start(WindowBase):
    contrasthandle = False

    def __init__(self, windowmanager,loop, mopidyconnection,bluetooth):
        super().__init__(windowmanager, loop)
        self.busysymbol = symbols.SYMBOL_PROGRAMM

        self.bluetooth = bluetooth

        self.mopidyconnection = mopidyconnection
        self.timeout = False
        self.conrasthandle = False
        self.check_bt = 0
        self.handle_key_back = False
        self.startup = time.monotonic()


    def activate(self):
        logger.debug("activate: startet")
        self.set_window_busy()

        self.loop.run_in_executor(None,self.exec_init)

    def exec_init(self):
        try:
            logger.debug("exec_init: startet")

            self.append_busytext("Wird gestartet...")
            oled_version = get_oledversion()
            logger.info(f"exec_init: oled_version: {oled_version}")
            self.append_busytext(f"Version: {oled_version}")

            if (run_as_service()):
                self.append_busytext("Als Dienst - minimales Logging...")
            else:
                self.append_busytext("Kommandozeile - normales Logging...")

            if (csettings.AUTO_ENABLED):
                logger.info("auto_enable firewall EIN")
                self.append_busytext("Aktiviere Firewall...")
                enable_firewall()
            else:
                logger.info("auto_enable firewall False")
                self.append_busytext("Übespringe Firewall...")


            if csettings.BLUETOOTH_ENABLED: self.bluetooth.enable_dev_local()

            if (csettings.BLUETOOTH_AUTOCONNECT and csettings.BLUETOOTH_ENABLED):
                logger.info("bluetooth autoconnect")
                self.append_busytext("Verbinde Bluetooth...")
                self.append_busytext(f"Suche Gerät: {self.bluetooth.selected_bt_name}")

                self.bluetooth.enable_dev_bt()
            else:
                logger.info("bluetooth autoconnect AUS")
                self.append_busytext("Überspringe Bluetooth...")

            if "x728" in settings.INPUTS:
                self.append_busytext(f"Batterie {settings.battcapacity}% geladen")

            while not  self.mopidyconnection.connected:
                self.append_busytext(f"mopidy verbinden...")
                time.sleep(1)
            self.append_busytext(f"mopidy verbunden.")

        except Exception as error:
            logger.error(f"exec_init: {error}")
            self.append_busyerror(f"Fehler {error}")
        finally:

            self.append_busytext(f"Initialisierung beendet.")
            self.startup = time.monotonic()


            while (time.monotonic() - self.startup) < csettings.START_TIMEOUT:
                logger.debug("start: wait")
                time.sleep (1)
            self.windowmanager.set_window("idle")


    def push_callback(self,lp=False):
        pass

    def turn_callback(self, direction, key=None):
        pass
