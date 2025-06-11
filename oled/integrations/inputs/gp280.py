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

        self.__keys = []

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
                elif event.type == pygame.JOYAXISMOTION:
                    joystick = joysticks[event.joy]
                    axis_value = joystick.get_axis(event.axis)
                    if event.axis == 1 and axis_value > 0.5:
                        x = 0
                        y = -1
                    elif event.axis == 1 and axis_value < -0.5:
                        x = 0
                        y = 1
                    # Wenn Y-Achse (vertikal) bewegt wird
                    elif event.axis == 0 and axis_value > 0.5:
                        x = 1
                        y = 0
                    elif event.axis == 0 and axis_value < -0.5:
                        x = -1
                        y = 0
                    else:
                        x = 0
                        y = 0
                    if (x, y) in self.config.direction_map:
                        direction = self.config.direction_map[(x, y)]
                        logger.debug(f"pygame JOYHAT: direction {direction}")
                        self.loop.run_in_executor(None, self.handle_turn, 0, direction)

                elif event.type == pygame.JOYBUTTONDOWN:
                    try:
                        pressed = int(event.button)
                        button_string = f"button_{pressed}"
                        button = self.config.__dict__[button_string]
                        if button not in self.__keys: self.__keys.append(button)
                    except Exception as error:
                        logger.debug (f"keypdown {error}")


                elif event.type == pygame.JOYBUTTONUP:

                    try:
                        pressed = int(event.button)
                        logger.debug (f"up keycode: {pressed}")
                        button_string = f"button_{pressed}"
                        button = self.config.__dict__[button_string]

                        logger.debug (f"handle button up {button}")

                        if button == '*':
                            logger.debug (f"push callback: button = {button}")
                            self.push_callback()
                        elif button != '':
                            if "F" in self.__keys and button == '9': button = 'S'

                            logger.debug (f"turn callback: button = {button}")
                            await self.loop.run_in_executor(None,self.handle_turn,0,button)
                    except Exception as error:
                        logger.debug (f"poll_loop: {error}")
                    try:

                        logger.debug (f"downpressed keys: {self.__keys}")
                        logger.debug (f" remove {button}")
                        self.__keys.remove(button)
                    except ValueError:
                        logger.debug(f"{button} war nict gedrückt")
                    except Exception as error:
                        logger.debug (f"{error}")

            await asyncio.sleep(0.1)

    def handle_turn(self,rotation,button):
        logger.debug (f"start handle_turn for {rotation} and {button}")
        self.turn_callback(rotation,button)


    def quit(self):
        logger.info("Shutting Down Pygame")
        pygame.joystick.quit()
        pygame.display.quit()
        pygame.quit()