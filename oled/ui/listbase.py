""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
from datetime import datetime

import settings


from integrations.logging import *

class ListBase(WindowBase):
    def __init__(self, windowmanager, title):
        super().__init__(windowmanager)
        self.menu = []
        self.basetitle = title
        self.left_pressed = False
        self.right_pressed = False
        self.drawtextx = 0
        self.position = -2
        self.progress = {}
        self.displaylines = settings.DISPLAY_HEIGHT // 20
        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_SMALL)
        self.faicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_SMALL)
        self.selection_changed = True

    def render(self):

        if self.left_pressed:
            self.left_pressed = False
            self.on_key_left()
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
                draw.rectangle((0, settings.DISPLAY_HEIGHT - 1, settings.DISPLAY_WIDTH, settings.DISPLAY_HEIGHT - 1),outline=settings.COLOR_SELECTED, fill=settings.COLOR_SELECTED)
                draw.rectangle((mypos - 5, settings.DISPLAY_HEIGHT - 1, mypos + 5, settings.DISPLAY_HEIGHT - 1),outline="black", fill="black")
            except:
                pass

            #Back button and selection arrow
            if self.position == -2:
                draw.text((1, 1), text="\uf137", font=self.faicons, fill=settings.COLOR_SELECTED)
                draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf106", font=self.faicons, fill="white")
            elif self.position == -1:
                draw.text((1, 1), text="\uf104", font=self.faicons, fill="white")
                draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf139", font=self.faicons, fill=settings.COLOR_SELECTED)

            else:
                draw.text((1, 1), text="\uf104", font=self.faicons, fill="white")
                draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf106", font=self.faicons, fill="white")

            #Calculate title coordinate from text lenght
            linewidth,lineheight = self.font.getsize(self.title)
            draw.text(((settings.DISPLAY_WIDTH-linewidth)/2, 1), text=self.title, font=self.font, fill="white")

            #Playlists
            menulen = len(self.menu)

            linewidth,lineheight = self.font.getsize("000")

            startx = settings.FONT_HEIGHT_NORMAL

            seite = 0 if self.position < 0 else self.position // self.displaylines

            pos = 0 if self.position < 0 else self.position % self.displaylines 

            maxpos = (self.displaylines if (seite + 1) * self.displaylines <= menulen else (menulen % self.displaylines))


            for i in range(maxpos):
                if self.position  == seite * self.displaylines+ i : #selected
                    progresscolor = settings.COLOR_SELECTED
                    drawtext = self.menu[seite * self.displaylines + i]
                    if (datetime.now()-settings.lastinput).total_seconds() > 2:
                        if self.font.getsize(drawtext[self.drawtextx:])[0] > settings.DISPLAY_WIDTH -1:
                            self.drawtextx += 1
                        else:
                            self.drawtextx = 0
                    #Selection arrow
                    draw.polygon(((1, 11+startx + i * lineheight - lineheight / 2), (1, 15+startx + i * lineheight - lineheight / 2 ),
                                        (5, 13+startx + i * lineheight - lineheight / 2)), fill=settings.COLOR_SELECTED)

                    draw.text((startx, startx + i * lineheight), drawtext[self.drawtextx:], font=self.font, fill=settings.COLOR_SELECTED)

                else:
                    progresscolor = settings.COLOR_GREEN

                    draw.text((startx, startx  + i * lineheight), self.menu[seite *self.displaylines + i], font=self.font, fill="white")
                
                try:
                    drawtext = "%2.0d%%" % (self.progress[self.menu[seite * self.displaylines + i]])
                    linewidth1, lineheight1 = self.font.getsize(drawtext)
                    log(lDEBUG2,"listbase: percent:%s:" %(drawtext))
                    draw.rectangle((settings.DISPLAY_WIDTH - linewidth1 - 15  , startx + i * lineheight , settings.DISPLAY_WIDTH , startx + (i + 1) * lineheight ), outline="black", fill="black")
                    draw.text((settings.DISPLAY_WIDTH - linewidth1 - 5, startx + i * lineheight), drawtext, font=self.font, fill=progresscolor)
                except:
                    log(lDEBUG2,"no percentage")




    def on_key_left(self):
        raise NotImplementedError()

    def on_key_right(self):
        raise NotImplementedError()

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'left' or key == '4' or key == '0':
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
            elif key == 'B' or key== 'HL':
                    direction = 0 - self.displaylines
            elif key == 'C' or key == 'HR':
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



