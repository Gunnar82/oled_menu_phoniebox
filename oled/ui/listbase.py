""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
from datetime import datetime

import settings

class ListBase(WindowBase):
    def __init__(self, windowmanager, title):
        super().__init__(windowmanager)
        self.counter = 0
        self.page = 0
        self.menu = []
        self.basetitle = title
        self.left_pressed = False
        self.right_pressed = False
        self.drawtextx = 0
        self.position = -1
        self.progress = {}
        self.displaylines = 9 if settings.DISPLAY_HEIGHT > 64 else 4
        self.position = (self.counter + self.page -2 ) if (self.counter > 1) else -1
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
            if self.counter == 0:
                draw.text((1, 1), text="\uf137", font=self.faicons, fill=settings.COLOR_SELECTED)
                draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf106", font=self.faicons, fill="white")
            elif self.counter == 1:
                draw.text((1, 1), text="\uf104", font=self.faicons, fill="white")
                draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf139", font=self.faicons, fill=settings.COLOR_SELECTED)

            else:
                draw.text((1, 1), text="\uf104", font=self.faicons, fill="white")
                draw.text((settings.DISPLAY_WIDTH - settings.FONT_SIZE_NORMAL, 1), text="\uf106", font=self.faicons, fill="white")

            #Calculate title coordinate from text lenght
            linewidth,lineheight = self.font.getsize(self.title)
            draw.text(((settings.DISPLAY_WIDTH-linewidth)/2, 1), text=self.title, font=self.font, fill="white")

            #Playlists
            menulen = self.displaylines if (len(self.menu) >= self.displaylines) else len(self.menu)

            linewidth,lineheight = self.font.getsize(self.menu[0])

            startx = settings.FONT_HEIGHT_NORMAL

            for i in range(menulen):

                if self.counter + self.page -2  == i + self.page: #selected
                    drawtext = self.menu[i+self.page]
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
                    yoffsetright = 128
                    try:
                        drawtext = self.progress[self.menu[i+self.page]]
                        draw.text((100, 17+i*12), "%2.0d%%" % (drawtext*100), font=self.font, fill="white")
                        yoffsetright = 16
                    except:
                        pass

                    draw.text((startx, startx  + i * lineheight), self.menu[i+self.page][:yoffsetright], font=self.font, fill="white")
                    #drawrectangle((90 , 17+i*12 , 128 , 34+i*12 ), outline="black", fill="black")




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
            elif key == '2':
                direction = -1
            elif key == '8':
                direction = 1
            elif key =='A':
                direction = 0
                self.page = 0
                self.counter = 2
            elif key == 'D':
                direction = 0
                if len(self.menu) <= self.displaylines:
                    self.page = 0
                else:
                    self.page = len(self.menu) - self.displaylines
                    self.counter = self.displaylines + 1
            elif key == 'B':
                    direction = 0 - self.displaylines
            elif key == 'C':
                    direction = self.displaylines



        if (len(self.menu) < self.displaylines):
            print ("Handling Short Menu Items: %d, Lines: %d" % (len(self.menu), self.displaylines))

            self.page = 0
            if self.counter + direction -  2 > len(self.menu) - 1: # zero based
                self.counter = len(self.menu) + 2 - 1
            elif self.counter + direction < 0: # base counter is 2
                self.counter = 0
            else:
               self.counter += direction
        elif direction > 0:
            if self.counter - 1 + self.page > len(self.menu) - 1: # zero based
                self.counter = self.displaylines + 1 # self.counter: base is 2
                self.page = len(self.menu) - self.displaylines
            else:
                if (self.counter + direction > self.displaylines + 1):
                    self.page += direction
                else:
                    self.counter += direction


        elif direction < 0:

            if self.page > 0:

                if self.counter + direction >= 2:
                    self.counter += direction

                elif self.page + direction >= 0:
                    self.page += direction
                elif self.page + direction < 0:
                    self.page = 0
            else:
                self.counter += direction

            if self.counter + 1 + self.page < 2:
                self.counter = 0
                self.page = 0

        self.position = (self.counter + self.page -2 ) if (self.counter > 1) else -1
        self.selection_changed = True



