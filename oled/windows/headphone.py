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

    def __init__(self, windowmanager,loop,usersettings,bluetooth,title):
        super().__init__(windowmanager,loop,usersettings,title)
        self.bluetooth = bluetooth
        self.descr.append(["Lautsprecher",symbols.SYMBOL_SPEAKER])
        self.descr.append(["",symbols.SYMBOL_HEADPHONE])

        self.descr.append(["Gerät suchen","\uf01e"])


    def set_current_bt_name(self):
        self.descr[2][0]="BT: %s" %(self.bluetooth.selected_bt_name)


    def deactivate(self):
        logger.debug ("ende")
        #self.bluetooth.start_bluetoothctl()

    def activate (self):
        try:
            self.descr = self.descr[:1]
            self.descr.append(["Gerät suchen","\uf01e"])
            self.descr.append(["Lautsprecher",symbols.SYMBOL_SPEAKER])
            for mac, devname in self.usersettings.get_bluetooth_devices():
                self.descr.append([devname,symbols.SYMBOL_HEADPHONE,mac])
        except Exception as error:
            logger.debug (error)

    #def push_callback(self,lp=False):
    def push_handler(self):
        print (self.counter)

        self.set_window_busy()
        self.append_busytext()


        if self.counter == 1:
            self.append_busytext("Trenne Bluetooth - falls verbunden")
            self.bluetooth.disconnect_all_connected_devices()

            self.windowmanager.set_window("bluetoothmenu")

        elif self.counter == 2:
            self.append_busytext("Aktiviere lokale Ausgabe")
            self.append_busytext("Deaktiviere Bluetoothausgabe")

            self.bluetooth.enable_dev_local()

            self.append_busytext("Abgeschlosssen.")

        elif self.counter > 2:
            dev_name = self.descr[self.counter][0]
            dev_mac = self.descr[self.counter][2]

            self.append_busytext("Verbinde Gerät:")
            self.append_busytext (dev_name)
    
            self.bluetooth.disconnect_all_connected_devices()
            if not self.bluetooth.connect_default_bt_device(dev_mac):
                self.append_busyerror ("Keine Verbindung:")
            else:
                self.append_busytext("Deaktiviere lokale Ausgabe")
                self.append_busytext("Aktiviere Bluetoothausgabe")


        self.append_busytext("Beendet.")
        self.set_window_busy(False)



