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


class mcp_23017_keys:
    busy = False

    INTERRUPT_ENABLE_A                      = 0x04   # interrupt on change (0=disable, 1=enable)
    INTERRUPT_COMPARE_VALUE_A               = 0x06   # default comparison for interrupt on change
    INTERRUPT_CONTROL_A                     = 0x08   # interrupt control (0=interrupt on change, 1=interrupt on change from 0x06)
    INTERRUPT_FLAG_A                        = 0x0E   # interrupt flag
    INTERRUPT_CAPTURE_A                     = 0x10   # interrupt capture


    I2CADDR = 0x27 # valid range is 0x20 - self.I2CADDR
    IODIR_A = 0x00
    PU_A    = 0x0C
    RD_A   = 0x12

    PULUPA = 0x0F #0x0F		# PullUp enable register base address
    PULUPB = 0xF0 #0xF0		# PullUp enable register base address
  
    # initialize I2C comm, 1 = rev2 Pi, 0 for Rev1 Pi
    i2c = smbus.SMBus(1) 


    def reset(self):

        self.i2c.write_byte_data(self.I2CADDR,self.INTERRUPT_FLAG_A,0xFF)
        self.i2c.write_byte_data(self.I2CADDR,self.INTERRUPT_COMPARE_VALUE_A,0x00)
        self.i2c.write_byte_data(self.I2CADDR,self.INTERRUPT_ENABLE_A,0xFF)
        self.i2c.write_byte_data(self.I2CADDR,self.INTERRUPT_CONTROL_A,0x00)

        self.i2c.write_byte_data(self.I2CADDR, self.IODIR_A, 0xFF)
        self.i2c.write_byte_data(self.I2CADDR, self.PU_A, 0xFF)
        self.i2c.write_byte_data(self.I2CADDR, self.RD_A, 0xFF)
        self.i2c.read_byte_data(self.I2CADDR,0x12)

    # get a keystroke from the keypad
    def getch(self):
        try:
            value = int(self.i2c.read_byte_data(self.I2CADDR,0x12))
            keystring = f"key_{value}"
            key = self.config.__dict__[keystring]
        except Exception as error:
            key = None

        return key #value

    def button_down_callback(self,channel):
        if not self.busy:
            try:
                gpio_state = GPIO.input(channel)
                self.busy = True
                key = self.getch()
                if key != None and gpio_state == 0:
                    if key == '*':
                        self.push_callback()
                    else:
                        self.turn_callback(0,key)
            finally:
                time.sleep(0.2)
                self.reset()
                self.busy = False

    # initialize the keypad class
    def __init__(self, loop, turn_callback, push_callback, config):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback
        self.config = config
        self.I2CADDR = config.ADDR
        self.reset()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.INTPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(config.INTPIN, GPIO.BOTH, callback=self.button_down_callback, bouncetime=150)


# test code

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
