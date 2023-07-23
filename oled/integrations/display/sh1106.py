""" Display hardware or emulator """
import settings

def get_display():
    settings.CONTRAST_HANDLE = True

    from luma.core.interface.serial import spi,i2c

    from luma.oled.device import ssd1351

    device = sh1106(i2c(port=1, address=0x3C))


    device.contrast(settings.CONTRAST_FULL)
    device.cleanup = do_nothing

    print("Using real display hardware")
    return device

def do_nothing(obj):
    pass



def set_fonts():
    settings.CONTRAST_HANDLE = True
    settings.FONT_SIZE_XXL = 20
    settings.FONT_SIZE_XL = 18
    settings.FONT_SIZE_L = 16
    settings.FONT_SIZE_NORMAL = 12
    settings.FONT_SIZE_SMALL = 10

    settings.FONT_HEIGHT_XXL = 20
    settings.FONT_HEIGHT_XL = 18
    settings.FONT_HEIGHT_NORMAL = 14
    settings.FONT_HEIGHT_SMALL = 12

    settings.DISPLAY_WIDTH = 128
    settings.DISPLAY_HEIGHT = 128 # or 64
    settings.DISPLAY_RGB = False
