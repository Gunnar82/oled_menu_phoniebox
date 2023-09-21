""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.bluetooth as bt
from integrations.logging import *
import time
import asyncio

 
class Headphonemenu(MenuBase):

    def get_dev_status(self, first=False):
        print ("updating device status")
        self.bt1_status = bt.output_status(settings.ALSA_DEV_BT_1)
        self.bt2_status = bt.output_status(settings.ALSA_DEV_BT_2)
        self.local_status = bt.output_status(settings.ALSA_DEV_LOCAL)

        if not first:
            print (lDEBUG3,"bt1_status: %s"%(self.bt1_status))
            self.descr[1] = [settings.NAME_DEV_BT_1 + " " + self.bt1_status, "\uf057" if not settings.ENABLED_DEV_BT_1 else "\uf293" if self.bt1_status == "enabled" else "\uf294"]
            self.descr[2] = [settings.NAME_DEV_BT_2 + " " + self.bt2_status, "\uf057" if not settings.ENABLED_DEV_BT_2 else "\uf293" if self.bt2_status == "enabled" else "\uf294"]
            self.descr[3] = [settings.ALSA_DEV_LOCAL + " " + self.local_status,"\uf028" if self.local_status == "enabled" else "\uf026"]


    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager,title)
        self.loop = loop
        self.get_dev_status(first=True)
        self.descr.append(["Zurück","\uf0a8"])
        self.descr.append([settings.NAME_DEV_BT_1 + " " + self.bt1_status, "\uf057" if not settings.ENABLED_DEV_BT_1 else "\uf293" if self.bt1_status == "enabled" else "\uf294"])
        self.descr.append([settings.NAME_DEV_BT_2 + " " + self.bt2_status, "\uf057" if not settings.ENABLED_DEV_BT_2 else "\uf293" if self.bt2_status == "enabled" else "\uf294"])
        self.descr.append([settings.ALSA_DEV_LOCAL + " " + self.local_status,"\uf028" if self.local_status == "enabled" else "\uf057"])

    def deactivate(self):
        print ("ende")

    async def handle_push(self):
        await asyncio.sleep(1)
        if self.counter == 1:
            if settings.ENABLED_DEV_BT_1:
                bt.enable_dev_bt_1()
        elif self.counter == 2:
            if settings.ENABLED_DEV_BT_2:
                bt.enable_dev_bt_2()
        elif self.counter == 3:
            bt.enable_dev_local()
        time.sleep(2)
        self.get_dev_status()

    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        else:
            self.set_busy("Verbinde",settings.SYMBOL_BLUETOOTH_OFF, self.descr[self.counter][0])
            self.loop.create_task(self.handle_push())
