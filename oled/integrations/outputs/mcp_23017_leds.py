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
        for threshold, return_value in self.value_thresholds:
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

        self.value_thresholds = [
            (94, 127),  # value >= 94 -> 127
            (86, 63),   # value >= 86 -> 63
            (75, 31),   # value >= 75 -> 31
            (46, 15),   # value >= 60 -> 15
            (35, 7),    # value >= 50 -> 7
            (25, 3),    # value >= 15 -> 3
            (15, 1),     # else -> 1
            (-1, 0),     # else -> 1
        ]

        while self.loop.is_running():
            try:
                value = 0
                elapsed_time = time.monotonic() - settings.lastinput

                gerade =  (int(elapsed_time) // 20) % 2 == 0 

                if not settings.ledson: value = 0

                elif (settings.job_t >= 0 or settings.job_i >= 0) and gerade:
                    if settings.job_i < settings.job_t or settings.job_t < 0: 
                        percent  = int(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                    else:
                        # ausgehend von 30 min als max

                        percent  = int((self.usersettings.shutdowntime - time.monotonic()) /  ( 30 * 60) * 100)

                    value = self.get_led_value_from_value(percent) + 128 #

                elif "x728" in settings.INPUTS:
                    value = self.get_led_value_from_value(settings.battcapacity, only_current = not settings.battloading)


                self.i2c.write_byte_data(self.config.ADDR, self.config.OUTPUT_REGISTER, value) # GENERAL_PURPOSE_B

            except Exception as error:
                print (error)

            await asyncio.sleep(0.5)

    # initialize the keypad class
    def __init__(self, loop, usersettings, config):
        self.loop = loop
        self.config = config
        self.usersettings = usersettings
        settings.ledson = True

        self.toggle_index = 0  # Steuert, welcher Decrement verwendet wird, beginnt bei 0
        self.decrements = [1, 2, 4, 8, 16, 32, 64]  # Liste der Decrements (Potenzen von 2)
        self.thresholds = [94, 85, 75, 60, 50, 30, 15]  # Schwellenwerte

        self.loop.create_task(self.set())



# test code

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
