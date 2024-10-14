""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import time

import settings

import config.colors as colors
import config.symbols as symbols

from integrations.logging_config import *

logger = setup_logger(__name__)

class ListBase(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.LISTBASE_ENTRY_SIZE)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.LISTBASE_ENTRY_SIZE)
    faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_L)

    comment = ["c"]
    heading = ["h"]
    symbol = ["s"]

    info_key_left = True

    render_progressbar = True
    show_position = True
    is_type_info = False


    def __init__(self, windowmanager, loop, title):
        super().__init__(windowmanager, loop)
        self.menu = []
        self.basetitle = title
        self.title = title
        self.left_pressed = False
        self.right_pressed = False
        self.drawtextx = 0
        self.position = -2
        self.progressbarpos = 0
        self.selection_changed = True
        self.handle_left_key = True
        self.hide_buttons = False
        self.titlelineheight = self.font.getsize(self.basetitle)[1] + 3

        self.entrylinewidth,self.entrylineheight = self.font.getsize("000")
        self.symbolentrylinewidth,self.symbolentrylineheight = self.faiconsbig.getsize(symbols.SYMBOL_SANDCLOCK)

        self.displaylines = (settings.DISPLAY_HEIGHT - self.titlelineheight) // self.entrylineheight # - title (height)

        self.startleft, self.selected_symbol_height = self.faicons.getsize(symbols.SYMBOL_LIST_SELECTED)
        self.startleft += 5

    def render(self):
        if self.left_pressed and self.handle_left_key:
            self.left_pressed = False
            self.loop.run_in_executor(None,self.on_key_left)
            return

        if self.right_pressed:
            self.right_pressed = False
            self.on_key_right()
            return

        if self.position >= 0 and self.show_position:
            title = "%s %2.2d / %2.2d" %(self.title, self.position + 1,len(self.menu))
        else:
            title = self.title

        with canvas(self.device) as draw:

            #progressbar
            try:
                self.progressbarpos = (self.position + 1) / len(self.menu)
            except Exception as error:
                logger.debug(f"{error}")


            #Back button and selection arrow
            if not self.hide_buttons:
                if self.position == -2:
                    draw.text((1, 1), text="\uf137", font=self.faicons, fill=colors.COLOR_SELECTED)
                    draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf106", font=self.faicons, fill="white")
                elif self.position == -1:
                    draw.text((1, 1), text="\uf104", font=self.faicons, fill="white")
                    draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf139", font=self.faicons, fill=colors.COLOR_SELECTED)

                else:
                    draw.text((1, 1), text="\uf104", font=self.faicons, fill="white")
                    draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf106", font=self.faicons, fill="white")

            #Calculate title coordinate from text lenght

            titlelinewidth = self.font.getsize(title)[0]
            draw.text(((settings.DISPLAY_WIDTH-titlelinewidth)/2, 1), text=title, font=self.fontheading, fill="white")

            #Playlists
            menulen = len(self.menu)

            seite = 0 if self.position < 0 else self.position // self.displaylines

            pos = 0 if self.position < 0 else self.position % self.displaylines 

            maxpos = (self.displaylines if (seite + 1) * self.displaylines <= menulen else (menulen % self.displaylines))

            current_y = self.titlelineheight

            for i in range(maxpos):
                scrolling = False

                selected_element = self.menu[seite * self.displaylines + i]
                logger.debug(f" list_loop: {selected_element}")

                try:
                    drawtext = symbols.SYMBOL_HEADING if isinstance(selected_element,list) and selected_element[1] in self.heading else ""
                    logger.debug("element is heading")
                except Exception as e:
                    drawtext = ""

                is_symbol = False
 
                logger.debug("selected element test")

                if isinstance(selected_element,list):
                    logger.debug(f"selected_element is list: {selected_element}")
                    drawtext += selected_element[0]

                    try:
                        if selected_element[1] == self.symbol:
                            is_symbol = True
                    except:
                        pass
                else:
                    logger.debug(f"item is no list {selected_element}")
                    drawtext += selected_element

                logger.debug(f"drawtext; {drawtext}")

                if self.position  == seite * self.displaylines+ i and not is_symbol: #selected
                    progresscolor = colors.COLOR_SELECTED

                    if (time.monotonic()-settings.lastinput) > 2:
                        if self.font.getsize(drawtext[self.drawtextx:])[0] > settings.DISPLAY_WIDTH -1 - self.startleft:
                            self.drawtextx += 1
                            scrolling = True
                        else:
                            self.drawtextx = 0


                    draw.text((2, current_y + 2), symbols.SYMBOL_LIST_SELECTED, font=self.faicons, fill=colors.COLOR_SELECTED)

                    draw.text((self.startleft , current_y), drawtext[self.drawtextx:], font=self.font, fill=colors.COLOR_SELECTED)

                else:
                    progresscolor = colors.COLOR_GREEN
                    if is_symbol:
                        draw.text(((settings.DISPLAY_WIDTH - self.symbolentrylinewidth) / 2, current_y), drawtext, font=self.faiconsbig, fill=colors.COLOR_RED)
                    else:
                        draw.text((self.startleft, current_y), drawtext, font=self.font, fill="white" if not self.is_type_info else colors.COLOR_GREEN)

                try:
                    selected_element = self.menu[seite * self.displaylines + i]
                    if not scrolling and isinstance(selected_element,list) and selected_element[2] != "":
                        drawtext = selected_element[2]
                        linewidth1, lineheight1 = self.font.getsize(drawtext)
                        logger.debug("listbase: percent:%s:" %(drawtext))
                        draw.rectangle((settings.DISPLAY_WIDTH - linewidth1 - 15  , current_y , settings.DISPLAY_WIDTH - 3 , current_y + self.entrylineheight ), outline="black", fill="black")
                        draw.text((settings.DISPLAY_WIDTH - linewidth1 - self.startleft, current_y), drawtext, font=self.font, fill=progresscolor)
                except Exception as error:
                    logger.debug(f"no percentage {error}")

                if is_symbol:
                    current_y += self.symbolentrylineheight
                else:
                    current_y += self.entrylineheight

            if self.render_progressbar: self.render_progressbar_draw(draw,self.progressbarpos,buttom_top = False)


    def is_heading(self):
        try:
            return self.menu[self.position][1] in self.heading
        except:
            return False


    def is_comment(self):
        try:
            return self.menu[self.position][1] in self.comment
        except:
            return False

    def on_key_left(self):
        raise NotImplementedError()

    def on_key_right(self):
        if not self.is_comment() and not self.is_heading():
            self.push_callback()

    def push_callback(self,lp=False):
        if self.counter in [ -1, -2]:
            self.windowmanager.set_window(self.window_on_back)
        else:
            if not self.is_comment() and not self.is_heading():
                self.loop.run_in_executor(None,self.push_handler)

    def turn_callback(self, direction, key=None):
        if key and not self.is_busy:
            if (key == 'left' or key == '4' or key == 'Y') and self.handle_left_key:
                self.left_pressed = True
                return
            elif key == 'right' or key == '6' or key == '*':
                self.right_pressed = True
                return
            elif key == 'up' or key == '2':
                direction = -1
            elif key == 'down' or key == '8':
                direction = 1
            elif key =='A':
                direction = 0
                self.position = 0
            elif key == 'D':
                direction = 0
                self.position = len(self.menu)
            elif key == 'B' or key== 'hl':
                    direction = 0 - self.displaylines
            elif key == 'C' or key == 'hr':
                    direction = self.displaylines

        logger.debug("Handling  Menu Items: %d, Lines: %d, direction: %s" % (len(self.menu), self.displaylines, direction))

        if self.position + direction  >= len(self.menu) : # zero based
            self.position = len(self.menu) -1
        elif self.position + direction < -2: # base counter is 2
            self.position = -2
        else:
           self.position += direction

        self.selection_changed = True


        logger.debug("self.position: %d" % (self.position))


    def appenditem(self,item):
        logger.debug(f"append item: {item}")
        self.menu.append(item)


    def appendheading(self,item):
        logger.debug(f"appendheading: {item}")
        self.menu.append([item,"h"])


    def appendcomment(self,item):
        logger.debug(f"appendheading: {item}")
        self.menu.append([item,"c"])

    def appendsymbol(self,item):
        logger.debug(f"appendsymbol: {item}")
        self.menu.append([item,self.symbol])

    def clearmenu(self):
        self.menu = []

    def set_last_position(self):
        self.position = len(self.menu) - 1