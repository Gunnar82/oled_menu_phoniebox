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


from integrations.logging_config import *

logger = setup_logger(__name__)



class neopixel:
    busy = False
    last_leds_on = -1

    async def set(self):
        last_percent = -111
        last_color = None
        last_gradient = None
        last_brightness = -1
        percent = 100

        brightness_array = [0,self.usersettings.NEOPX_BRIGHTNESS_DAY, self.usersettings.NEOPX_BRIGHTNESS_NIGHT]
        current_brightness = 0

        while self.loop.is_running():
            try:
                if settings.mcp_leds_change:
                    settings.mcp_leds_change = False
                    current_brightness += 1



            except Exception as error:
                current_brightness = 0
                logger.error(f"change led brightness button: {error}")

            brightness = brightness_array[(current_brightness + 1) % len(brightness_array)]

            try:

                wechsel = int(time.monotonic() // 5) % 4

                if wechsel == 0: # Sleep Timer handling
                    if settings.job_t < 0 and settings.job_i < 0:
                        wechsel = 1

                if wechsel == 1: # Battery Handling
                    if "x728" not in settings.INPUTS:
                        wechsel = 2

                if wechsel == 2: # Battery Handling
                    if settings.percent_track < 0:
                        wechsel = 3

                if wechsel == 3: # Battery Handling
                    if settings.percent_playlist < 0:
                        wehcsel = 4

                # Berechnung der LED-Werte
                if (wechsel == 0):
                    if (settings.job_i <= settings.job_t or settings.job_t == -1) and settings.job_i > -1:
                        percent = int(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                        await self.send_to_daemon(percent, brightness, color=self.config.COLOR_JOB_I)
                    else:
                        seconds_till_shutdown = int(self.usersettings.shutdowntime - time.monotonic())
                        total_seconds_for_shutdown = int(self.usersettings.shutdowntime - self.usersettings.shutdownset)
                        percent = int((seconds_till_shutdown) / total_seconds_for_shutdown * 100)
                        await self.send_to_daemon(percent, brightness, color=self.config.COLOR_JOB_T)
                elif wechsel == 1:
                    percent = int(settings.battcapacity)
                    await self.send_to_daemon(percent, brightness, color=self.config.COLOR_X728_LOADING if settings.battloading else None)
                elif wechsel == 2:
                    percent = 100 - settings.percent_track
                    await self.send_to_daemon(percent, brightness, color=self.config.COLOR_TRACK, color2=self.config.COLOR2_TRACK ,blink_low=False)
                elif wechsel == 3:
                    percent = settings.percent_playlist
                    await self.send_to_daemon(percent, brightness, color=self.config.COLOR_PLAYLIST,blink_low=False)
                else:
                    await self.send_to_daemon(100)
            except Exception as error:
                print(f"NeoPixel async error: {error}")

            await asyncio.sleep(1)

    async def send_to_daemon(self, percent, brightness, color=None, color2=None, gradient=None, blink_low=True):
        """Async send an LED command to the NeoPixel ESP32 via USB Serial"""
        try:
            leds_on = int((percent/100) * self.config.LEDCOUNT)
            if (
                leds_on == getattr(self, "last_leds_on", None)
                and brightness == getattr(self,"last_brightness",-1)
                and color == getattr(self, "last_color", None)
                and gradient == getattr(self, "last_gradient", None)
            ):
                return  # nichts ändern

            self.last_leds_on = leds_on
            self.last_color = color
            self.last_gradient = gradient
            self.last_brightness = brightness

            cmd = {
                "cmd": "battery",
                "percent": percent,
                "brightness": brightness,
                "steps": 5,
                "delay": 0.05,
                "blink_low": 1 if blink_low else 0
            }
            if color:
                cmd["color"] = color
                cmd["color2"] = color2
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
            self.ser.write(line.encode())

        except Exception as e:
            print(f"Error sending to NeoPixel daemon via Serial: {e}")


    def set_led_count(self):
        # Serial senden
        if not hasattr(self, "ser") or self.ser is None:
            # automatisch USB Port suchen
            ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
            if not ports:
                print("Kein USB-Gerät gefunden")
                return
            self.ser = serial.Serial(ports[0], 115200, timeout=1)
            print(f"Verbunden mit {ports[0]}")

        cmd = {
            "cmd": "config",
            "led": self.config.LEDCOUNT
        }
        print (cmd)
        self.ser.write((json.dumps(cmd) + "\n").encode())


    def __init__(self, loop, usersettings, config):
        self.loop = loop
        self.config = config
        self.usersettings = usersettings
        self.ser = None
        settings.mcp_leds_change = False
        self.loop.create_task(self.set())
        self.brightness_day = True
        try:
            self.set_led_count()
        except Exception as error:
            logger.error (error)

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
