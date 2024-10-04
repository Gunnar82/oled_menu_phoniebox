""" Display hardware or emulator """
import settings

def get_display():
    settings.DISPLAY_HANDLE_CONTRAST = True
    from luma.core.interface.serial import spi,i2c

    from luma.oled.device import ssd1351

    serial = spi(port=0, device=0, gpio_SCLK=10, gpio_DC=22, gpio_RST=27, gpio_CS=16, bus_speed_hz=16000000)
    device = ssd1351(serial_interface=serial,rotate=3, bgr=True)


    device.contrast(settings.CONTRAST_FULL)
    #device.cleanup = do_nothing

    print("Using real display hardware")
    return device

def do_nothing(obj):
    pass



def set_fonts():
    import fonts.fonts_128x128