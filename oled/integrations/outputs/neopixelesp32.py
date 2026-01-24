#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import signal
import sys
import asyncio
import serial
import json
import settings
import glob

class neopixel:
    busy = False
    last_leds_on = -1

    async def set(self):
        last_percent = -111
        last_color = None
        last_gradient = None
        percent = 100
        brightness = self.usersettings.NEOPX_BRIGHTNESS_DAY

        while self.loop.is_running():
            try:
                if settings.mcp_leds_change:
                    settings.mcp_leds_change = False
                    self.brightness_day = not self.brightness_day
                    settings.mcp_leds_change = False
                    print ("BD",self.brightness_day)

            except Exception as error:
                brightness = self.usersettings.NEOPX_BRIGHNESS_DAY
                logger.error(f"change led brightness button: {error}")

            brightness = self.usersettings.NEOPX_BRIGHTNESS_DAY if self.brightness_day else self.usersettings.NEOPX_BRIGHTNESS_NIGHT

            try:

                wechsel = (int(time.monotonic() // 10) % 2) == 0
                # Berechnung der LED-Werte
                if (settings.job_t >= 0 or settings.job_i >= 0) and not (wechsel and "x728" in settings.INPUTS):
                    if (settings.job_i <= settings.job_t or settings.job_t == -1) and settings.job_i > -1:
                        percent = int(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                        await self.send_to_daemon(percent, brightness, color=[0,255,0])
                    else:
                        seconds_till_shutdown = int(self.usersettings.shutdowntime - time.monotonic())
                        total_seconds_for_shutdown = int(self.usersettings.shutdowntime - self.usersettings.shutdownset)
                        percent = int((seconds_till_shutdown) / total_seconds_for_shutdown * 100)
                        await self.send_to_daemon(percent, brightness, color=[255,0,0])
                elif "x728" in settings.INPUTS:
                    percent = int(settings.battcapacity)
                    await self.send_to_daemon(percent, brightness, color=[0,0,255] if settings.battloading else None)
                else:
                    await self.send_to_daemon(100)
            except Exception as error:
                print(f"NeoPixel async error: {error}")

            await asyncio.sleep(3)

    async def send_to_daemon(self, percent, brightness, color=None, gradient=None):
        """Async send an LED command to the NeoPixel ESP32 via USB Serial"""
        try:
            leds_on = int((percent/100) * self.config.LEDCOUNT)
            if (
                leds_on == getattr(self, "last_leds_on", None)
                and color == getattr(self, "last_color", None)
                and gradient == getattr(self, "last_gradient", None)
            ):
                return  # nichts ändern

            self.last_leds_on = leds_on
            self.last_color = color
            self.last_gradient = gradient

            cmd = {
                "cmd": "battery",
                "percent": percent,
                "brightness": brightness,
                "steps": 5,
                "delay": 0.05
            }
            if color:
                cmd["color"] = color
            if gradient:
                cmd["gradient"] = gradient

            # Serial senden
            if not hasattr(self, "ser") or self.ser is None:
                # automatisch USB Port suchen
                ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
                if not ports:
                    print("Kein USB-Gerät gefunden")
                    return
                self.ser = serial.Serial(ports[0], 115200, timeout=1)
                print(f"Verbunden mit {ports[0]}")

            line = json.dumps(cmd) + "\n"
            print (line)
            self.ser.write(line.encode())

        except Exception as e:
            print(f"Error sending to NeoPixel daemon via Serial: {e}")

    def __init__(self, loop, usersettings, config):
        self.loop = loop
        self.config = config
        self.usersettings = usersettings
        self.ser = None
        settings.mcp_leds_change = False
        self.loop.create_task(self.set())
        self.brightness_day = True

    def close(self):
        """Schließt den Serial-Port sicher"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.closed = True

    def __del__(self):
        """Destructor: wird aufgerufen, wenn Objekt garbage-collected wird"""
        self.close()

# signal handler
def signal_handler(sig, frame):
    sys.exit(0)
