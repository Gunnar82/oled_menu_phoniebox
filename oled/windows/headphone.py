""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.symbols as symbols


import os

import time
import asyncio

from integrations.logging_config import setup_logger

logger = setup_logger(__name__)

 
class Headphonemenu(MenuBase):


    def __init__(self, windowmanager,loop,bluetooth,title):
        super().__init__(windowmanager,loop,title)
        self.bluetooth = bluetooth
        self.descr.append([settings.ALSA_DEV_LOCAL,symbols.SYMBOL_SPEAKER])
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
    async def push_handler(self):
        await asyncio.sleep(1)
        if self.counter == 1:
            self.bluetooth.enable_dev_local()

        elif self.counter == 2:
            if not self.bluetooth.enable_dev_bt():
                self.set_busy ("Keine Verbindung!",symbols.SYMBOL_ERROR,self.bluetooth.selected_bt_name)
                await asyncio.sleep(1)

        elif self.counter == 3:
            self.bluetooth.cmd_disconnect()
            time.sleep(2)
            self.windowmanager.set_window("bluetoothmenu")

        await asyncio.sleep(1)


