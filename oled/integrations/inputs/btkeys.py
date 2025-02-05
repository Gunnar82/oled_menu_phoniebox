import evdev
import time

from integrations.logging_config import *
from integrations.functions import run_command

logger = setup_logger(__name__,lvlDEBUG)


class BluetoothKeys():
    # Button key codes
    bt_keycode_play = 200
    bt_keycode_pause = 201
    bt_keycode_next = 163
    bt_keycode_prev = 165


    def __init__(self,loop,turn_callback, push_callback, mopidy, bluetooth):
        try:
            logger.debug ("btkeys init")
            self.loop = loop
            self.mopidy = mopidy
            self.bluetooth = bluetooth
            self.turn_callback = turn_callback
            self.push_callback = push_callback
            self.evdevice = None
            self.btkeystask = self.loop.run_in_executor(None,self.handle_bluetooth_keys)
        except Exception as error:
            logger.debug(error)


    def is_avrcp_connected(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            logger.debug(f"Gefundenes Gerät: {device.path} - {device.name}")
            # Überprüfen, ob der Gerätename "Bluetooth", "Media", "AVRCP" oder "JQ-BT" e                                                                                                             nthält
            if "AVRCP" in device.name:
                self.evdevice = device
                return True
        logger.debug ("Kein AVRCP gefunden")
        return False

    def handle_bluetooth_keys(self):
        logger.debug("handle_bluetooth_keys started")

        logger.debug("handle_bluetooth_keys loop")
        try:
            while True:
                if self.is_avrcp_connected():
                    logger.debug ("found avrcp")

                    for event in self.evdevice.read_loop():
                        if event.type == evdev.ecodes.EV_KEY:
                            logger.debug(event)
                            if event.value == 1:  # Taste gedrückt
                                logger.debug(f"Event: {event}")  # Debugging: Ereignisdetails anzeigen
                                if event.code == self.bt_keycode_play:
                                    logger.debug("play")  # Debugging: Ereignisdetails anzeigen
                                    self.mopidy.playpause()
                                elif event.code == self.bt_keycode_pause:
                                    logger.debug("pause")  # Debugging: Ereignisdetails anzeigen
                                    self.mopidy.playpause()
                                elif event.code == self.bt_keycode_next:
                                    logger.debug("right")  # Debugging: Ereignisdetails anzeigen
                                    self.turn_callback(0,"right")
                                elif event.code == self.bt_keycode_prev:
                                    logger.debug("left")  # Debugging: Ereignisdetails anzeigen
                                    self.turn_callback(0,"left")
                                #elif key_event.keycode == self.bt_keycode_stop:
                                #    print("Stopp gedrückt")
                                else:
                                    logger.debug(f"Kein Handlin implementiert: {key_event.keycode}")
                else:
                    logger.debug ("no AVRCP")
                time.sleep(1)
        except SIGINTException as e:
            print("gefunden:::: {e}")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
            print (e)
