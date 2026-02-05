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

def next_item(lst, current):
    if not lst:
        return None

    try:
        i = lst.index(current)
    except ValueError:
        # aktuelles Item existiert nicht mehr
        return lst[0]

    return lst[(i + 1) % len(lst)]


class neopixel:
    busy = False
    last_leds_on = -1

    async def set(self):
        last_percent_batt = -111
        last_percent_track = -111
        last_percent_playlist = -111
        last_percent_job_i = -111
        last_percent_job_t = -111

        last_wechsel = time.monotonic()

        last_color = None
        last_gradient = None
        last_brightness = -1
        percent = 0

        brightness_array = [0,self.usersettings.NEOPX_BRIGHTNESS_DAY, self.usersettings.NEOPX_BRIGHTNESS_NIGHT]
        current_brightness_pos = 0
        last_change = -1
        wechsel = 0
        wechsel_array = []

        while self.loop.is_running():

            try:
                if settings.mcp_leds_change:
                    settings.mcp_leds_change = False
                    current_brightness_pos += 1
            except Exception as error:
                current_brightness = 0
                logger.error(f"change led brightness button: {error}")

            try:
                if "x728" in settings.INPUTS:
                    if not 1 in wechsel_array: wechsel_array.append(1)

                    if round(settings.battcapacity / 100 * self.config.LEDCOUNT) != round(last_percent_batt / 100 * self.config.LEDCOUNT):
                        percent = round(settings.battcapacity)
                        last_percent_batt = percent
                        logger.debug ("b",last_percent_batt)
                        wechsel = 1

                if (settings.job_i <= settings.job_t or settings.job_t == -1) and settings.job_i > -1:
                    percent = round(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                    if not 2 in wechsel_array: wechsel_array.append(2)

                    if round(percent  / 100 * self.config.LEDCOUNT) != round(last_percent_job_i / 100 * self.config.LEDCOUNT):
                        last_percent_job_i = percent
                        logger.debug ("i",last_percent_job_i)
                        wechsel = 2
                else:
                    if 2 in wechsel_array: wechsel_array.remove(2)


                if (settings.job_t <= settings.job_i or settings.job_i == -1) and settings.job_t > -1:

                    seconds_till_shutdown = round(self.usersettings.shutdowntime - time.monotonic())
                    total_seconds_for_shutdown = int(self.usersettings.shutdowntime - self.usersettings.shutdownset)
                    percent = round((seconds_till_shutdown) / total_seconds_for_shutdown * 100)


                    if not 3 in wechsel_array: wechsel_array.append(3)

                    if round(percent  / 100 * self.config.LEDCOUNT) != round(last_percent_job_t / 100 * self.config.LEDCOUNT):
                        last_percent_job_t = percent
                        logger.debug ("t",last_percent_job_t)
                        wechsel = 3
                else:
                    if 3 in wechsel_array: wechsel_array.remove(3)


                if settings.percent_track > -1:

                    if not 4 in wechsel_array: wechsel_array.append(4)

                    if round(settings.percent_track  / 100 * self.config.LEDCOUNT) != round(last_percent_track / 100 * self.config.LEDCOUNT):
                        last_percent_track = settings.percent_track
                        logger.debug ("tr",last_percent_track)
                        wechsel = 4
                else:
                    if 4 in wechsel_array: wechsel_array.remove(4)


                if settings.percent_playlist > -1:
                    if not 5 in wechsel_array: wechsel_array.append(5)

                    if round(settings.percent_playlist / 100 * self.config.LEDCOUNT) != round(last_percent_playlist / 100 * self.config.LEDCOUNT):
                        last_percent_playlist = settings.percent_playlist
                        logger.debug ("pl",last_percent_playlist)
                        wechsel = 5
                else:
                    if 5 in wechsel_array: wechsel_array.remove(5)

                if time.monotonic() > last_wechsel + 10 :
                    last_wechsel = time.monotonic()
                    wechsel = next_item(wechsel_array,wechsel)
            except:
                wechsel = 0

            brightness = brightness_array[(current_brightness_pos + 1) % len(brightness_array)]

            try:
                if last_change + 10 < time.monotonic():
                    last_change = time.monotonic()
                    wechsel = next_item(wechsel_array,wechsel)


                # Berechnung der LED-Werte
                if (wechsel == 1):
                    await self.send_to_daemon(last_percent_batt, brightness, color=self.config.COLOR_X728_LOADING if settings.battloading else None)
                    await asyncio.sleep(1)
                    last_change = time.monotonic()
                if (wechsel == 2):
                    await self.send_to_daemon(last_percent_job_i, brightness, color=self.config.COLOR_JOB_I)
                    await asyncio.sleep(1)
                    last_change = time.monotonic()
                if (wechsel == 3):
                    await self.send_to_daemon(last_percent_job_t, brightness, color=self.config.COLOR_JOB_T)
                    await asyncio.sleep(1)
                    last_change = time.monotonic()
                if (wechsel == 4):
                    await self.send_to_daemon(last_percent_track, brightness, color=self.config.COLOR_TRACK, color2=self.config.COLOR2_TRACK ,blink_low=False)
                    await asyncio.sleep(1)
                    last_change = time.monotonic()
                if (wechsel == 5):
                    await self.send_to_daemon(last_percent_playlist, brightness, color=self.config.COLOR_PLAYLIST)
                    await asyncio.sleep(1)
                    last_change = time.monotonic()

            except Exception as error:
                logger.error(f"NeoPixel async error: {error}")
            await asyncio.sleep(1)

    async def send_to_daemon(self, percent, brightness, color=None, color2="BLACK", gradient=None, blink_low=True):
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
            logger.error(f"Error sending to NeoPixel daemon via Serial: {e}")


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
