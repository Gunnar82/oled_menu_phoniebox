#  MBTechWorks.com 2016
#  Pulse Width Modulation (PWM) demo to cycle brightness of an LED

import RPi.GPIO as GPIO   # Import the GPIO library.
import time               # Import time library
import settings
import asyncio

class statusled:
    async def _pulse(self):
        try:
            status = self.musicmanager.status()
            if status['state'] == "stop":
                self.pulsing = 1 
        except:
            self.pulsing = 0


        # main loop of program
        dc=0                               # set dc variable to 0 for 0%
        self.pwm.start(dc)                      # Start PWM with 0% duty cycle
        try:
            while settings.STATUS_LED_ENABLED and self.loop.is_running():                      # Loop until Ctl C is pressed to stop.
                try:
                    status = self.musicmanager.status()
                    print (settings.job_i)
                    print (settings.job_t)

                    if (settings.job_i >= 0 and settings.job_i <= 5) or ( settings.job_t >= 0 and settings.job_t <= 5):
                        self.pulsing = 2
                    elif settings.battcapacity <= settings.X728_BATT_LOW:
                        self.pulsing = 3
                    elif status['state'] == 'play':
                        self.pulsing = 0

                    elif status['state'] == "pause" or status['state'] == "stop":
                        self.pulsing = 1
                except:
                     self.pulsing = 10

                cloop = 0
                while cloop < self.pulsing:
                    cloop += 1
                    self.pwm.start(dc)
                    for dc in range(0, 10, 1):    # Loop 0 to 100 stepping dc by 5 each loop
                        self.pwm.ChangeDutyCycle(dc)
                        time.sleep(0.05)             # wait .05 seconds at current LED brightness
                    for dc in range(10, 0, -1):    # Loop 95 to 5 stepping dc down by 5 each loop
                        self.pwm.ChangeDutyCycle(dc)
                        time.sleep(0.05)             # wait .05 seconds at current LED brightness
                    self.pwm.stop()

                await asyncio.sleep(3)

        except:
            pass

    def __init__(self,loop,musicmanager):
        self.loop = loop
        self.musicmanager = musicmanager
        GPIO.setmode(GPIO.BCM)    # Set Pi to use pin number when referencing GPIO pins.
                              # Can use GPIO.setmode(GPIO.BCM) instead to use 
                              # Broadcom SOC channel names.
        GPIO.setup(settings.STATUS_LED_PIN, GPIO.OUT)  # Set GPIO pin 12 to output mode.
        self.pwm = GPIO.PWM(settings.STATUS_LED_PIN, 100)   # Initialize PWM on pwmPin 100Hz frequency

        self.loop.create_task(self._pulse())

    def startpulse(self,count = 1):
        print (count)
        self.pulsing = count

    def stoppulse(self):
        self.pulsing = 0
        self.pwm.stop()

    def stoploop(self):
        GPIO.cleanup()                     # resets GPIO ports used back to input mode
