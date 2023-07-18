""" Display hardware or emulator """
import settings

def get_display():

    from luma.core.interface.serial import spi,i2c


    if settings.DISPLAY_DRIVER == "ST7789":

        from luma.lcd.device import st7789
#11 10port=1, device=0,13, backlight_enabled=True
        serial = spi(port=0,device=1, gpio_SCLK=11,gpio_SDA=10, gpio_DC = 9, gpio_CS = 1, gpio_RST=None, bus_speed_hz=8000000)
        device = st7789(serial_interface=serial,rotate=3,bgf=True, gpio_LIGHT=13,active_low=False)

    else:

        from luma.oled.device import ssd1351

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

