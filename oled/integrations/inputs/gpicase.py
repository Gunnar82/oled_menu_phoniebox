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

    def __init__(self, loop, turn_callback, push_callback,windowmanager,nowplaying):
        print("Polling PyGame keys")
        pygame.init()
        pygame.joystick.init()
        pygame.mixer.init(44100, -16,2,512)
        pygame.mixer.pause()
        pygame.mixer.quit()
        pygame.mouse.set_visible(False)

        self.windowmanager = windowmanager
        self.clock = pygame.time.Clock()

        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback

        self.powerbtn = -1

        self.powerpressed = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(27, GPIO.OUT)
        GPIO.output(27, GPIO.HIGH)
        GPIO.add_event_detect(26,GPIO.BOTH, callback=self._button_press, bouncetime=100)

        self.loop.create_task(self._poll_pygame_keys())

    def _button_press(self, *args):
        try:
            gpio26 = GPIO.input(26)
            self.powerbtn = gpio26
            if settings.job_t >= 0:
                #if self.powerbtn != gpio26:
                log (lDEBUG,"Shutdown Timer active - Waiting")
                if gpio26 == 0:
                    if self.powerpressed < 1:
                        self.powerpressed += 1
                        self.windowmanager.set_window("ende")
                else:
                    self.powerpressed = 0
                    self.windowmanager.set_window("idle")
            elif not settings.callback_active:
                settings.callback_active = True
                if self.nowplaying.input_is_online:
                    playout.savepos_online(self.nowplaying.filename,self.nowplaying._elapsed)
                playout.savepos()
                #self.mopidyconnection.stop()
                log(lINFO,"Stopping event loop")
                playout.pc_shutdown()
                time.sleep(1)
                self.loop.stop()

        finally:
            log(lDEBUG,"gpicase power handling: ende")
            time.sleep(0.1)
            settings.callback_active = False



    async def _poll_pygame_keys(self):
        # for al the connected joysticks
        joysticks = []
        shutdown = False

        while self.loop.is_running() and not shutdown:
            #self.clock.tick(60)
            for event in pygame.event.get():
                log(lDEBUG,"pygame: %s " % (event))
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks.append(joy)
                elif event.type == pygame.QUIT:
                    shutdown = True
                elif event.type == pygame.JOYHATMOTION:
                    x,y = event.value
                    if (y == -1 and x == 0): # keypad down
                        log (lDEBUG2, "pygame: down")
                        self.turn_callback(0,'down')
                    elif (y == 1 and x == 0): #keypad up
                        log (lDEBUG2, "pygame: up")
                        self.turn_callback(0,'up')
                    elif (x == -1 and y == 0): # keypad left
                        log (lDEBUG2, "pygame: left")
                        self.turn_callback(0,'left')
                    elif (x == 1 and y == 0): #keypas right
                         log (lDEBUG2, "pygame: right")
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
                        self.turn_callback(0,'hl')
                    elif int(event.button) == 5: # HR
                        self.turn_callback(0,'hr')
                    elif int(event.button) == 6: # START
                        self.turn_callback(0,'select')
                    elif int(event.button) == 7: # START
                        self.turn_callback(0,'start')

            await asyncio.sleep(0.1)

    def quit(self):
        log(lERROR,"Shutting Down Pygame")
        #pygame.joystick.quit()
        #pygame.display.quit()
        #pygame.quit()