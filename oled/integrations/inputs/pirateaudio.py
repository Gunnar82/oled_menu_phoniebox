""" Rotary encoder setup """
import asyncio
import threading
import settings # pylint: disable=import-error
import time
import integrations.functions as fn

from integrations.logging import *

try:
    #Only avaiable on Raspberry
    import RPi.GPIO as GPIO # pylint: disable=import-error
except ImportError:
    pass

class PirateAudio():
    def __init__(self, loop, turn_callback, push_callback):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback

        GPIO.setmode(GPIO.BCM)

        #Config for pins!
        self.lockrotary = threading.Lock() #create lock for rotary switch
        self._setup_gpio(settings.PIN_A)
        self._setup_gpio(settings.PIN_B)
        self._setup_gpio(settings.PIN_X)
        self._setup_gpio(settings.PIN_Y)
        log(lINFO,"using gpiocontrol")

    def _button_press(self, *args):
        try:
            time.sleep (0.1)
            if not settings.callback_active:
                settings.callback_active = True
                key = args[0]
                log(lDEBUG,"gpiocontrol args %s"%(format(args)))

                if key == settings.PIN_A:
                    self.turn_callback(0,'#')
                elif key == settings.PIN_B:
                    self.turn_callback(-1)
                elif key == settings.PIN_X:
                    self.push_callback()
                elif key == settings.PIN_Y:
                    self.turn_callback(1)
        finally:
            log(lDEBUG,"gpiocontrol: ende")
            time.sleep(0.1)
            settings.callback_active = False



    def _setup_gpio(self, pin):

        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Push Button
        GPIO.add_event_detect(pin,GPIO.RISING, callback=self._button_press, bouncetime=300)


    @staticmethod
    def cleanup():
        print("Cleaning up GPIO")
        if not settings.EMULATED:
            GPIO.cleanup()
