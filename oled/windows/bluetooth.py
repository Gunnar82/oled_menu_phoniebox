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
        self.descr.append(["aktualisieren","\uf01e"])
        self.descr.append(["",""])
        self.descr.append(["",""])

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
                print ("running loop bt")
                while len(self.descr) > 4:
                    print (self.descr)
                    self.descr.pop()

                for device in self.bluetooth.get_paired_devices():
                    print ("paired devices: %s" %(device))
                    self.descr.append([device['name'],symbols.SYMBOL_BLUETOOTH_OFF,device['mac_address']])

                for device in self.bluetooth.get_discoverable_devices():
                    print ("availabe devices: %s" %(device))

                    self.descr.append([device['name'],symbols.SYMBOL_BLUETOOTH_ON,device['mac_address']])

                self.generate = False

            await asyncio.sleep(1)

    #def push_callback(self,lp=False):
    async def push_handler(self):
        await asyncio.sleep(1)
        if (self.counter == 1):
            self.bluetooth.start_scan()

            self.generate = True
        else:
            if self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_OFF:
                self.bluetooth.set_alsa_bluetooth_mac(self.descr[self.counter][2],self.descr[self.counter][0])

            elif self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_ON:
                self.bluetooth.pair(self.descr[self.counter][2])
                self.bluetooth.trust(self.descr[self.counter][2])
                self.generate = True

        await asyncio.sleep(1)


    def turn_callback(self, direction, key=None):
        super().turn_callback(direction,key)

        if direction > 0 and self.counter == 2:
            self.counter = 5
        elif direction < 0 and self.counter == 5:
            self.counter == 2

        if key == 'X' or key == '5':
            if self.counter > 1 and self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_OFF:
                self.set_busy("Gerät gelöscht: %s!" % (self.descr[self.counter][0]))
                self.bluetooth.remove(self.descr[self.counter][2])
                self.generate = True
