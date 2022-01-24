import struct
import smbus
import sys
import time
import RPi.GPIO as GPIO
import integrations.playout as playout


# Global settings
# GPIO is 26 for x728 v2.0, GPIO is 13 for X728 v1.2/v1.3
GPIO_PORT 	= 26
GPIO_SHUTDOWN   = 5
GPIO_BOOT	= 12

I2C_ADDR    = 0x36

GPIO.setmode(GPIO.BCM)
#GPIO.setup(GPIO_BOOT, GPIO.OUT)
#GPIO.output(GPIO_BOOT,1)
GPIO.setup(GPIO_PORT, GPIO.OUT)
GPIO.setup(GPIO_SHUTDOWN, GPIO.IN)

GPIO.setwarnings(False)

#def shutdown_handler(channel):
#    playout.pc_shutdown()


#GPIO.add_event_detect(GPIO_SHUTDOWN, GPIO.RISING, callback=shutdown_handler)

bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

def shutdown_handler(channel):
    print ("SD")

def readVoltage():

     address = I2C_ADDR
     read = bus.read_word_data(address, 2)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     voltage = swapped * 1.25 /1000/16
     return voltage

def readCapacity():

     address = I2C_ADDR
     read = bus.read_word_data(address, 4)
     swapped = struct.unpack("<H", struct.pack(">H", read))[0]
     capacity = swapped/256
     return capacity


def getSymbol():
    capacity = readCapacity()
    print (capacity)
    if capacity < 15:
        return "\uf244"
    elif capacity < 30:
        return "\uf243"
    elif capacity < 50:
        return "\uf242"
    elif capacity < 90:
        return "\uf241"
    else:
        return "\uf240"
