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
        self.i2c.write_byte_data(self.I2CADDR, 0x01, 0x00) # IODIRB

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
                if "x728" in settings.INPUTS:
                    value = self.get_led_value_from_value(settings.battcapacity, only_current = not settings.battloading)

                    self.i2c.write_byte_data(self.I2CADDR, 0x13, value) # GENERAL_PURPOSE_B

            except Exception as error:
                print (error)

            await asyncio.sleep(1)

    # initialize the keypad class
    def __init__(self, loop, config):
        self.loop = loop
        self.config = config
        self.I2CADDR = config.ADDR
        self.toggle_index = 0  # Steuert, welcher Decrement verwendet wird, beginnt bei 0
        self.decrements = [1, 2, 4, 8, 16, 32, 64]  # Liste der Decrements (Potenzen von 2)
        self.thresholds = [94, 85, 75, 60, 50, 30, 15]  # Schwellenwerte

        self.loop.create_task(self.set())



# test code

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
