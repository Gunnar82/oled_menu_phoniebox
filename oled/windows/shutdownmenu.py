""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.playout as playout
import integrations.functions as fn

class Shutdownmenu(MenuBase):

    def __init__(self, windowmanager, mopidyconnection,title):
        super().__init__(windowmanager,title)

        self.mopidyconnection = mopidyconnection
        self.execshutdown = False
        self.execreboot = False

        self.descr.append(["Neustart OLED", "\uf0e2"])
        self.descr.append(["AUS Sofort", "\uf011"])
        self.descr.append(["Zurück", "\uf0a8"])
        self.descr.append(["Reboot", "\uf0e2"])
        self.descr.append(["Timer AUS", "\uf1f7"])
        self.descr.append(["Timer 15min", "\uf0a2"])
        self.descr.append(["Timer 30min", "\uf0a2"])
        self.descr.append(["Timer 60min", "\uf0a2"])
        self.descr.append(["Idle AUS", "\uf185"])
        self.descr.append(["Idle 5min", "\uf186"])
        self.descr.append(["Idle 15min", "\uf186"])


    def push_callback(self,lp=False):
        if self.counter == 0:
            fn.restart_oled()

        elif self.counter == 1:
            playout.savepos()
            self.mopidyconnection.stop()
            self.execshutdown = True
            print("Stopping event loop")
            self.loop.stop()
        elif self.counter == 2:
            self.windowmanager.set_window("mainmenu")
        elif self.counter == 3:
            self.windowmanager.set_window("start")
            self.mopidyconnection.stop()
            self.execreboot = True
            print("Stopping event loop")
            self.loop.stop()
        
        elif self.counter == 4:
            os.system("%s -c=shutdownafter -v=0" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 5:
            os.system("%s -c=shutdownafter -v=15" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 6:
            os.system("%s -c=shutdownafter -v=30" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 7:
            os.system("%s -c=shutdownafter -v=60" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 8:
            os.system("%s -c=setidletime -v=0" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 9:
            os.system("%s -c=setidletime -v=5" % settings.PLAYOUT_CONTROLS)
        elif self.counter == 10:
            os.system("%s -c=setidletime -v=20" % settings.PLAYOUT_CONTROLS)
        
        self.windowmanager.set_window("idle")
            #self.mopidyconnection.stop()
            #self.execreboot = True
            #print("Stopping event loop")
            #self.loop.stop()

