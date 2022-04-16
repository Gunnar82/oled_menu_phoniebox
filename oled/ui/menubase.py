""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class MenuBase(WindowBase):
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
    font = ImageFont.truetype(settings.FONT_TEXT, size=12)

    def __init__(self, windowmanager,title):
        super().__init__(windowmanager)
        self.counter = 0
        self.descr = []
        self.basetitle = title

    def render(self):
        with canvas(self.device) as draw:
            mwidth = MenuBase.font.getsize(self.descr[self.counter][0])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter][0], font=MenuBase.font, fill="white")

            #rectangle as selection marker
            if self.counter < 4: #4 icons in one row
                y_coord = 15
                x_coord = 7 + self.counter * 35
            elif self.counter >=4  and self.counter < 8:
                y_coord = 44
                x_coord = 6 + (self.counter - 4) * 35
            elif self.counter >=8 and self.counter  < 12: #3 icons in one row
                y_coord = 63 if settings.DISPLAY > 64 else 15
                x_coord = 7 + (self.counter - 8) * 35
            elif self.counter >= 12:
                y_coord = 92 if settings.DISPLAY > 64 else 44
                x_coord = 6 + (self.counter - 12) * 35

            #draw.rectangle((x_coord, y_coord, x_coord+25, y_coord+25), outline=settings.COLOR_YELLOW, fill=0)

            #icons as menu buttons
            i = 0

            if self.counter <= 16:
                while (i <= 16) and (i < len(self.descr)):
                    if (i < 4):
                        x_coord = 11 + i * 33
                        y_coord = 20
                    elif (i < 8):
                        x_coord = 11 + (i-4) * 33
                        y_coord = 45
                    elif (i < 12):
                        x_coord = 11 + (i-8) * 33
                        y_coord = 70
                    elif (i < 16):
                        x_coord = 11 + (i-12) * 33
                        y_coord = 95


                    if (self.counter == i):
                        fill = settings.COLOR_SELECTED
                        outline = 255
                    else:
                        fill = "white"
                        outline = "black"

                    draw.text((x_coord, y_coord), text=self.descr[i][1], font=MenuBase.faicons, outline=outline, fill=fill)

                    i += 1

    def activate(self):
        self.counter = 0

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                direction = -4
            elif key == 'down' or key == '8':
                direction = 4
            elif key == 'left' or key == '4':
                direction = -1
            elif key == 'right' or key == '6':
                direction = 1
            elif key == '#':
               self.windowmanager.set_window("idle")


        if (self.counter + direction < len(self.descr) and self.counter + direction >= 0):
            self.counter += direction


