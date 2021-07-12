""" View class to inherit other views from """

class WindowBase():
    def __init__(self, windowmanager):
        self.windowmanager = windowmanager
        self.device = self.windowmanager.device
        self.loop = self.windowmanager.loop
        self.timeout = True

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
