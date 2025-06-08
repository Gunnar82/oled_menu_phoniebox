import struct
import smbus
import sys
import time
import RPi.GPIO as GPIO
#import integrations.playout as playout
import settings

import config.symbols as symbols
import config.colors as colors

import config.shutdown_reason as SR
import asyncio
from datetime import datetime

from integrations.logging_config import *
from integrations.functions import set_lastinput,restart_oled
logger = setup_logger(__name__)


class x728:

    GPIO_BUTTON  = 5 # INPUT BUTTON PRESSED
    GPIO_BOOT	= 12
    GPIO_POWERFAIL = 6
    GPIO_BUZZER = 20 # BUZZER
    GPIO_LED     = 26 #


    def __init__(self,loop,windowmanager,led,usersettings):
        # Global settings
        self.usersettings = usersettings
        self.led = led
        self.loop = loop
        self.windowmanager = windowmanager
        self.voltage = 0
        self.oldvoltage = 0
        self.__capacity = -1
        self.__loading = False
        self.I2C_ADDR    = 0x36

        self.battload_emerg_started = False

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.GPIO_POWERFAIL, GPIO.IN)
        GPIO.setup(self.GPIO_BUTTON, GPIO.IN)

        GPIO.setup(self.GPIO_BOOT, GPIO.OUT)
        GPIO.output(self.GPIO_BOOT, GPIO.HIGH)

        GPIO.add_event_detect(self.GPIO_POWERFAIL, GPIO.BOTH, callback=self.gpio_callback, bouncetime=100)
        GPIO.add_event_detect(self.GPIO_BUTTON, GPIO.BOTH, callback=self.gpio_callback, bouncetime=100)

        self.gpio_callback(self.GPIO_POWERFAIL)

        self.bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

        self.loop.create_task(self.__handler())


    async def __handler(self):
        while self.loop.is_running():
            try:
                self.readVoltage()
                settings.battcapacity = self.readCapacity()
                symbols.SYMBOL_BATTERY = self.getSymbol()
                settings.battload_color = self.get_battload_color()

                if not self.battload_emerg_started: self. is_battload_emerg()
            except Exception as error:
                logger.error(f"_handler_ {error}")
                print ("err x728")

            await asyncio.sleep (10)

    def is_battload_emerg(self):
        if not self.__loading:
            if self.__capacity >= 0 and self.__capacity <= self.usersettings.X728_BATT_EMERG:
                self.battlaod_emerg_started = True
                if not self.battlaod_emerg_started: set_lastinput()
        else:
            self.battlaod_emerg_started = False

    def gpio_callback (self,channel):
        status = GPIO.input(channel) == 1 # GPIO_POWERFAIL: 0 == angeschlossen, 1 = ohne Kabel
        logger.debug(f"handle GPIO {channel}, status: {status}")

        if channel == self.GPIO_POWERFAIL:
            self.get_powerfail_state(status)
        elif channel == self.GPIO_BUTTON:
            self.button_pressed = status
            if status:
                self.button_pressed_time = time.monotonic()
                self.loop.run_in_executor(None,self._handle_button_pressed)


    def _handle_button_pressed(self):

        handling = True

        while self.loop.is_running() and handling:
            timediff = time.monotonic() - self.button_pressed_time

            logger.debug(f"handle_button_pressed: timediff {timediff}, pressed: {self.button_pressed} ")


            if  (timediff >= 6 and self.button_pressed) or (settings.job_t > 0):
                if self.led is not None:
                    self.led.set_permanent()

                logger.debug(">6sek oder job_t")
                handling = False
                settings.shutdown_reason = SR.SR6 if settings.job_t > 0 else SR.SR2
                self.windowmanager.set_window("ende")

            elif timediff < 6:
                if self.button_pressed:
                    if self.led is not None:
                        self.led.set_dark()
                else:
                    logger.debug("> 2 && < 6 sek: reboot")
                    handling = False
                    restart_oled()

            time.sleep(1)

    def readVoltage(self):
         read = self.bus.read_word_data(self.I2C_ADDR, 2)
         swapped = struct.unpack("<H", struct.pack(">H", read))[0]
         self.voltage = swapped * 1.25 /1000/16


    def readCapacity(self):

         read = self.bus.read_word_data(self.I2C_ADDR, 4)
         swapped = struct.unpack("<H", struct.pack(">H", read))[0]
         cap = int(swapped/256)
         self.__capacity = cap 
         return cap


    def get_powerfail_state(self,status):
        logger.debug(f"Powerfail ist {status}")
        self.__loading = not status
        settings.battloading = not status
        if not status: self.battlod_emerg_started = False

    def getSymbol(self):
        if self.__capacity < 10:
            return "\uf244"
        elif self.__capacity < 30:
            return "\uf243"
        elif self.__capacity < 60:
            return "\uf242"
        elif self.__capacity < 90:
             return "\uf241"	
        else:
            return "\uf240"


    def get_battload_color(self):
        if settings.battloading:
            return colors.COLOR_BLUE
        elif self.__capacity == -1:
            return "WHITE"
        elif self.__capacity >= 70:
            return colors.COLOR_GREEN
        elif self.__capacity >= 40:
            return colors.COLOR_YELLOW
        elif self.__capacity >= 15: #self.usersettings.X728_BATT_LOW:
            return colors.COLOR_ORANGE
        else:
            return colors.COLOR_RED


    def shutdown(self):
        logger.debug("x728 shutdown")
