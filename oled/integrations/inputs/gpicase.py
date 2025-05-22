import asyncio
import threading
import settings
import pygame
import time
import integrations.playout as playout
import config.shutdown_reason as SR

from integrations.logging_config import *
logger = setup_logger(__name__)


try:
    #Only avaiable on Raspberry
    import RPi.GPIO as GPIO # pylint: disable=import-error
except ImportError:
    pass


class pygameInput():

    def setup_headless_mode(self):
        """Setzt den Dummy-Video-Treiber für headless-Systeme."""
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    def __init__(self, loop, turn_callback, push_callback,windowmanager,nowplaying,config):
        print("Polling PyGame keys")

        self.setup_headless_mode()
        pygame.init()
        pygame.joystick.init()
        pygame.mixer.init(44100, -16,2,512)
        pygame.mixer.pause()
        pygame.mixer.quit()
        pygame.mouse.set_visible(False)

        self.windowmanager = windowmanager
        self.clock = pygame.time.Clock()
        self.nowplaying = nowplaying

        self.loop = loop
        self.turn_callback = turn_callback
        self.push_callback = push_callback
        self.config = config
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
            #if self.powerbtn != gpio26:
            logger.debug(f"gpicase Powerbutton: {gpio26}")

            if gpio26 == 0:
                if settings.shutdown_reason != SR.SR4 : settings.shutdown_reason = SR.SR2

                if self.powerpressed < 1:
                    self.powerpressed += 1
                    self.windowmanager.set_window("ende")
            else:
                self.powerpressed = 0
                self.windowmanager.set_window("idle")
        finally:
            logger.debug("gpicase power handling: ende")
            time.sleep(0.1)
            settings.callback_active = False



    async def _poll_pygame_keys(self):
        # for al the connected joysticks
        joysticks = []
        shutdown = False

        while self.loop.is_running() and not shutdown:
            #self.clock.tick(60)
            for event in pygame.event.get():
                logger.debug("pygame: %s " % (event))
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks.append(joy)
                elif event.type == pygame.QUIT:
                    shutdown = True
                elif event.type == pygame.JOYHATMOTION:
                    x,y = event.value
                    if (y == -1 and x == 0): # keypad down
                        logger.debug ("pygame: down")
                        self.turn_callback(0,'8')
                    elif (y == 1 and x == 0): #keypad up
                        logger.debug ("pygame: up")
                        self.turn_callback(0,'2')
                    elif (x == -1 and y == 0): # keypad left
                        logger.debug ("pygame: left")
                        self.turn_callback(0,'4')
                    elif (x == 1 and y == 0): #keypas right
                         logger.debug( "pygame: right")
                         self.turn_callback(0,'6')
                elif event.type == pygame.JOYBUTTONUP:
                    try:
                        pressed = int(event.button)
                        button_string = f"button_{pressed}"
                        button = self.config.__dict__[button_string]

                        if button == '*':
                            self.push_callback()
                        elif button != '':
                            self.turn_callback(0,button)
                    except Exception as error:
                        logger.debug (f"poll_loop: {error}")
                await asyncio.sleep(0.1)

    def quit(self):
        logger.info("Shutting Down Pygame")
        pygame.joystick.quit()
        pygame.display.quit()
        pygame.quit()