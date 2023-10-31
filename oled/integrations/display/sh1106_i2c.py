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
    import fonts.fonts_128x64