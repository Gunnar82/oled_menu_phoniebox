""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import config.colors as colors
import config.file_folder as cfg_file_folder
import config.shutdown_reason as SR
import os
import integrations.playout as playout


from integrations.functions import restart_oled, get_timeouts, run_command

class Shutdownmenu(MenuBase):

    def __init__(self, windowmanager, loop, mopidyconnection,nowplaying,title):
        super().__init__(windowmanager,loop,title)

        self.mopidyconnection = mopidyconnection
        self.nowplaying = nowplaying
        self.descr.append(["Neustart OLED", "\uf0e2"])  #1
        self.descr.append(["AUS Sofort", "\uf011"])     #2
        self.descr.append(["Reboot", "\uf0e2"])         #3
        self.descr.append(["Timer AUS", "\uf1f7"])      #4
        self.descr.append(["Timer Eingabe", "\uf0a2"])  #5
        self.descr.append(["Idle AUS", "\uf185"])             #6
        self.descr.append(["Idle Eingabe", "\uf186"])         #7
        self.descr.append(["AUS nach STOP", "\uf011"])        #8
        self.descr.append(["AUS nach Titeln", "\uf011"])      #9
        self.descr.append(["IP vorlesen", "\uf012"])          #10
        self.descr.append(["VOLstart AUS", "\uf026"])         #11
        self.descr.append(["VOLstart Eingabe", "\uf028"])     #12
        self.descr.append(["VOLmax AUS", "\uf026"])           #13
        self.descr.append(["VOLmax Eingabe", "\uf028"])       #14
        self.descr.append(["\u0394vol 1%", "\uf026"])         #15
        self.descr.append(["\u0394vol 3%", "\uf027"])         #16
        self.descr.append(["\u0394vol 5%", "\uf027"])         #17
        self.descr.append(["\u0394vol 8%", "\uf028"])         #18


    def push_handler(self):
        if self.counter == 1:
            restart_oled()
        elif self.counter == 2:
            #playout.pc_toggle()
            settings.shutdown_reason = SR.SR2
            self.windowmanager.set_window("ende")
        elif self.counter == 3:
            settings.shutdown_reason = SR.SR3
            self.windowmanager.set_window("ende")
        else:
            if self.counter == 4:
                run_command("%s -c=shutdownafter -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 5:
                value = self.windowmanager.getValue(startpos=30,unit=" min")
                run_command("%s -c=shutdownafter -v=%d" % (cfg_file_folder.PLAYOUT_CONTROLS,value))
            elif self.counter == 6:
                run_command("%s -c=setidletime -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 7:
                value = self.windowmanager.getValue(startpos=15,unit=" min")
                run_command("%s -c=setidletime -v=%d" % (cfg_file_folder.PLAYOUT_CONTROLS,value))
            elif self.counter == 8:
                settings.shutdown_reason = SR.SR4
                self.windowmanager.windows["ende"].wait4end = True
                self.windowmanager.set_window("ende")
            elif self.counter == 9:
                if not self.nowplaying._state == "stop":
                    value = self.windowmanager.getValue(startpos=int(self.nowplaying._song),vmin=int(self.nowplaying._song),vmax=int(self.nowplaying._playlistlength),unit="")
                    settings.shutdown_reason = SR.SR4
                    self.windowmanager.windows["ende"].wait4track = int(value)
                    self.windowmanager.set_window("ende")

            elif self.counter == 10:
                run_command("%s -c=readwifiipoverspeaker" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 11:
                run_command("%s -c=setstartupvolume -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 12:
                value = self.windowmanager.getValue(startpos=90,unit=" %")
                run_command("%s -c=setstartupvolume -v=%d" % (cfg_file_folder.PLAYOUT_CONTROLS,value))
            elif self.counter == 13:
                run_command("%s -c=setmaxvolume -v=0" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 14:
                value = self.windowmanager.getValue(startpos=100,unit=" %")
                run_command("%s -c=setmaxvolume -v=%d" % (cfg_file_folder.PLAYOUT_CONTROLS,value))
            elif self.counter == 15:
                run_command("%s -c=setvolstep -v=1" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 16:
                run_command("%s -c=setvolstep -v=3" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 17:
                run_command("%s -c=setvolstep -v=5" % cfg_file_folder.PLAYOUT_CONTROLS)
            elif self.counter == 18:
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
                self.musicmanagerconnection.stop()
                settings.shutdown_reason = SR.SR2
                print("Stopping event loop")
                self.loop.stop()
            elif key == '0':
                restart_oled()

