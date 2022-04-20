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
        self.lines_per_page = 4 if settings.DISPLAY_HEIGHT == 128 else 2
        self.symbols_per_line = 4

    def render(self):
        with canvas(self.device) as draw:
            mwidth = MenuBase.font.getsize(self.descr[self.counter][0])
            draw.text((64 - int(mwidth[0]/2),1), text=self.descr[self.counter][0], font=MenuBase.font, fill="white")

            #icons as menu buttons
            symbols_per_page = self.lines_per_page * self.symbols_per_line

            page = (self.counter) // (self.lines_per_page * self.symbols_per_line) 

            i = page * symbols_per_page

            current_line = 0
            current_symbol = 0

            while (i < symbols_per_page * (page+1)) and (i < len(self.descr)):
                x_coord = 11 + 31 * current_symbol
                y_coord = 20 + 25 * current_line

                if (self.counter == i):
                    fill = settings.COLOR_SELECTED
                    outline = settings.COLOR_SELECTED_OUTLINE
                else:
                    fill = "white"
                    outline = "black"

                if (i == self.counter):
                    y_coord -= 2

                draw.text((x_coord, y_coord) , text=self.descr[i][1], font=MenuBase.faicons, outline=outline, fill=fill)

                current_symbol += 1

                if current_symbol >= self.symbols_per_line:
                    current_symbol = 0
                    current_line += 1

                i += 1

    def activate(self):
        self.counter = 0

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'up' or key == '2':
                direction = -self.symbols_per_line
            elif key == 'down' or key == '8':
                direction = self.symbols_per_line
            elif key == 'left' or key == '4':
                direction = -1
            elif key == 'right' or key == '6':
                direction = 1
            elif key == '#':
               self.windowmanager.set_window("idle")


        if (self.counter + direction < len(self.descr) and self.counter + direction >= 0):
            self.counter += direction


