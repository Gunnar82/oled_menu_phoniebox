""" Display hardware or emulator """
import settings

def get_display():

    from luma.oled.device import ssd1351
    from luma.core.interface.serial import spi,i2c


    if settings.DISPLAY_TYPE == "i2c":
        device = sh1106(i2c(port=1, address=0x3C))
    else:
        serial = spi(port=0, device=0, gpio_SCLK=10, gpio_DC=22, gpio_RST=27, gpio_CS=16, bus_speed_hz=16000000)
        device = ssd1351(serial_interface=serial,rotate=1, bgr=True)

    device.contrast(settings.CONTRAST_FULL)
    device.cleanup = do_nothing

    print("Using real display hardware")
    return device

def do_nothing(obj):
    pass

