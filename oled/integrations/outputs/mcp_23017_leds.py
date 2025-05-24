#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

"""

# Original from William Henning
# http://www.mikronauts.com/raspberry-pi/raspberry-pi-4x4-keypad-i2c-MCP23017-howto/

import smbus
import time
import signal
import sys
import RPi.GPIO as GPIO
import asyncio
import settings

class mcp_23017_leds:
    busy = False
  
    # initialize I2C comm, 1 = rev2 Pi, 0 for Rev1 Pi
    i2c = smbus.SMBus(1) 


    def get_led_value_from_value(self, value, only_current = True):
        base_value = 0
        # Bestimmen des Basis-Rückgabewerts basierend auf dem `value`
        for threshold, return_value in self.config.value_thresholds:
            if value >= threshold:
                base_value = return_value
                break

        if only_current: return base_value

        # Bestimmen des abwechselnden Rückgabewerts basierend auf dem Aufruf
        result_value = self.decrements[self.toggle_index]

        # Erhöhe den Index für den nächsten Funktionsaufruf
        self.toggle_index += 1

        # Wenn das Ende der Decrements-Liste erreicht ist, zurück auf den ersten Wert
        if self.decrements[self.toggle_index] > base_value:
            self.toggle_index = 0

        # Multiplizieren des `base_value` mit dem abwechselnden Wert
        return self.decrements[self.toggle_index]

    async def set(self):

        self.i2c.write_byte_data(self.config.ADDR, self.config.IOADDR, 0x00) # IODIRB

        self.toggle_index = 0  # Steuert den Rückgabewert, beginnt bei 0
        self.decrements = [0, 1, 3, 7, 15, 31, 63, 127]  # 2er Potenzen minus 1


        pos = 0

        while self.loop.is_running():
            try:

                if  settings.mcp_leds_change:
                    settings.mcp_leds_change = False
                    pos += 1

                if pos > 2: pos = 0

                if pos == 0 and (settings.job_t >= 0 or settings.job_i >= 0):

                    if ( settings.job_i <= settings.job_t or settings.job_t == -1) and settings.job_i > -1: 

                        percent  = int(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                        value = self.get_led_value_from_value(percent) + 128 #

                    else:

                        # ausgehend von 30 min als max
                        seconds_till_shutdown = int(self.usersettings.shutdowntime - time.monotonic())
                        total_seconds_for_shutdown = int(self.usersettings.shutdowntime - self.usersettings.shutdownset)
                        percent  = int((seconds_till_shutdown) /  total_seconds_for_shutdown * 100)
                        value = 255 - self.get_led_value_from_value(percent) #

                elif pos == 0 and not "x728" in settings.INPUTS: # KEIN Timeout
                    pos == 1

                elif "x728"in settings.INPUTS  and pos == 1:
                    value = self.get_led_value_from_value(settings.battcapacity, only_current = not settings.battloading)

                elif pos == 1:
                    pos = 2

                else: # pos >= 2:
                    value = 0

                self.i2c.write_byte_data(self.config.ADDR, self.config.OUTPUT_REGISTER, value) # GENERAL_PURPOSE_B

            except Exception as error:
                print (f"{error}")

            await asyncio.sleep(0.5)

    # initialize the keypad class
    def __init__(self, loop, usersettings, config):
        self.loop = loop
        self.config = config
        self.usersettings = usersettings
        settings.mcp_leds_change = False

        self.toggle_index = 0  # Steuert, welcher Decrement verwendet wird, beginnt bei 0
        self.decrements = [1, 2, 4, 8, 16, 32, 64]  # Liste der Decrements (Potenzen von 2)
        self.thresholds = [94, 85, 75, 60, 50, 30, 15]  # Schwellenwerte

        self.loop.create_task(self.set())



# test code

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
