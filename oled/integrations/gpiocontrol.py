""" Rotary encoder setup """
import asyncio
import threading
import settings # pylint: disable=import-error


try:
    #Only avaiable on Raspberry
    import RPi.GPIO as GPIO # pylint: disable=import-error
except ImportError:
    pass

class GPIOControl():
    def __init__(self, loop, turn_callback, push_callback):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback


        #Config for pins!
        self.lockrotary = threading.Lock() #create lock for rotary switch
        self._setup_gpio(settings.PIN_A)
        self._setup_gpio(settings.PIN_B)
        self._setup_gpio(settings.PIN_X)
        self._setup_gpio(settings.PIN_Y)
        print("using gpiocontrol")

    def _rotary_turn(self, channel):
        key = channel
        print (key)
        del channel

        if key == settings.PIN_A:
            self.turn_callback(0,'#')
        elif key == settings.PIN_B:
            self.turn_callback(-1)
        elif key == settings.PIN_X:
            self.push_callback()
        elif key == settings.PIN_Y:
            self.turn_callback(1)






    def _setup_gpio(self, pin):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Push Button
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self._rotary_turn, bouncetime = 100)


    @staticmethod
    def cleanup():
        print("Cleaning up GPIO")
        if not settings.EMULATED:
            GPIO.cleanup()
