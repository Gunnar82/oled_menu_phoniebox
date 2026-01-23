#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import signal
import sys
import asyncio
import socket
import json
import settings

SOCKET_PATH = "/tmp/neopixel.sock"

class neopixel:
    busy = False
    last_leds_on = -1

    async def set(self):
        self.toggle_index = 0
        last_percent = -111
        last_color = None
        last_gradient = None
        percent = 100

        while self.loop.is_running():
            try:
                # Berechnung der LED-Werte

                if (settings.job_t >= 0 or settings.job_i >= 0):
                    if (settings.job_i <= settings.job_t or settings.job_t == -1) and settings.job_i > -1:
                        percent = int(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                        await self.send_to_daemon(percent,color=[255,0,255])
                    else:
                        # ausgehend von 30 min als max
                        seconds_till_shutdown = int(self.usersettings.shutdowntime - time.monotonic())
                        total_seconds_for_shutdown = int(self.usersettings.shutdowntime - self.usersettings.shutdownset)
                        percent = int((seconds_till_shutdown) / total_seconds_for_shutdown * 100)
                        await self.send_to_daemon(percent,color=[255,0,0])
                elif "x728" in settings.INPUTS:
                    percent  = int(settings.battcapacity)
                    await self.send_to_daemon(percent,color=[0,0,255] if settings.battloading else None)

                # → Sende den Wert an den NeoPixel-Daemon
                else:
                   await self.send_to_daemon(100)

            except Exception as error:
                print(f"NeoPixel async error: {error}")

            await asyncio.sleep(2)

    async def send_to_daemon(self, percent, color=None, gradient=None):
        """Async send an LED command to the NeoPixel daemon via UNIX socket"""
        try:
            leds_on = int((percent/100) * self.config.LEDCOUNT)
            if (
                leds_on == getattr(self, "last_leds_on", None)
                and color == getattr(self, "last_color", None)
                and gradient == getattr(self, "last_gradient", None)
            ):
                return

            self.last_leds_on = leds_on
            self.last_color = color
            self.last_gradient = gradient



            cmd = {
                "cmd": "battery",
                "percent": percent,
                "steps": 5,
                "delay": 0.05
            }

            if color:
                cmd["color"] = color
            if gradient:
                cmd["gradient"] = gradient

            # Socket senden
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(SOCKET_PATH)
            s.send(json.dumps(cmd).encode())
            s.close()
        except Exception as e:
            print(f"Error sending to NeoPixel daemon: {e}")

    def __init__(self, loop, usersettings, config):
        self.loop = loop
        self.config = config
        self.usersettings = usersettings
        settings.mcp_leds_change = False
        self.loop.create_task(self.set())


# signal handler
def signal_handler(sig, frame):
    sys.exit(0)
