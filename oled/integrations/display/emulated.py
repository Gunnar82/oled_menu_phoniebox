""" Display hardware or emulator """
import settings

import luma.emulator.device

class EmuPygame(luma.emulator.device.pygame):
    def display(self, image):
            super(EmuPygame, self).display(image)
            super(EmuPygame, self).display(image)



def get_display():
    settings.DISPLAY_HANDLE_CONTRAST = False

    print("Using PyGame output")
    #Mode=1: Monochrome
    return EmuPygame(transform='identity', scale=1, mode='RGB',height=240,width=320)

def do_nothing(obj):
    pass


def set_fonts():
    import fonts.fonts_320x240