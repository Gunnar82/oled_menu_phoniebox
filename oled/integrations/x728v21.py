import struct
import smbus
import sys
import time
import RPi.GPIO as GPIO
#import integrations.playout as playout
import settings

import config.symbols as symbols

import asyncio
from datetime import datetime

from integrations.logging_config import *

logger = setup_logger(__name__)


class x728:

    def readVoltage(self):
         read = self.bus.read_word_data(self.I2C_ADDR, 2)
         swapped = struct.unpack("<H", struct.pack(">H", read))[0]
         self.voltage = swapped * 1.25 /1000/16


    def readCapacity(self):

         read = self.bus.read_word_data(self.I2C_ADDR, 4)
         swapped = struct.unpack("<H", struct.pack(">H", read))[0]
         self.capacity = swapped/256

    async def _handler(self):
        while self.loop.is_running():
            try:
                self.readVoltage()
                self.readCapacity()

                settings.battcapacity = self.capacity
                symbols.SYMBOL_BATTERY = self.getSymbol()

            except:
                print ("err x728")

            await asyncio.sleep (10)


    def __init__(self,loop):
        # Global settings
        self.loop = loop
        # GPIO is 26 for x728 v2.0, GPIO is 13 for X728 v1.2/v1.3
        self.GPIO_PORT 	= 26
        self.GPIO_SHUTDOWN   = 5
        self.GPIO_BOOT	= 12
        self.GPIO_POWERFAIL = 6
        self.voltage = 0
        self.capacity = 0
        self.oldvoltage = 0
        self.oldcapacity = -1
        self.loading = False
        self.I2C_ADDR    = 0x36

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_POWERFAIL, GPIO.IN)
        GPIO.add_event_detect(self.GPIO_POWERFAIL, GPIO.BOTH, callback=self.powerfail_callback, bouncetime=100)
        self.get_powerfail_state()

        self.bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

        self.loop.create_task(self._handler())

    def powerfail_callback (self,channel):
        self.get_powerfail_state()


    def get_powerfail_state(self):
        status = GPIO.input(self.GPIO_POWERFAIL) == 1 # 0 == angeschlossen, 1 = ohne Kabel
        logger.debug(f"Powerfail ist {status}")
        settings.battloading = not status

    def getSymbol(self):
        if self.capacity < 10:
            return "\uf244"
        elif self.capacity < 30:
            return "\uf243"
        elif self.capacity < 60:
            return "\uf242"
        elif self.capacity < 90:
             return "\uf241"
        else:
            return "\uf240"

