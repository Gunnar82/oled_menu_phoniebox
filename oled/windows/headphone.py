""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.symbols as symbols


import os

import time

from integrations.logging_config import *

logger = setup_logger(__name__)

 
class Headphonemenu(MenuBase):

    def __init__(self, windowmanager,loop,bluetooth,title):
        super().__init__(windowmanager,loop,title)
        self.bluetooth = bluetooth
        self.descr.append(["Lautsprecher",symbols.SYMBOL_SPEAKER])
        self.descr.append(["",symbols.SYMBOL_HEADPHONE])

        self.descr.append(["Gerät suchen","\uf01e"])


    def set_current_bt_name(self):
        self.descr[2][0]="BT: %s" %(self.bluetooth.selected_bt_name)


    def deactivate(self):
        print ("ende")
        #self.bluetooth.start_bluetoothctl()

    def activate (self):
        self.set_current_bt_name()

    #def push_callback(self,lp=False):
    def push_handler(self):

        self.set_window_busy()
        self.append_busytext()


        if self.counter == 1:
            self.append_busytext("Aktiviere lokale Ausgabe")
            self.append_busytext("Deaktiviere Bluetoothausgabe")

            self.bluetooth.enable_dev_local()

            self.append_busytext("Abgeschlosssen.")

        elif self.counter == 2:
            self.append_busytext("Verbinde Gerät:")
            self.append_busytext (self.bluetooth.selected_bt_name)

            if not self.bluetooth.enable_bluez():
                self.append_busyerror ("Keine Verbindung:")
            else:
                self.append_busytext("Deaktiviere lokale Ausgabe")
                self.append_busytext("Aktiviere Bluetoothausgabe")


        elif self.counter == 3:
            self.append_busytext("Trenne Bluetooth - falls verbunden")
            #for i in range(0, 4):
            #    self.bluetooth.cmd_disconnect()
            self.windowmanager.set_window("bluetoothmenu")

        self.append_busytext("Beendet.")
        self.set_window_busy(False)



