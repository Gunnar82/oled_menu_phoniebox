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


class mcp_23017_buttons:
    busy = False

    INTERRUPT_COMPARE_VALUE_A               = 0x06   # default comparison for interrupt on change
    INTERRUPT_CONTROL_A                     = 0x08   # interrupt control (0=interrupt on change, 1=interrupt on change from 0x06)
    INTERRUPT_FLAG_A                        = 0x0E   # interrupt flag
    INTERRUPT_CAPTURE_A                     = 0x10   # interrupt capture


    I2CADDR = 0x27 # valid range is 0x20 - self.I2CADDR
    PU_A    = 0x0C
    RD_A   = 0x12

    PULUPA = 0x0F #0x0F		# PullUp enable register base address
    PULUPB = 0xF0 #0xF0		# PullUp enable register base address
  
    # initialize I2C comm, 1 = rev2 Pi, 0 for Rev1 Pi
    i2c = smbus.SMBus(1) 


    def reset(self):

        self.i2c.write_byte_data(self.I2CADDR, 0x00, 0xFF) # IODIRA
        self.i2c.write_byte_data(self.I2CADDR, 0x04, self.config.GPINTENA) # INTERUPT_ENABLE_A
        self.i2c.write_byte_data(self.I2CADDR, 0x06, 0x00) # INTERUPT_COMPARE_VALUE
        self.i2c.write_byte_data(self.I2CADDR, 0x08, 0x00) # INTERRUPT_CONTROL_A
        self.i2c.write_byte_data(self.I2CADDR, 0x0E, 0xFF) # INTERRUPT_FLAG_A

        self.i2c.write_byte_data(self.I2CADDR, 0x0C, 0xFF) # PULLUP_A
        self.i2c.write_byte_data(self.I2CADDR, 0x12, 0xFF) # GENERAL_PURPOSE_A

        self.i2c.read_byte_data(self.I2CADDR,0x12)

    # get a keystroke from the keypad
    def getch(self):
        try:
            value = int(self.i2c.read_byte_data(self.I2CADDR,0x12))
            print (value)
            buttonstring = f"button_{value}"
            button = self.config.__dict__[buttonstring]
        except Exception as error:
            button = None
        return button #value

    def button_down_callback(self,channel):
        if not self.busy:
            try:
                gpio_state = GPIO.input(channel)
                self.busy = True
                button = self.getch()
                if button != None and gpio_state == 0:
                    if button == '*':
                        self.push_callback()
                    else:
                        self.turn_callback(0,button)
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

        GPIO.add_event_detect(config.INTPIN, GPIO.FALLING, callback=self.button_down_callback, bouncetime=150)


# test code

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
