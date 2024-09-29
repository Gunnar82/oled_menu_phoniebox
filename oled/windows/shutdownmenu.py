""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.file_folder as cfg_file_folder

import os
import integrations.playout as playout


from integrations.functions import restart_oled, get_timeouts, run_command

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


    def push_handler(self):
        if self.counter == 1:
            restart_oled()

        elif self.counter == 2:
            playout.pc_toggle()
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
            run_command("%s -c=shutdownafter -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
        elif self.counter == 5:
            run_command("%s -c=shutdownafter -v=15" % cfg_file_folder.PLAYOUT_CONTROLS)
        elif self.counter == 6:
            run_command("%s -c=shutdownafter -v=30" % cfg_file_folder.PLAYOUT_CONTROLS)
        elif self.counter == 7:
            run_command("%s -c=shutdownafter -v=60" % cfg_file_folder.PLAYOUT_CONTROLS)
        elif self.counter == 8:
            run_command("%s -c=setidletime -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
        elif self.counter == 9:
            run_command("%s -c=setidletime -v=5" % cfg_file_folder.PLAYOUT_CONTROLS)
        elif self.counter == 10:
            run_command("%s -c=setidletime -v=15" % cfg_file_folder.PLAYOUT_CONTROLS)

        get_timeouts()


    def turn_callback(self, direction, key=None):

        super().turn_callback(direction,key=key)

        if key:
            if key == 'A':
                self.set_busyinfo(item = "Austimer 30 min",symbol="\uf0a2",wait=5)
                run_command("%s -c=shutdownafter -v=30" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif key == 'B':
                self.set_busyinfo(item="Austimer deaktiviert",symbol="\uf1f7",wait=5)
                run_command("%s -c=shutdownafter -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)

            elif key == 'C':
                playout.savepos()
                self.mopidyconnection.stop()
                settings.shutdown_reason = settings.SR2
                print("Stopping event loop")
                self.loop.stop()
            elif key == '0':
                restart_oled()

