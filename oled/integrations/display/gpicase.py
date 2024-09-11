""" Display hardware or emulator """
import settings

#import framebuffer device
from luma.core.device import linux_framebuffer


def get_display():
    settings.CONTRAST_HANDLE = False

    print("gpicase")

    device = linux_framebuffer("/dev/fb0",bgr=True)
    device.capabilities(width=320,height=240,rotate=0,mode='RGB')
    return device

def do_nothing(obj):
    pass


def set_fonts():
    import fonts.fonts_320x240