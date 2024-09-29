""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

import config.colors as colors
import config.symbols as symbols
import time

from integrations.logging_config import *

logger = setup_logger(__name__)


class MenuBase(WindowBase):
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.MENUBASE_ICON_SIZE)

    iconwidth, iconheight = faicons.getsize(symbols.SYMBOL_USB)

    def __init__(self, windowmanager,loop,title):
        super().__init__(windowmanager,loop)
        self.counter = 0
        self.descr = []
        self.descr.append([ "Zurück", "\uf0a8"])
        self.basetitle = title
        self.lines_per_page = 4 if settings.DISPLAY_HEIGHT >= 128 else 2
        self.symbols_per_line = 4


    def render(self):
        with canvas(self.device) as draw:
            headingwidth, headingheight = self.fontheading.getsize(self.descr[self.counter][0])
            draw.text((int(settings.DISPLAY_WIDTH / 2) - int(headingwidth/2),1), text=self.descr[self.counter][0], font=self.fontheading, fill="white")

            #icons as menu buttons
            symbols_per_page = self.lines_per_page * self.symbols_per_line

            page = (self.counter) // (self.lines_per_page * self.symbols_per_line) 

            i = page * symbols_per_page

            current_line = 0
            current_symbol = 0

            # TODO GENAUE MITTE BERECHNEN
            startx = int(settings.DISPLAY_WIDTH /2) -  int(self.iconwidth * self.symbols_per_line / 2) - int ((self.symbols_per_line - 1) * 0.2 )

            while (i < symbols_per_page * (page+1)) and (i < len(self.descr)):
                x_coord = startx + ( self.iconwidth * 1.2 ) * current_symbol
                y_coord = settings.MENUBASE_START_Y  + self.iconheight * 1.3  * current_line

                if (self.counter == i):
                    fill = colors.COLOR_SELECTED
                    outline = colors.COLOR_SELECTED_OUTLINE
                else:
                    fill = "white"
                    outline = "black"

                if (i == self.counter):
                    y_coord -= 2
                    draw.rectangle((x_coord + 2, y_coord + self.iconheight + 2 ,x_coord + self.iconwidth - 5, y_coord + self.iconheight + 5) , outline=outline, fill=fill)

                draw.text((x_coord, y_coord) , text=self.descr[i][1], font=self.faicons, outline=outline, fill=fill)

                current_symbol += 1

                if current_symbol >= self.symbols_per_line:
                    current_symbol = 0
                    current_line += 1

                i += 1

    def activate(self):
        self.counter = 0


    def push_handler(self):
        raise NotImplementedError()

    def push_callback(self,lp=False):
        if self.counter == 0:
            self.windowmanager.set_window(self.window_on_back)
        else:
            self.set_busyinfo(item = self.descr[self.counter][0],symbol=self.descr[self.counter][1],wait=2)
            self.loop.run_in_executor(None,self.push_handler)

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


