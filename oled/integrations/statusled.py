#  MBTechWorks.com 2016
#  Pulse Width Modulation (PWM) demo to cycle brightness of an LED

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
import settings
import asyncio

class statusled:
    async def _pulse(self):
        # main loop of program
        dc=0                               # set dc variable to 0 for 0%
        self.pwm.start(dc)                      # Start PWM with 0% duty cycle
        try:
            while settings.STATUS_LED_ENABLED:                      # Loop until Ctl C is pressed to stop.
                cloop = 0
                while cloop < self.pulsing:
                    cloop += 1
                    self.pwm.start(dc)
                    for dc in range(0, 101, 5):    # Loop 0 to 100 stepping dc by 5 each loop
                        self.pwm.ChangeDutyCycle(dc)
                        time.sleep(0.05)             # wait .05 seconds at current LED brightness
                    for dc in range(95, 0, -5):    # Loop 95 to 5 stepping dc down by 5 each loop
                        self.pwm.ChangeDutyCycle(dc)
                        time.sleep(0.05)             # wait .05 seconds at current LED brightness
                    self.pwm.stop()

                await asyncio.sleep(3)

        except:
            pass

    def __init__(self,loop):
        self.loop = loop
        self.pulsing = 0

        GPIO.setmode(GPIO.BCM)    # Set Pi to use pin number when referencing GPIO pins.
                              # Can use GPIO.setmode(GPIO.BCM) instead to use 
                              # Broadcom SOC channel names.
        GPIO.setup(settings.STATUS_LED_PIN, GPIO.OUT)  # Set GPIO pin 12 to output mode.
        self.pwm = GPIO.PWM(settings.STATUS_LED_PIN, 100)   # Initialize PWM on pwmPin 100Hz frequency

        self.loop.create_task(self._pulse())

    def startpulse(self,count = 1):
        self.pulsing = count

    def stoppulse(self):
        self.pulsing = 0
        self.pwm.stop()

    def stoploop(self):
        GPIO.cleanup()                     # resets GPIO ports used back to input mode
