import asyncio
import threading
import settings
import pygame
import time

import integrations.playout as playout
from integrations.logging import *

try:
    #Only avaiable on Raspberry
    import RPi.GPIO as GPIO # pylint: disable=import-error
except ImportError:
    pass


class pygameInput():

    def __init__(self, loop, turn_callback, push_callback):
        print("Polling PyGame keys")
        pygame.init()
        pygame.joystick.init()
        self.clock = pygame.time.Clock()

        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback

        self.powerbtn = -1

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(27, GPIO.OUT)
        GPIO.output(27, GPIO.HIGH)
        GPIO.add_event_detect(26,GPIO.BOTH, callback=self._button_press, bouncetime=500)

        self.loop.create_task(self._poll_pygame_keys())


    def _button_press(self, *args):
        try:
            gpio26 = GPIO.input(26)

            
            time.sleep (0.1)
            if settings.job_t >= 0:
                #if self.powerbtn != gpio26:
                self.powerbtn = gpio26
                log (lDEBUG,"Shutdown Timer active - Waiting")
                self.turn_callback(0,'GPI_PWR_OFF' if gpio26 == 0 else 'GPI_PWR_ON')
            elif not settings.callback_active:
                settings.callback_active = True
                playout.savepos()
                #self.mopidyconnection.stop()
                #self.execshutdown = True
                log(lINFO,"Stopping event loop")
                self.loop.stop()
                playout.pc_shutdown()

        finally:
            log(lDEBUG,"gpicase power handling: ende")
            time.sleep(0.1)
            settings.callback_active = False



    async def _poll_pygame_keys(self):
        # for al the connected joysticks
        joysticks = []


        while self.loop.is_running():
            #self.clock.tick(60)
            for event in pygame.event.get():
                #print (event)
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks.append(joy)
                if event.type == pygame.JOYHATMOTION:
                    x,y = event.value
                    if (y == -1): # keypad down
                        self.turn_callback(0,'down')
                    elif (y == 1): #keypad up
                        self.turn_callback(0,'up')
                    elif (x == -1): # keypad left
                        self.turn_callback(0,'left')
                    elif (x == 1): #keypas right
                         self.turn_callback(0,'right')
                elif event.type == pygame.JOYBUTTONUP:
                    if int(event.button) == 0: # A
                        self.push_callback()
                    elif int(event.button) == 1: #B
                        self.turn_callback(0,'#')
                    elif int(event.button) == 2: # X
                        self.turn_callback(0,'X')
                    elif int(event.button) == 3: # Y
                        self.turn_callback(0,'Y')
                    elif int(event.button) == 4: # HL
                        self.turn_callback(0,'HL')
                    elif int(event.button) == 5: # HR
                        self.turn_callback(0,'HR')
                    elif int(event.button) == 6: # START
                        self.turn_callback(0,'SELECT')
                    elif int(event.button) == 7: # START
                        self.turn_callback(0,'START')

            await asyncio.sleep(0.1)
