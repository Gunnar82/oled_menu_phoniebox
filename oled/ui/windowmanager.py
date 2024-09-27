"""Manages the currently shown activewindow on screen and passes callbacks for the rotary encoder"""
import settings
import time

import asyncio
import config.symbols as symbols
import integrations.functions as fn


from integrations.rfidwatcher import RfidWatcher
from integrations.latestplayed import LatestPlayed

from integrations.logging_config import *

import config.user_settings as csettings

logger = setup_logger(__name__)


class WindowManager():
    def __init__(self, loop, device):
        self._looptime = 2
        self._RENDERTIME = 0.25

        self.looptime = self._looptime
        self.device = device
        self.windows = {}
        self.activewindow = []
        self.loop = loop
        fn.set_lastinput()
        self._lastcontrast = csettings.CONTRAST_FULL
        self.loop.create_task(self._render())
        self.lastrfidate = 0

        self.rfidwatcher = RfidWatcher()
        self.rfidwatcher.start()

        self.lastplayed = LatestPlayed()
        self.lastplayed.start()

        self.rendered_busy = False
        logger.info("Rendering task created")

    def add_window(self, windowid, window):
        self.windows[windowid] = window
        logger.info(f"Added {windowid} window")

    def set_window(self, windowid):
        if windowid in self.windows:
            try:
                self.activewindow.set_window_busy(False)
                self.activewindow.deactivate()
            except (NotImplementedError, AttributeError):
                pass
            self.activewindow = self.windows[windowid]
            logger.info(f"Activated {windowid}")
        else:
            logger.info(f"Window {windowid} not found!")

        try:
            self.rendertime = self.activewindow._rendertime
            self.activewindow.busy = False
            self.activewindow.activate()
            self.activewindow.windowtitle = windowid
        except (NotImplementedError, AttributeError):
            pass


    def show_window(self):
        fn.set_lastinput()
        settings.screenpower = True
        self.device.show()


    def clear_window(self):
        logger.debug("clear_window: Show blank screen")
        settings.screenpower = False
        self.device.clear()
        #Low-Power sleep mode
        self.device.hide()

    async def _render(self):

        while self.loop.is_running():
            #letzte Eingabezeit abfragen
            seconds_since_last_input = time.monotonic() - settings.lastinput

            #wenn in aktivem Fenster aktiviert, setze timeoutwindow
            if (seconds_since_last_input >= csettings.MENU_TIMEOUT) and self.activewindow.timeout:
                logger.info(f"_render: MENU_TIMEOUT: setze auf: {self.activewindow.timeoutwindow}")
                self.set_window(self.activewindow.timeoutwindow)

            #wenn in aktivem Fenster aktiviert, setze Display-Helligkeit
            if self.activewindow.contrasthandle:
                logger.debug(f"_render: {self.activewindow.contrasthandle}")
                #Helligkeit Stufe 2
                if (seconds_since_last_input >= csettings.DARK_TIMEOUT) and settings.DISPLAY_HANDLE_CONTRAST:
                    self.rendertime = csettings.DARK_RENDERTIME
                    self.looptime = int (csettings.DARK_RENDERTIME // 2)

                    contrast = csettings.CONTRAST_BLACK

                elif  (seconds_since_last_input >= csettings.CONTRAST_TIMEOUT):
                    # Helligkeit Stufe 1
                    self.looptime = csettings.CONTRAST_RENDERTIME
                    self.rendertime = csettings.CONTRAST_RENDERTIME
                    logger.debug("contrast_timeout")
                    if csettings.DISABLE_DISPLAY:
                        #Display ausschalten, wenn unterstützt
                        if settings.screenpower:
                            logger.debug("disable Display")
                            self.clear_window()
                    elif settings.DISPLAY_HANDLE_CONTRAST:
                        #wenn nicht, Helligkeit auf minimum
                        contrast = csettings.CONTRAST_DARK

                else:
                    #Eingabe erfolgt, normales render-Verhalten
                    contrast = csettings.CONTRAST_FULL
                    self.rendertime = self.activewindow._rendertime
                    self.looptime = self._looptime
            else:
                #wenn keine Kontrast-Anpassung unterstützt wird
                contrast = csettings.CONTRAST_FULL
                logger.debug(f"_render: contrasthandle: {self.activewindow.contrasthandle}")

                self.rendertime = self.activewindow._rendertime

            if self._lastcontrast != contrast:
                #wenn sich der Kontrast geändert hat, setze
                self._lastcontrast = contrast

                self.device.contrast(contrast)

            if self.activewindow != []:
                #render abarbeiten
                count = 0
                while (contrast == csettings.CONTRAST_BLACK) and (count < 4 * csettings.DARK_RENDERTIME) and (seconds_since_last_input >= csettings.CONTRAST_TIMEOUT):
                    # Render bei Display-Abdunkelung ist verlangsamt
                    # Eingabe prüfen. Bei Eingabe fortsetzen
                    if seconds_since_last_input <= csettings.DARK_TIMEOUT: break
                    count += 1
                    await asyncio.sleep(0.25)

                if self.rfidwatcher.get_state():
                    self.lastrfidate = time.monotonic()
                    self.show_window()


                if settings.screenpower:
                    try:
                        logger.debug("busy State of %s:  %s" %(self.activewindow.windowtitle,self.activewindow.busy))
                        if (time.monotonic() - self.lastrfidate) < 3:
                            #RFID Karte wurde gelesen
                            logger.debug("render: rfid symbol")
                            self.activewindow.busysymbol = symbols.SYMBOL_CARD_READ
                            #self.rendertime = self.activewindow.busyrendertime
                            self.activewindow.renderbusy()
                            self.activewindow.busysymbol = symbols.SYMBOL_SANDCLOCK

                        elif ((time.monotonic() - self.activewindow.start_busyrendertime) < self.activewindow.busyrendertime and self.activewindow.busy) or (settings.callback_active and self.activewindow.changerender and not self.activewindow.new_busyrender):
                            #window busy
                            logger.debug(f"render: start renderbusy - time: {self.activewindow.busyrendertime}s: {self.activewindow.windowtitle}")

                            self.activewindow.renderbusy()
                            logger.debug(f"render: end renderbusy: {self.activewindow.windowtitle}")
                            await asyncio.sleep(self._RENDERTIME)
                        elif (self.activewindow.is_busy):
                            logger.debug(f"render: start new_renderbusy: {self.activewindow.windowtitle}")

                            self.activewindow.new_renderbusy()
                            logger.debug(f"render: end new_renderbusy: {self.activewindow.windowtitle}")


                        else:
                            logger.debug("render: start render")
                            self.activewindow.render()
                    except Exception as error:
                        logger.error(f"render: exception: {error}")

            logger.debug(f"render: screenpower: {settings.screenpower}, _RENDERTIME: {self._RENDERTIME}, rendertime: {self.rendertime} ")

            #warte Rendertime ab
            iTimerCounter = 0 

            while (iTimerCounter < self.rendertime / self._RENDERTIME  and settings.screenpower):
                iTimerCounter += 1
                await asyncio.sleep(self._RENDERTIME)
                #logger.debug("self.busytext1: %s" %(self.activewindow.busytext1))
                if not settings.screenpower and secconds_since_last_input <= csettings.DARK_TIMEOUT: break
                if (not settings.callback_active and self.rendered_busy):
                    #logger.debug("render resetting %s.busy to False" %(self.activewindow.windowtitle))
                    self.activewindow.busy = False

            await asyncio.sleep(self._RENDERTIME)


    def init_callback_or_idle(self):
        fn.set_lastinput()
        settings.staywake = False
        self.device.contrast(csettings.CONTRAST_FULL)

        if not settings.screenpower:
            settings.screenpower = True
            self.device.show()

            logger.debug("init_callback: no screenpower: show idle, if handle_key_back")

            if self.activewindow.handle_key_back:
                self.set_window("idle")
        return settings.screenpower


    def push_callback(self,lp=False):
        if not self.init_callback_or_idle(): return

        settings.callback_active = True
        logger.debug("push_callback: started")

        try:
            self.activewindow.push_callback(lp=lp)
        except (NotImplementedError, AttributeError):
            logger.error("window_manager: push_callback error")
        finally:
            settings.callback_active = False
            logger.debug("push_callback: ended")


    def turn_callback(self, direction, key=None):
        if not self.init_callback_or_idle(): return

        if key == '0' and self.activewindow.windowtitle not in ["idle"]:
            try:
                fn.restart_oled()
            except Exception as error:
                logger.error("turn_callback: %s" % (str(error)))
        else:
            settings.callback_active = True
            logger.debug("turn_callback: started")

            try:
                if key == '#' and self.activewindow.handle_key_back:
                    logger.info("activate window_on_back: %s" % (self.activewindow.window_on_back))
                    if self.activewindow.window_on_back not in ["","none","n/a"]: self.set_window(self.activewindow.window_on_back)
                else:
                    self.activewindow.turn_callback(direction,key=key)
            except Exception as error:
                logger.error(f"window_manager: turn_callback: {error}")
            finally:
                settings.callback_active = False
                logger.debug("turn_callback: ended")



    def __del__(self):
        self.rfidwatcher.stop()

