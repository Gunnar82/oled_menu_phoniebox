import asyncio
import threading
import settings
import pygame


class pygameInput():

    def __init__(self, loop, turn_callback, push_callback):
        print("Polling PyGame keys")
        pygame.init()
        self.clock = pygame.time.Clock()

        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback

        self.loop.create_task(self._poll_pygame_keys())


    async def _poll_pygame_keys(self):
        # for al the connected joysticks
        joysticks = []

        for i in range(0, pygame.joystick.get_count()):
            # create an Joystick object in our list
            joysticks.append(pygame.joystick.Joystick(i))
            # initialize the appended joystick (-1 means last array item)
            joysticks[-1].init()
            # print a statement telling what the name of the controller is
            print ("Detected joystick: %s" % (joysticks[-1].get_name()))

        while self.loop.is_running():
            self.clock.tick(60)
            event = pygame.event.poll()

            if event.type == pygame.JOYHATMOTION:
                x,y = event.value
                if (y == -1):
                    self.turn_callback(0,'8')
                elif (y == 1):
                    self.turn_callback(0,'2')
                elif (x == -1):
                    self.turn_callback(0,'4')
                elif (x == 1):
                     self.turn_callback(0,'6')

            elif event.type == pygame.JOYBUTTONUP:
                if int(event.button) == 0:
                    self.push_callback()
                elif int(event.button) == 1:
                    self.turn_callback(0,'#')


            await asyncio.sleep(0.1)
