""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.bluetooth

class Headphonemenu(MenuBase):

    def __init__(self, windowmanager,title):
        super().__init__(windowmanager,title)
        self.descr.append(["Zurück","\uf0a8"])
        self.descr.append([settings.NAME_DEV_BT_1 + " " + settings.ENABLED_DEV_BT_1, "\uf293" if settings.ENABLED_DEV_BT_1 == "ON" else "\uf057"])
        self.descr.append([settings.NAME_DEV_BT_2 + " " + settings.ENABLED_DEV_BT_2, "\uf293" if settings.ENABLED_DEV_BT_2 == "ON" else "\uf057"])
        self.descr.append(["Lautsprecher","\uf028"])
        integrations.bluetooth.enable_dev_local()


    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 1 and settings.ENABLED_DEV_BT_1 == "ON":
            integrations.bluetooth.enable_dev_bt_1()
            self.windowmanager.set_window("mainmenu")    
        elif self.counter == 2 and settings.ENABLED_DEV_BT_1 == "ON":
            integrations.bluetooth.enable_dev_bt_2()
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 3:
            integrations.bluetooth.enable_dev_local()
            self.windowmanager.set_window("mainmenu")

