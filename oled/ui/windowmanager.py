"""Manages the currently shown activewindow on screen and passes callbacks for the rotary encoder"""
import settings
from datetime import datetime

import asyncio

import config.symbols as symbols
import integrations.functions as fn

from integrations.logging import *
from integrations.rfidwatcher import RfidWatcher
from integrations.latestplayed import LatestPlayed

class WindowManager():
    def __init__(self, loop, device):
        self._looptime = 2
        self._RENDERTIME = 0.25

        self.looptime = self._looptime
        self.device = device
        self.windows = {}
        self.activewindow = []
        self.loop = loop
        settings.lastinput = datetime.now()
        self._lastcontrast = settings.CONTRAST_FULL
        self.loop.create_task(self._render())
        self.lastrfidate = datetime(2000,1,1)

        self.rfidwatcher = RfidWatcher()
        self.rfidwatcher.start()

        self.lastplayed = LatestPlayed()
        self.lastplayed.start()

        self.rendered_busy = False
        log(lINFO,"Rendering task created")

    def add_window(self, windowid, window):
        self.windows[windowid] = window
        log(lINFO,f"Added {windowid} window")

    def set_window(self, windowid):
        if windowid in self.windows:
            try:
                self.activewindow.deactivate()
            except (NotImplementedError, AttributeError):
                pass
            self.activewindow = self.windows[windowid]
            log(lINFO,f"Activated {windowid}")
        else:
            log(lINFO,f"Window {windowid} not found!")

        try:
            self.rendertime = self.activewindow._rendertime
            self.activewindow.busy = False
            self.activewindow.activate()
            self.activewindow.windowtitle = windowid
        except (NotImplementedError, AttributeError):
            pass


    def show_window(self):
        settings.lastinput = datetime.now()
        settings.screenpower = True
        self.device.show()


    def clear_window(self):
        log(lDEBUG,"Show blank screen")
        settings.screenpower = False
        self.device.clear()
        #Low-Power sleep mode
        self.device.hide()

    async def _render(self):

        while self.loop.is_running():

            seconds_since_last_input = (datetime.now() - settings.lastinput).total_seconds()

            if (seconds_since_last_input >= settings.MENU_TIMEOUT) and self.activewindow.timeout:
                self.set_window(self.activewindow.timeoutwindow)

            if self.activewindow.contrasthandle:
                log(lDEBUG2,"contrasthandle")
                if (seconds_since_last_input >= settings.DARK_TIMEOUT):
                    self.rendertime = settings.DARK_RENDERTIME
                    self.looptime = int (settings.DARK_RENDERTIME // 2)

                    contrast = settings.CONTRAST_BLACK

                elif  (seconds_since_last_input >= settings.CONTRAST_TIMEOUT):
                    self.looptime = settings.CONTRAST_RENDERTIME
                    self.rendertime = settings.CONTRAST_RENDERTIME
                    log(lDEBUG2,"contrast_timeout")
                    if settings.DISABLE_DISPLAY:
                        if settings.screenpower:
                            log(lDEBUG,"disable Display")
                            self.clear_window()
                    else:
                        contrast = settings.CONTRAST_DARK

                else:
                    contrast = settings.CONTRAST_FULL
                    self.rendertime = self.activewindow._rendertime
                    self.looptime = self._looptime

            else:
                self.rendertime = self.activewindow._rendertime

            if self._lastcontrast != contrast:
                self._lastcontrast = contrast

                self.device.contrast(contrast)

            if self.activewindow != []:
                count = 0
                while (contrast == settings.CONTRAST_BLACK) and (count < 4 * settings.DARK_RENDERTIME) and (seconds_since_last_input >= settings.CONTRAST_TIMEOUT):
                    count += 1
                    await asyncio.sleep(0.25)

                if self.rfidwatcher.get_state():
                    self.lastrfidate = datetime.now()
                    self.show_window()

                if self.activewindow.windowtitle in ['start']:
                    self.show_window()

                if settings.screenpower:
                    try:
                        log(lDEBUG3,"busy State of %s:  %s" %(self.activewindow.windowtitle,self.activewindow.busy))
                        if (datetime.now() - self.lastrfidate).total_seconds() < 3:
                            log(lDEBUG,"render rfid symbol")
                            self.activewindow.busysymbol = symbols.SYMBOL_CARD_READ
                            #self.rendertime = self.activewindow.busyrendertime
                            self.activewindow.renderbusy()
                            self.activewindow.busysymbol = symbols.SYMBOL_SANDCLOCK

                        elif ((datetime.now() - self.activewindow.start_busyrendertime).total_seconds() < self.activewindow.busyrendertime and self.activewindow.busy) or (settings.callback_active and self.activewindow.changerender):

                                self.activewindow.renderbusy()
                                log(lDEBUG2,"rendering busy of window %s, busyrendertime: %d" %(self.activewindow.windowtitle,self.rendertime))
                                await asyncio.sleep(self._RENDERTIME)
                        else:
                            log(lDEBUG3,"general rendering")
                            self.activewindow.render()
                    except Exception as error:
                        log(lERROR,error)

            iTimerCounter = 0 

            while (iTimerCounter < self.rendertime / self._RENDERTIME  and settings.screenpower):
                log(lDEBUG2,"renderloop: %d, %d "%(iTimerCounter+1, self.rendertime / self._RENDERTIME))
                iTimerCounter += 1
                await asyncio.sleep(self._RENDERTIME)
                log(lDEBUG3, "self.busytext1: %s" %(self.activewindow.busytext1))

                if (not settings.callback_active and self.rendered_busy):
                    log(lDEBUG3,"render resetting %s.busy to False" %(self.activewindow.windowtitle))
                    self.activewindow.busy = False

            await asyncio.sleep(self._RENDERTIME)


    def push_callback(self,lp=False):
        settings.lastinput = datetime.now()
        settings.staywake = False
        if settings.screenpower:
            settings.callback_active = True
            log(lDEBUG2,"push_callback: started")

            try:
                self.device.contrast(settings.CONTRAST_FULL)
                self.activewindow.push_callback(lp=lp)
            except (NotImplementedError, AttributeError):
                log(lERROR,"window_manager: push_callback error")
            finally:
                settings.callback_active = False
                log(lDEBUG2,"push_callback: ended")

        else: 
            settings.screenpower = True
            self.device.show()
            if self.activewindow.windowtitle not in ["ende", "lock"]:
                self.set_window("idle")

    def turn_callback(self, direction, key=None):
        settings.lastinput = datetime.now()
        settings.staywake = False
        if key == '0' and self.activewindow.windowtitle not in ["idle"]:
            try:
                fn.restart_oled()
            except Exception as error:
                log(lERROR,"turn_callback: %s" % (str(error)))

        elif settings.screenpower:
            settings.callback_active = True
            log(lDEBUG2,"turn_callback: started")

            try:
                self.device.contrast(settings.CONTRAST_FULL)
                if key == '#':
                    log(lINFO,"activate window_on_back: %s" % (self.activewindow.window_on_back))
                    if self.activewindow.window_on_back not in ["","none","n/a"]: self.set_window(self.activewindow.window_on_back)
                else:
                    self.activewindow.turn_callback(direction,key=key)
            except (NotImplementedError, AttributeError):
                log(lERROR,"window_manager: turn_callback error")
            finally:
                settings.callback_active = False
                log(lDEBUG2,"turn_callback: ended")

        else:
            settings.screenpower = True
            self.device.show()
            if self.activewindow.windowtitle not in ["ende", "lock"]:
                 self.set_window("idle")


    def __del__(self):
        self.rfidwatcher.stop()

