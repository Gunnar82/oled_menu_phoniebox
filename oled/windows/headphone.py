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

 
class Headphonemenu(MenuBase):


    def __init__(self, windowmanager,loop,bluetooth,title):
        super().__init__(windowmanager,loop,title)
        self.bluetooth = bluetooth



    def set_current_bt_name(self):
        self.descr[2][0]="BT: %s" %(self.bluetooth.selected_bt_name)


    def deactivate(self):
        print ("ende")
        self.bluetooth.stop_scan()
        #self.bluetooth.start_bluetoothctl()

    def activate (self):
        self.bluetooth.start_bluetoothctl()
        self.bluetooth.start_scan()
        self.gen_menu()

    def gen_menu(self):
        print (len(self.descr))
        while len(self.descr) > 1:
            self.descr.pop()

        self.descr.append([settings.ALSA_DEV_LOCAL,symbols.SYMBOL_SPEAKER])
        self.descr.append(["",symbols.SYMBOL_HEADPHONE])
        self.set_current_bt_name()


        self.descr.append(["Gerät suchen","\uf01e"])

        for devices in self.bluetooth.get_paired_devices():
            self.descr.append([devices['name'],symbols.SYMBOL_BLUETOOTH_OFF,devices['mac_address']])

        for devices in self.bluetooth.get_discoverable_devices():
            self.descr.append([devices['name'],symbols.SYMBOL_BLUETOOTH_ON,devices['mac_address']])

    def turn_callback(self,direction, key = None):
        super().turn_callback(direction,key)
#        if self.counter == 3:
#            if direction > 0 or key in ['right','up','2', '4'] :
#                self.counter = 4
#            elif  direction < 0 or key in ['left','down','6','8']:
#                self.counter = 2

    #def push_callback(self,lp=False):
    async def push_handler(self):
        await asyncio.sleep(1)
        if self.counter == 1:
            self.bluetooth.enable_dev_local()

        elif self.counter == 2:
            if self.bluetooth.enable_dev_bt() != 0:
                self.set_busy ("Keine Verbindung!",symbols.SYMBOL_ERROR,self.bluetooth.selected_bt_name)
                await asyncio.sleep(1)

        elif self.counter == 3:
            self.gen_menu()

        else:
            if self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_OFF:
                self.bluetooth.set_alsa_bluetooth_mac(self.descr[self.counter][2],self.descr[self.counter][0])

            elif self.descr[self.counter][1] == symbols.SYMBOL_BLUETOOTH_ON:
                self.bluetooth.pair(self.descr[self.counter][2])
                self.bluetooth.trust(self.descr[self.counter][2])
                self.gen_menu()
        await asyncio.sleep(1)


