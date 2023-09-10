""" Display hardware or emulator """
import settings

import luma.emulator.device

class EmuPygame(luma.emulator.device.pygame):
    def display(self, image):
            super(EmuPygame, self).display(image)
            super(EmuPygame, self).display(image)



def get_display():
    settings.CONTRAST_HANDLE = False

    print("Using PyGame output")
    #Mode=1: Monochrome
    return EmuPygame(transform='identity', scale=1, mode='RGB',height=240,width=320)

def do_nothing(obj):
    pass


def set_fonts():
    print("set fonts")

    settings.FONT_SIZE_XXXL = 60
    settings.FONT_SIZE_XXL = 50
    settings.FONT_SIZE_XL = 30
    settings.FONT_SIZE_L = 20
    settings.FONT_SIZE_NORMAL = 24
    settings.FONT_SIZE_SMALL = 18

    settings.FONT_HEIGHT_XXL = 40
    settings.FONT_HEIGHT_XL = 30
    settings.FONT_HEIGHT_NORMAL = 24
    settings.FONT_HEIGHT_SMALL = 20

    settings.DISPLAY_WIDTH = 320
    settings.DISPLAY_HEIGHT = 240 # or 64
    settings.DISPLAY_RGB = True
