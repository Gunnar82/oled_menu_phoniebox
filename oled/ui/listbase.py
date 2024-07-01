""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
from datetime import datetime

import settings

import config.colors as colors
import config.symbols as symbols


from integrations.logging import *

class ListBase(WindowBase):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.LISTBASE_ENTRY_SIZE)
    faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.LISTBASE_ENTRY_SIZE)

    comment = ["c", "h"]

    def __init__(self, windowmanager, loop, title):
        super().__init__(windowmanager, loop)
        self.menu = []
        self.basetitle = title
        self.left_pressed = False
        self.right_pressed = False
        self.drawtextx = 0
        self.position = -2
        self.progress = {}
        self.selection_changed = True
        self.handle_left_key = True
        self.titlelineheight = self.font.getsize(self.basetitle)[1] + 3

        self.entrylinewidth,self.entrylineheight = self.font.getsize("000")
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

        if self.position >= 0:
            self.title = "%s %2.2d / %2.2d" %(self.basetitle, self.position + 1,len(self.menu))
        else:
            self.title = self.basetitle

        with canvas(self.device) as draw:
            #progressbar
            try:
                mypos = int((self.position + 1) / len(self.menu) * settings.DISPLAY_WIDTH)
                draw.rectangle((0, settings.DISPLAY_HEIGHT - 1, settings.DISPLAY_WIDTH, settings.DISPLAY_HEIGHT - 1),outline=colors.COLOR_SELECTED, fill=colors.COLOR_SELECTED)
                draw.rectangle((mypos - 5, settings.DISPLAY_HEIGHT - 1, mypos + 5, settings.DISPLAY_HEIGHT - 1),outline="black", fill="black")
            except:
                pass

            #Back button and selection arrow
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

            titlelinewidth = self.font.getsize(self.title)[0]
            draw.text(((settings.DISPLAY_WIDTH-titlelinewidth)/2, 1), text=self.title, font=self.fontheading, fill="white")

            #Playlists
            menulen = len(self.menu)

            seite = 0 if self.position < 0 else self.position // self.displaylines

            pos = 0 if self.position < 0 else self.position % self.displaylines 

            maxpos = (self.displaylines if (seite + 1) * self.displaylines <= menulen else (menulen % self.displaylines))
 

            for i in range(maxpos):
                scrolling = False

                current_y = self.titlelineheight + i * self.entrylineheight

                if self.position  == seite * self.displaylines+ i : #selected
                    progresscolor = colors.COLOR_SELECTED
                    drawtext = self.menu[seite * self.displaylines + i][0]
                    if (datetime.now()-settings.lastinput).total_seconds() > 2:
                        if self.font.getsize(drawtext[self.drawtextx:])[0] > settings.DISPLAY_WIDTH -1 - self.startleft:
                            self.drawtextx += 1
                            scrolling = True
                        else:
                            self.drawtextx = 0


                    draw.text((2, current_y + 2), symbols.SYMBOL_LIST_SELECTED, font=self.faicons, fill=colors.COLOR_SELECTED)

                    draw.text((self.startleft , current_y), drawtext[self.drawtextx:], font=self.font, fill=colors.COLOR_SELECTED)

                else:
                    progresscolor = colors.COLOR_GREEN

                    draw.text((self.startleft, current_y), self.menu[seite *self.displaylines + i][0], font=self.font, fill="white")

                try:
                    if not scrolling:
                        drawtext = self.progress[self.menu[seite * self.displaylines + i][0]]
                        linewidth1, lineheight1 = self.font.getsize(drawtext)
                        log(lDEBUG2,"listbase: percent:%s:" %(drawtext))
                        draw.rectangle((settings.DISPLAY_WIDTH - linewidth1 - 15  , current_y , settings.DISPLAY_WIDTH , current_y + self.entrylineheight ), outline="black", fill="black")
                        draw.text((settings.DISPLAY_WIDTH - linewidth1 - self.startleft, current_y), drawtext, font=self.font, fill=progresscolor)
                except Exception as error:
                    log(lDEBUG2,"no percentage")

    def is_comment(self):
        try:
            return self.menu[self.position][1] in self.comment
        except:
            return False

    def on_key_left(self):
        raise NotImplementedError()

    def on_key_right(self):
        if not self.is_comment():
            self.push_callback()

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        if key:
            if (key == 'left' or key == '4' or key == 'Y') and self.handle_left_key:
                self.set_busy("übergeordneter Ordner",busyrendertime=1)
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

        log(lDEBUG,"Handling  Menu Items: %d, Lines: %d, direction: %s" % (len(self.menu), self.displaylines, direction))

        if self.position + direction  >= len(self.menu) : # zero based
            self.position = len(self.menu) -1
        elif self.position + direction < -2: # base counter is 2
            self.position = -2
        else:
           self.position += direction

        self.selection_changed = True

        log(lDEBUG,"self.position: %d" % (self.position))



