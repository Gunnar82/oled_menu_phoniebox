""" View class to inherit other views from """

class WindowBase():
    def __init__(self, windowmanager):
        self.windowmanager = windowmanager
        self.counter = 0
        self.page = 0
        self.device = self.windowmanager.device
        self.loop = self.windowmanager.loop
        self.timeout = True
        self.contrasthandle = True
        self.timeoutwindow="idle"

    def activate(self):
        raise NotImplementedError()

    def deactivate(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, ud=False):
        raise NotImplementedError()
