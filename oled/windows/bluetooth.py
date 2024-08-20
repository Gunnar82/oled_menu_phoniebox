""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.symbols as symbols

import os
from integrations.logging import *
import time
import asyncio

 
class Bluetoothmenu(MenuBase):


    def __init__(self, windowmanager,loop,bluetooth,title):
        super().__init__(windowmanager,loop,title)
        self.bluetooth = bluetooth
        self.window_on_back = "headphonemenu"
        self.descr.append(["Refresh","\uf01e"])

    def deactivate(self):
        print ("ende")
        self.bluetooth.stop_bluetoothctl()

        self.bluetooth.stop_scan()
        #self.bluetooth.start_bluetoothctl()

    def activate (self):
        self.bluetooth.start_bluetoothctl()
        #self.bluetooth.disconnect()
        self.bluetooth.start_scan()

        self.gen_menu()

    def gen_menu(self):
        while len(self.descr) > 2:
            self.descr.pop()

        for devices in self.bluetooth.get_paired_devices():
            self.descr.append([devices['name'],symbols.SYMBOL_BLUETOOTH_OFF,devices['mac_address']])

        for devices in self.bluetooth.get_discoverable_devices():
            self.descr.append([devices['name'],symbols.SYMBOL_BLUETOOTH_ON,devices['mac_address']])

    #def push_callback(self,lp=False):
    async def push_handler(self):
        await asyncio.sleep(1)
        if (self.counter == 1):
            self.gen_menu()
        else:
            if self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_OFF:
                self.bluetooth.set_alsa_bluetooth_mac(self.descr[self.counter][2],self.descr[self.counter][0])

            elif self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_ON:
                self.bluetooth.pair(self.descr[self.counter][2])
                self.bluetooth.trust(self.descr[self.counter][2])
                self.gen_menu()
        await asyncio.sleep(1)


