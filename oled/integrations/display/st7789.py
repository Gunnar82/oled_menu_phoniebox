""" Display hardware or emulator """
import settings

def get_display():
    settings.DISPLAY_HANDLE_CONTRAST = True

    from luma.core.interface.serial import spi
    from luma.lcd.device import st7789
#11 10port=1, device=0,13, backlight_enabled=True
    serial = spi(port=0,device=1, gpio_SCLK=11,gpio_SDA=10, gpio_DC = 9, gpio_CS = 1, gpio_RST=None, bus_speed_hz=8000000)
    device = st7789(serial_interface=serial,rotate=1,bgf=True, gpio_LIGHT=13,active_low=False)


    device.contrast(settings.CONTRAST_FULL)
    device.cleanup = do_nothing

    print("Using real display hardware")
    return device

def do_nothing(obj):
    pass


def set_fonts():
    import fonts.fonts_240x240
