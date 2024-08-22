""" Shutdown menu """
from ui.listbase import ListBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.symbols as symbols

import os
from integrations.logging import *
import time
import asyncio

 
class Bluetoothmenu(ListBase):

    def __init__(self, windowmanager,loop,bluetooth,title):
        super().__init__(windowmanager,loop,title)
        self.bluetooth = bluetooth
        self.window_on_back = "headphonemenu"
        self.menu.append(["aktualisieren...","c"])
        self.menu.append(["","h"])
        self.handle_left_key = False


        self.generate = False
        self.timeout = False

    def deactivate(self):
        self.active = False
        self.bluetooth.stop_scan()

        self.bluetooth.stop_bluetoothctl()


    def activate (self):
        self.active = True
        self.bluetooth.start_bluetoothctl()
        self.bluetooth.start_scan()
        self.generate = True
        self.loop.create_task(self.gen_menu())

    async def gen_menu(self):
        while self.loop.is_running() and self.active:
            if self.generate:

                while len(self.menu) > 2:
                    self.menu.pop()

                self.menu.append(["> gekoppelte Geräte:","c"])

                for device in self.bluetooth.get_paired_devices():
                    self.menu.append([device['name'],symbols.SYMBOL_BLUETOOTH_OFF,device['mac_address']])

                self.menu.append(["","h"])
                self.menu.append(["> neue Geräte:","c"])

                for device in self.bluetooth.get_discoverable_devices():

                    self.menu.append([device['name'],symbols.SYMBOL_BLUETOOTH_ON,device['mac_address']])

                self.generate = False

            await asyncio.sleep(1)

    #def push_callback(self,lp=False):
    async def push_handler(self):
        await asyncio.sleep(1)
        if (self.position == 1):
            self.bluetooth.start_scan()

            self.generate = True
        else:
            if self.menu[self.position][1] == symbols.SYMBOL_BLUETOOTH_OFF:
                self.bluetooth.set_alsa_bluetooth_mac(self.menu[self.position][2],self.menu[self.position][0])

            elif self.menu[self.position][1] == symbols.SYMBOL_BLUETOOTH_ON:
                self.bluetooth.pair(self.menu[self.position][2])
                self.bluetooth.trust(self.menu[self.position][2])
                self.generate = True

        await asyncio.sleep(1)


    def turn_callback(self, direction, key=None):
        super().turn_callback(direction,key)

