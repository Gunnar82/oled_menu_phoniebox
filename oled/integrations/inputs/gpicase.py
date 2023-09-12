import asyncio
import threading
import settings
import pygame
import time

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

        self.found_joystick = 0
        self.loop.create_task(self._poll_pygame_keys())

    async def _poll_pygame_keys(self):
        # for al the connected joysticks
        joysticks = []


        while self.loop.is_running():
            #self.clock.tick(60)
            for event in pygame.event.get():
                print (event)
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks.append(joy)
                if event.type == pygame.JOYHATMOTION:
                    x,y = event.value
                    if (y == -1): # keypad down
                        self.turn_callback(0,'8')
                    elif (y == 1): #keypad up
                        self.turn_callback(0,'2')
                    elif (x == -1): # keypad left
                        self.turn_callback(0,'4')
                    elif (x == 1): #keypas right
                         self.turn_callback(0,'6')
                elif event.type == pygame.JOYBUTTONUP:
                    if int(event.button) == 0: # A
                        self.push_callback()
                    elif int(event.button) == 1: #B
                        self.turn_callback(0,'#')
                    elif int(event.button) == 7: # START
                        self.turn_callback(0,'START')

            await asyncio.sleep(0.1)
