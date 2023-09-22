""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas
from PIL import ImageFont
import settings
import os
import integrations.playout as playout
import asyncio

from integrations.functions import restart_oled, get_timeouts

class Shutdownmenu(MenuBase):

    def __init__(self, windowmanager, loop, mopidyconnection,title):
        super().__init__(windowmanager,loop,title)

        self.mopidyconnection = mopidyconnection
        self.descr.append(["Neustart OLED", "\uf0e2"])
        self.descr.append(["AUS Sofort", "\uf011"])
        self.descr.append(["Reboot", "\uf0e2"])
        self.descr.append(["Timer AUS", "\uf1f7"])
        self.descr.append(["Timer 15min", "\uf0a2"])
        self.descr.append(["Timer 30min", "\uf0a2"])
        self.descr.append(["Timer 60min", "\uf0a2"])
        self.descr.append(["Idle AUS", "\uf185"])
        self.descr.append(["Idle 5min", "\uf186"])
        self.descr.append(["Idle 15min", "\uf186"])


    async def push_handler(self):
        await asyncio.sleep(1)
        if self.counter == 1:
            restart_oled()

        elif self.counter == 2:
            playout.savepos()
            self.mopidyconnection.stop()
            settings.shutdown_reason = settings.SR2
            print("Stopping event loop")
            self.loop.stop()
        elif self.counter == 3:
            self.windowmanager.set_window("start")
            self.mopidyconnection.stop()
            settings.shutdown_reason = settings.SR3
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

        get_timeouts()

        self.windowmanager.set_window("idle")
            #self.mopidyconnection.stop()
            #self.execreboot = True
            #print("Stopping event loop")
            #self.loop.stop()


    def turn_callback(self, direction, key=None):

        super().turn_callback(direction,key=key)

        if key:
            if key == 'A':
                self.set_busy("Austimer 30 min","\uf0a2")
                os.system("%s -c=shutdownafter -v=30" % settings.PLAYOUT_CONTROLS)
            elif key == 'B':
                self.set_busy("Austimer deaktiviert","\uf1f7")
                os.system("%s -c=shutdownafter -v=0" % settings.PLAYOUT_CONTROLS)

            elif key == 'C':
                playout.savepos()
                self.mopidyconnection.stop()
                settings.shutdown_reason = settings.SR2
                print("Stopping event loop")
                self.loop.stop()
            elif key == 'D':
                restart_oled()

