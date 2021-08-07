"""Manages the currently shown activewindow on screen and passes callbacks for the rotary encoder"""
import asyncio
from datetime import datetime
import settings

class WindowManager():
    def __init__(self, loop, device):
        self.device = device
        self.windows = {}
        self.activewindow = []
        self.loop = loop
        settings.lastinput = datetime.now()
        self._lastcontrast = settings.CONTRAST_FULL
        self.loop.create_task(self._render())

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
                self.activewindow.activate()
            except (NotImplementedError, AttributeError):
                pass
            print(f"Activated {windowid}")
        else:
            print(f"Window {windowid} not found!")

        

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
            if ((datetime.now() - settings.lastinput).total_seconds() >= settings.CONTRAST_TIMEOUT and self.activewindow.contrasthandle):
                contrast = settings.CONTRAST_DARK
            else:
                contrast = settings.CONTRAST_FULL

            if ((settings.job_t >=0 and settings.job_t <= 5) or (settings.job_i >= 0 and settings.job_i <=5)):
                settings.screenpower = True
            else:
                if ((datetime.now() - settings.lastinput).total_seconds() >= settings.DARK_TIMEOUT and self.activewindow.contrasthandle):
                    contrast = settings.CONTRAST_BLACK
                    settings.screenpower = False

            if self._lastcontrast != contrast:
                self._lastcontrast = contrast
                self.device.contrast(contrast)

            if self.activewindow != [] and settings.screenpower:
                try:
                    self.activewindow.render()
                except (NotImplementedError, AttributeError):
                    pass



            await asyncio.sleep(0.25)

    def push_callback(self,lp=False):
        settings.lastinput = datetime.now()
        settings.staywake = False
        if settings.screenpower:
            try:
                self.activewindow.push_callback(lp=lp)
            except (NotImplementedError, AttributeError):
                pass
        else:
            settings.screenpower = True
            self.device.show()
            self.set_window("idle")

    def turn_callback(self, direction, key=None):
        try:
            settings.screenpower = True
            settings.lastinput = datetime.now()
            self.activewindow.turn_callback(direction,key=key)
        except (NotImplementedError, AttributeError):
            pass
