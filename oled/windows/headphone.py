""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings, colors,symbols
import os
from integrations.logging import *
import time
import asyncio

 
class Headphonemenu(MenuBase):


    def __init__(self, windowmanager,loop,bluetooth,title):
        super().__init__(windowmanager,loop,title)
        self.bluetooth = bluetooth
        self.descr.append([settings.ALSA_DEV_LOCAL,symbols.SYMBOL_SPEAKER])
        self.descr.append(["",symbols.SYMBOL_HEADPHONE])
        self.descr.append(["",""])


        for device in self.bluetooth.all_bt_dev:
            self.descr.append([device[1],symbols.SYMBOL_BLUETOOTH_OFF,device[0]])

    def set_current_bt_name(self):
        self.descr[2][0]="BT: %s" %(self.bluetooth.selected_bt_name)


    def deactivate(self):
        print ("ende")

    def activate (self):
        self.set_current_bt_name()

    def turn_callback(self,direction, key = None):
        super().turn_callback(direction,key)
        if self.counter == 3:
            if direction > 0 or key in ['right','up','2', '4'] :
                self.counter = 4
            elif  direction < 0 or key in ['left','down','6','8']:
                self.counter = 2

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
            pass
        else:
            self.bluetooth.set_alsa_bluetooth_mac(self.descr[self.counter][2],self.descr[self.counter][0])
            self.set_current_bt_name()
        await asyncio.sleep(1)


