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
        self.descr.append(["IP vorlesen", "\uf012"])
        self.descr.append(["Start-Laufstärke AUS", "\uf026"])
        self.descr.append(["Start-Laufstärke 30%", "\uf027"])
        self.descr.append(["Start-Laufstärke 50%", "\uf027"])
        self.descr.append(["Start-Laufstärke 100%", "\uf028"])
        self.descr.append(["Max-Laufstärke AUS", "\uf026"])
        self.descr.append(["Max-Laufstärke 30%", "\uf027"])
        self.descr.append(["Max-Laufstärke 50%", "\uf027"])
        self.descr.append(["Max-Laufstärke 100%", "\uf028"])
        self.descr.append(["\u0394vol 1%", "\uf026"])
        self.descr.append(["\u0394vol 3%", "\uf027"])
        self.descr.append(["\u0394vol 5%", "\uf027"])
        self.descr.append(["\u0394vol 8%", "\uf028"])


    def push_handler(self):
        if self.counter == 1:
            restart_oled()
        elif self.counter == 2:
            #playout.pc_toggle()
            settings.shutdown_reason = settings.SR2
            self.windowmanager.set_window("ende")
        elif self.counter == 3:
            settings.shutdown_reason = settings.SR3
            self.windowmanager.set_window("ende")
        else:
            if self.counter == 4:
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
            elif self.counter == 11:
                run_command("%s -c=readwifiipoverspeaker" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 12:
                run_command("%s -c=setstartupvolume -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 13:
                run_command("%s -c=setstartupvolume -v=30" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 14:
                run_command("%s -c=setstartupvolume -v=50" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 15:
                run_command("%s -c=setstartupvolume -v=100" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 16:
                run_command("%s -c=setmaxvolume -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 17:
                run_command("%s -c=setmaxvolume -v=30" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 18:
                run_command("%s -c=setmaxvolume -v=50" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 19:
                run_command("%s -c=setmaxvolume -v=100" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 20:
                run_command("%s -c=setvolstep -v=1" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 21:
                run_command("%s -c=setvolstep -v=3" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 22:
                run_command("%s -c=setvolstep -v=5" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 23:
                run_command("%s -c=setvolstep -v=8" % cfg_file_folder.PLAYOUT_CONTROLS)

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

