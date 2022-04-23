import struct
import smbus
import sys
import time
import RPi.GPIO as GPIO
#import integrations.playout as playout
import settings
import asyncio
from datetime import datetime


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
        olddate = datetime.now()
        while self.loop.is_running():
            try:
                self.readVoltage()
                self.readCapacity()

                settings.battcapacity = self.capacity
                settings.battsymbol = self.getSymbol()
                if (datetime.now() - olddate).total_seconds() >= 60:
                    settings.battloading = ((self.oldvoltage < self.voltage) and (self.oldcapacity < self.capacity))
                    self.oldvoltage = self.voltage
                    self.oldcapacity = self.capacity
                    olddate = datetime.now()
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
        self.voltage = 0
        self.capacity = 0
        self.oldvoltage = 0
        self.oldcapacity = 0
        self.loading = False


        self.I2C_ADDR    = 0x36

        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(GPIO_BOOT, GPIO.OUT)
        #GPIO.output(GPIO_BOOT,1)
        #GPIO.setup(self.GPIO_PORT, GPIO.OUT)
        #GPIO.setup(self.GPIO_SHUTDOWN, GPIO.IN)

        #GPIO.setwarnings(False)

        #GPIO.add_event_detect(GPIO_SHUTDOWN, GPIO.RISING, callback=shutdown_handler)

        self.bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

        self.loop.create_task(self._handler())

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

