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


    def get_led_value_from_value(self, value, only_current = True, blink_value = False):
        base_value = 0
        # Bestimmen des Basis-Rückgabewerts basierend auf dem `value`
        for threshold, return_value in self.config.value_thresholds:
            if value >= threshold:
                base_value = return_value
                base_index = threshold
                break

        if only_current:
            if blink_value and isinstance(base_value,list):
                self.blink_value = not self.blink_value

                return (base_value[0] if not self.blink_value else base_value[1])
            else:
                self.blink_value = False

                return (base_value[0] if isinstance(base_value,list) else base_value)

        # Bestimmen des abwechselnden Rückgabewerts basierend auf dem Aufruf
        result_value = 127 - self.config.value_thresholds[self.toggle_index][1]

        # Erhöhe den Index für den nächsten Funktionsaufruf
        self.toggle_index += 1

        # Wenn das Ende der Decrements-Liste erreicht ist, zurück auf den ersten Wert
        if 100 - self.config.value_thresholds[self.toggle_index][0] > base_value:
            self.toggle_index = 0

        # Multiplizieren des `base_value` mit dem abwechselnden Wert
        return (self.config.value_thresholds[self.toggle_index][1][0] if isinstance(self.config.value_thresholds[self.toggle_index][1],list) else self.config.value_thresholds[self.toggle_index])

    async def set(self):

        self.i2c.write_byte_data(self.config.ADDR, self.config.IOADDR, 0x00) # IODIRB

        self.toggle_index = 0  # Steuert den Rückgabewert, beginnt bei 0


        pos = 0

        set_job = False

        while self.loop.is_running():
            try:

                if  settings.mcp_leds_change:
                    settings.mcp_leds_change = False
                    pos += 1

                if pos > 2: pos = 0


                if not set_job and (settings.job_t >= 0 or settings.job_i >= 0):
                    set_job = True
                    pos = 0

                if pos == 0 and (settings.job_t >= 0 or settings.job_i >= 0):

                    if ( settings.job_i <= settings.job_t or settings.job_t == -1) and settings.job_i > -1: 

                        percent  = int(settings.job_i / (self.usersettings.IDLE_POWEROFF * 60) * 100)
                        value = 127 - self.get_led_value_from_value(percent,blink_value = True) + 128

                    else:

                        # ausgehend von 30 min als max
                        seconds_till_shutdown = int(self.usersettings.shutdowntime - time.monotonic())
                        total_seconds_for_shutdown = int(self.usersettings.shutdowntime - self.usersettings.shutdownset)
                        percent  = int((seconds_till_shutdown) /  total_seconds_for_shutdown * 100)
                        value = self.get_led_value_from_value(percent, blink_value = True ) 

                elif pos == 0:

                    set_job = False

                    if "x728" in settings.INPUTS:
                        pos = 1
                    else:
                        pos = 2

                if "x728" in settings.INPUTS  and pos == 1:
                    value = self.get_led_value_from_value(settings.battcapacity, only_current = not settings.battloading, blink_value = True) + 128
                elif pos == 1:
                    pos = 2

                if pos == 2: # pos >= 2:
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
        self.blink_value = False

        self.toggle_index = 0  # Steuert, welcher Decrement verwendet wird, beginnt bei 0
        self.loop.create_task(self.set())



# test code

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
