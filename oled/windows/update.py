""" Playlist menu """
import settings,colors,symbols

import time
import requests
import htmllistparse
import subprocess,os
import asyncio
import shutil

from ui.menubase import MenuBase
import time
import integrations.playout as playout
from integrations.functions import get_size

import config.online as cfg_online
import config.file_folder as cfg_file_folder
import config.services as cfg_services

class UpdateMenu(MenuBase):
    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager, loop, title)
        self.loop = loop
        self.window_on_back = "idle"
        self.timeout = False
        self.processing = False
        self.totalsize = 0
        self.descr.append(["Update Radio","\uf019"])
        for srv in cfg_services.RESTART_LIST:
            self.descr.append(["Restart %s" % (srv),"\uf01e",srv])

    def activate(self):
        self.cmd = ""

    def exec_command(self):
        try:
            self.processing = True
            subprocess_result = subprocess.Popen(self.cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            subprocess_output = subprocess_result.communicate()[0],subprocess_result.returncode
            if subprocess_result.returncode == 0:
                self.set_busy(self.descr[self.counter][0],symbols.SYMBOL_PASS, busytext2="Erfolgreich")
            else:
                self.set_busy(self.descr[self.counter][0],symbols.SYMBOL_FAIL, busytext2=subprocess_output[0].decode())
        finally:
            time.sleep(5)
            self.processing = False


    async def push_handler(self,button = '*'):
        if self.counter == 1:
            if cfg_online.UPDATE_RADIO:
                self.cmd = "wget  --no-verbose --no-check-certificate  -r %s  --no-parent -A txt -nH -P %s/" %(cfg_online.ONLINE_RADIO_URL,cfg_file_folder.AUDIO_BASEPATH_BASE)
                self.set_busy("Aktualisiere Radiostationen",self.descr[self.counter][1],busyrendertime=10)
                self.loop.run_in_executor(None,self.exec_command)
            else:
                self.set_busy("Online Updates deaktiviert")
        else:
            self.cmd = "sudo systemctl restart %s" % (self.descr[self.counter][2])
            self.set_busy(self.descr[self.counter][0],self.descr[self.counter][1],busyrendertime=10)
            self.loop.run_in_executor(None,self.exec_command)



    def render(self):
        if self.processing:
            self.renderbusy()
        else:
            super().render()
