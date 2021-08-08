""" Display hardware or emulator """
import settings

def get_display():

    from luma.oled.device import sh1106
    from luma.core.interface.serial import i2c

    device = sh1106(i2c(port=1, address=0x3C))
    device.contrast(settings.CONTRAST_FULL)
    device.cleanup = do_nothing

    print("Using real display hardware")
    return device

def do_nothing(obj):
    pass

