"""Manages the currently shown activewindow on screen and passes callbacks for the rotary encoder"""
import asyncio
from datetime import datetime
import settings

from integrations.rfidwatcher import RfidWatcher

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


        print("Rendering task created")

    def add_window(self, windowid, window):
        self.windows[windowid] = window
        print(f"Added {windowid} window")

    def set_window(self, windowid):
        if windowid in self.windows:
            try:
                self.activewindow.deactivate()
            except (NotImplementedError, AttributeError):
                pass
            self.activewindow = self.windows[windowid]
            try:
                self.rendertime = self.activewindow._rendertime
                self.activewindow.busy = False
                self.activewindow.activate()
            except (NotImplementedError, AttributeError):
                pass
            print(f"Activated {windowid}")
        else:
            print(f"Window {windowid} not found!")

    def show_window(self):
        settings.screenpower = True
        self.device.show()


    def clear_window(self):
        print("Show blank screen")
        settings.screenpower = False
        self.device.clear()
        #Low-Power sleep mode
        self.device.hide()

    async def _render(self):
        while self.loop.is_running():
            if ((datetime.now() - settings.lastinput).total_seconds() >= settings.MENU_TIMEOUT) and self.activewindow.timeout:
                self.set_window(self.activewindow.timeoutwindow)

            if self.activewindow.contrasthandle:
                if (datetime.now() - settings.lastinput).total_seconds() >= settings.DARK_TIMEOUT:
                    self.rendertime = settings.DARK_RENDERTIME
                    self.looptime = int (settings.DARK_RENDERTIME // 2)

                    contrast = settings.CONTRAST_BLACK

                elif  (datetime.now() - settings.lastinput).total_seconds() >= settings.CONTRAST_TIMEOUT:
                    self.looptime = settings.CONTRAST_RENDERTIME
                    self.rendertime = settings.CONTRAST_RENDERTIME

                    if settings.DISABLE_DISPLAY:
                        if settings.screenpower:
                            self.clear_window()
                    else:
                        contrast = settings.CONTRAST_DARK

                else:
                    contrast = settings.CONTRAST_FULL
                    self.rendertime = self.activewindow._rendertime
                    self.looptime = self._looptime


            if self._lastcontrast != contrast:
                self._lastcontrast = contrast
                self.device.contrast(contrast)

            if self.activewindow != []:
                count = 0
                while (contrast == settings.CONTRAST_BLACK) and (count < 4 * settings.DARK_RENDERTIME) and ((datetime.now() - settings.lastinput).total_seconds() >= settings.CONTRAST_TIMEOUT):
                    count += 1
                    await asyncio.sleep(0.25)

                if self.rfidwatcher.get_state():
                    self.show_window()
                    self.lastrfidate = datetime.now()

                if settings.screenpower:
                    try:
                        if (datetime.now() - self.lastrfidate).total_seconds() < 3:
                            self.activewindow.busysymbol = settings.SYMBOL_CARD_READ
                            self.activewindow.renderbusy()
                            self.activewindow.busysymbol = settings.SYMBOL_SANDCLOCK
                        elif self.activewindow.busy:
                            self.rendertime = self.activewindow.busyrendertime
                            self.activewindow.renderbusy()
                        else:
                            self.activewindow.busysymbol = settings.SYMBOL_SANDCLOCK
                            self.activewindow.render()
                    except (NotImplementedError, AttributeError):
                        pass
            print (self.rendertime)
            iTimerCounter = 0 
            while (((datetime.now() - settings.lastinput).total_seconds() < self.activewindow.busyrendertime) and (iTimerCounter < self.rendertime / self._RENDERTIME)):
                print ("loop")
                iTimerCounter += 1
                await asyncio.sleep(self._RENDERTIME)

            await asyncio.sleep(self._RENDERTIME)

    def push_callback(self,lp=False):
        settings.lastinput = datetime.now()
        settings.staywake = False
        if settings.screenpower:
            self.activewindow.busy = True

            try:
                self.device.contrast(settings.CONTRAST_FULL)
                self.activewindow.push_callback(lp=lp)
            except (NotImplementedError, AttributeError):
                pass
            finally:
                self.activewindow.busy = False
                self.activewindow.busysymbol = settings.SYMBOL_SANDCLOCK

        else:
            settings.screenpower = True
            self.device.show()
            self.set_window("idle")

    def turn_callback(self, direction, key=None):
        try:
            self.activewindow.busy = True
            settings.screenpower = True
            self.device.show()
            settings.lastinput = datetime.now()
            self.device.contrast(settings.CONTRAST_FULL)
            if key == '#':
                print ("activate window_on_back: %s" % (self.activewindow.window_on_back))
                self.set_window(self.activewindow.window_on_back)
            else:
                self.activewindow.turn_callback(direction,key=key)
        except (NotImplementedError, AttributeError):
            pass
        finally:
            self.activewindow.busy = False

    def __del__(self):
        self.rfidwatcher.stop()

