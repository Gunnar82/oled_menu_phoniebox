""" Display hardware or emulator """
import settings

def get_display():
    settings.DISPLAY_HANDLE_CONTRAST = True

    from luma.core.interface.serial import spi

    from luma.oled.device import sh1106

    serial = spi(port=0,device=0, gpio_SCLK=11,gpio_SDA=10, gpio_DC = 24, gpio_CS = 8, gpio_RST=25, bus_speed_hz=8000000)
    device = sh1106(serial_interface=serial,rotate=2,bgf=True,active_low=False)


    device.contrast(settings.CONTRAST_FULL)
    device.cleanup = do_nothing

    print("Using real display hardware")
    return device

def do_nothing(obj):
    pass



def set_fonts():
    import fonts.fonts_128x64