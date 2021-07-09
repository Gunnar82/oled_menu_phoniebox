""" Hifiberry Powercontroller setup """
from smbus import SMBus
import asyncio
import threading
import settings # pylint: disable=import-error
import _thread
import keyboard
#import pigpio

try:
    #Only avaiable on Raspberry
    import RPi.GPIO as GPIO # pylint: disable=import-error
except ImportError:
    pass


ADDRESS=0x77

REG_VL=0xfd
REG_VH=0xfe
REG_ROTARYCHANGE=0x0c
REG_LEDMODE=0x01
REG_LEDR=0x02
REG_LEDG=0x03
REG_LEDB=0x04
REG_BUTTONMODE=0x05
REG_BUTTONSTATE=0x06
REG_POWEROFFTIMER=0x09
REG_BUTTONPOWEROFFTIME=0x0a
REG_INTERRUPTPIN=0x0e

LEDMODE_STATIC=0
LEDMODE_PULSING=1
LEDMODE_BLINK=2
LEDMODE_FLASH=3
LEDMODE_OFF=4

# Use Pi's GPIO15 (RXD) as interrupt pin
INTPINS = {
    0: 0,
    1: 4,
    2: 15, 
    3: 14
    }

BUTTONMODE_SHORT_LONG_PRESS=0

MIN_VERSION=4  # requires functionality to set interrupt pin that was introduced in v4


class PowerController():

    def __init__(self, loop, turn_callback, push_callback):
        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback
        self.bus=SMBus(1)
        self.intpin=0
        self.intpinpi=0

        try:
            self.intpin = int(settings.INTPIN)
            if self.intpin==0:
                self.intpin=1

            self.intpinpi=INTPINS[self.intpin]
        except Exception as e:
            self.intpin = 1

        try:
            vl = self.bus.read_byte_data(ADDRESS, REG_VL)
            vh = self.bus.read_byte_data(ADDRESS, REG_VH)
            version=256*vh+vl
            if version<MIN_VERSION:
                raise ("ERROR:PC:MINVERSION")

        except Exception as e:
            raise ("PC UNREADABLE")
        #self.lockpc = threading.Lock()

        self.init_controller()
        self._setup_gpio(self.intpinpi)
        #self.loop.create_task(self._poll_pygame_keys())
#        keyboard.add_hotkey('sleep', lambda: self.pushlong_callback())
        keyboard.add_hotkey('Esc', lambda: self.push_callback())

        keyboard.add_hotkey('Right', lambda: self.turn_right())
        keyboard.add_hotkey('Left', lambda: self.turn_left())
        keyboard.add_hotkey('Up', lambda: self.turn_up())
        keyboard.add_hotkey('Down', lambda: self.turn_down())

        pc_thread = _thread.start_new_thread(self.pc_run,())



#        if settings.EMULATED:
#            self.loop.create_task(self._poll_pygame_keys())
#            print("Polling PyGame keys")
#        else:
#            #Config for pins!
#            self.current_clk = 1
#            self.current_dt = 1
#            self.lockrotary = threading.Lock() #create lock for rotary switch
#            self._setup_gpio(settings.PIN_CLK, settings.PIN_DT, settings.PIN_SW)
#            print("Using rotary encoder interrupts")



    def shutdown(self):
        print ("pc-poweroff")
        #self.bus.write_byte_data(ADDRESS, REG_BUTTONSTATE, 0)
        self.bus.write_byte_data(ADDRESS, REG_LEDR, 0)
        self.bus.write_byte_data(ADDRESS, REG_LEDG, 100)
        self.bus.write_byte_data(ADDRESS, REG_LEDB, 0)
        self.bus.write_byte_data(ADDRESS, REG_LEDMODE, LEDMODE_BLINK)
        #self.bus.write_byte_data(ADDRESS, REG_POWEROFFTIMER, 30) # poweroff in 30 seconds

    def twos_comp(self, val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val

    def init_controller(self):
        self.bus.write_byte_data(ADDRESS, REG_LEDR, 0)
        self.bus.write_byte_data(ADDRESS, REG_LEDG, 100)
        self.bus.write_byte_data(ADDRESS, REG_LEDB, 0)
        self.bus.write_byte_data(ADDRESS, REG_LEDMODE, LEDMODE_STATIC)

        self.bus.write_byte_data(ADDRESS, REG_BUTTONPOWEROFFTIME, 20) # We deal with this directly
        self.bus.write_byte_data(ADDRESS, REG_BUTTONMODE, BUTTONMODE_SHORT_LONG_PRESS)
        self.bus.write_byte_data(ADDRESS, REG_INTERRUPTPIN, self.intpin) # Set interrupt pin 
        self.bus.write_byte_data(ADDRESS, REG_BUTTONSTATE, 0)
#        self.update_playback_state(STATE_UNDEF)
        self.ready=True



    def pc_run(self):
        while True:
            if GPIO.wait_for_edge(self.intpinpi,GPIO.BOTH,10):

                try:
                    rotary_change=self.twos_comp(self.bus.read_byte_data(ADDRESS, REG_ROTARYCHANGE),8) # this is a signed byte
                    button_state=self.bus.read_byte_data(ADDRESS, REG_BUTTONSTATE)
    
                    if rotary_change != 0:
                    #self.volchange(rotary_change*self.stepsize)
                        self.turn_callback(rotary_change)

    
                    if button_state == 1:
                        # short pressure_network
                        self.bus.write_byte_data(ADDRESS, REG_BUTTONSTATE, 0)
                        self.push_callback()
                    elif button_state == 2:
                        # Long press
                        self.bus.write_byte_data(ADDRESS, REG_BUTTONSTATE, 0)
                        self.push_callback(_lp=True)
                        #self.shutdown();

                except Exception as e:
                    print("Couldn't read data form I2C, aborting... (%s)", e)
                #self.push_callback()

    def _rotary_turn(self, channel):
        switch_a = GPIO.input(settings.PIN_CLK)
        switch_b = GPIO.input(settings.PIN_DT)

        if self.current_clk == switch_a and self.current_dt == switch_b:
            #Same interrupt as before? -> Bouncing -> no action
            pass
        else:
            #refresh saved state
            self.current_clk = switch_a
            self.current_dt = switch_b

            if (switch_a and switch_b): #both ones active
                self.lockrotary.acquire()
                if channel == settings.PIN_DT: #Direction depends on which one was last
                    self.turn_callback(1)
                else:
                    self.turn_callback(-1)
                self.lockrotary.release()

    def turn_left(self):
        self.turn_callback(-1, _key='left')


    def turn_right(self):
        self.turn_callback(1, _key='right')

    def turn_up(self):
        self.turn_callback(-1, _key='up')


    def turn_down(self):
        self.turn_callback(1, _key='down')

    def pushlong_callback(self):
        print ("long2")

        self.push_callback(_lp=True)

    def _setup_gpio(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Interupt_pin
        #GPIO.add_event_detect(pin, GPIO.FALLING, callback=self._rotary_push, bouncetime=300)

    async def _poll_pygame_keys(self):
        while self.loop.is_running():
            if keyboard.is_pressed('Up'):
                self.turn_callback(1)
            elif keyboard.is_pressed('Down'):
                self.turn_callback(-1)
            elif keyboard.is_pressed('Esc'):
                self.push_callback()

            await asyncio.sleep(0.05)

    @staticmethod
    def cleanup():
        print("Cleaning up GPIO")
        if not settings.EMULATED:
            GPIO.cleanup()
