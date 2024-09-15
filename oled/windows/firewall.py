""" Shutdown menu """
from ui.menubase import MenuBase
from luma.core.render import canvas

import settings

import logging

from integrations.logging_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

import config.colors as colors
from integrations.functions import run_command, get_firewall_state, enable_firewall, disable_firewall
import socket
import subprocess
import os
import asyncio
import re

import config.services as cfg_services


class Firewallmenu(MenuBase):

    def __init__(self, windowmanager,loop):
        super().__init__(windowmanager,loop,"Firewall")
        self.counter = 0
        self.changerender = True
        self._fw_status = "n/a"
        self.descr.append(["Firewall STATUS","\uf058"])
        self.descr.append(["Firewall EIN","\uf01b"])
        self.descr.append(["Firewall AUS","\uf01a"])

    async def push_handler(self):
        await asyncio.sleep(1)
        if self.counter == 2:
            enable_firewall()
        elif self.counter == 3:
            disable_firewall()
        await asyncio.sleep(5)


    def activate(self):
        self._active = True
        self.loop.create_task(self._get_firewallstatus())

    def deactivate(self):
        self._active = False


    async def _get_firewallstatus(self):
        while self.loop.is_running() and self._active:
            try:

                state = get_firewall_state()
                self.descr[1][0] = "Firewall ist " + ("AUS" if "deny" not in state else "EIN")

            except Exception as e:
                logger.error(e)

            await asyncio.sleep(1)

