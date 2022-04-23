""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
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

        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=11)
        with canvas(self.device) as draw:
            #Back button and selection arrow
            if self.counter == 0:
                draw.text((1, 1), text="\uf137", font=faicons, fill=settings.COLOR_SELECTED)
                draw.text((110, 1), text="\uf106", font=faicons, fill="white")
            elif self.counter == 1:
                draw.text((1, 1), text="\uf104", font=faicons, fill="white")
                draw.text((110, 1), text="\uf139", font=faicons, fill=settings.COLOR_SELECTED)

            else:
                draw.text((1, 1), text="\uf104", font=faicons, fill="white")
                draw.text((110, 1), text="\uf106", font=faicons, fill="white")
                #Selection arrow
                draw.polygon(((1, 7+(self.counter-1)*12), (1, 11+(self.counter-1)*12),
                                        (5, 9+(self.counter-1)*12)), fill=settings.COLOR_SELECTED)

            #Calculate title coordinate from text lenght
            draw.text(((128-len(self.title)*5)/2, 1), text=self.title, font=font, fill="white")

            #Playlists
            menulen = self.displaylines -1 if (len(self.menu) >= self.displaylines) else len(self.menu) - 1
            for i in range(menulen):
                if self.counter +self.page -2  == i + self.page:
                    drawtext = self.menu[i+self.page]
                    if font.getsize(drawtext[self.drawtextx:])[0] > 127:
                        self.drawtextx += 1
                    else:
                        self.drawtextx = 0

                    draw.text((8, 17+i*12), drawtext[self.drawtextx:], font=font, fill=settings.COLOR_SELECTED)

                else:
                    draw.text((8, 17+i*12), self.menu[i+self.page], font=font, fill="white")
                    draw.rectangle((90 , 17+i*12 , 128 , 34+i*12 ), outline="black", fill="black")

                    try:
                        drawtext = self.progress[self.menu[i+self.page]]
                        draw.text((100, 17+i*12), "%2.0d%%" % (drawtext*100), font=font, fill="white")
                    except:
                        pass


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


        if self.counter + direction >= 0:
            #first 4 items in long menu
            if self.counter > 1:
                if len(self.menu) > self.displaylines:
                    if ((self.counter-1) + direction >= 1) and ((self.counter-1) + direction <= self.displaylines):
                        self.counter += direction
                    #other items in long menu
                    elif (self.page + direction + self.displaylines <= len(self.menu)) and (self.page + direction  >= 0):
                        self.page += direction
                    elif (self.page == 0) and (self.counter > 0):
                        self.counter += direction
                #short menu < 4 items
                else:
                    if len(self.menu) <= self.displaylines and (self.counter-1) + direction <= len(self.menu):
                        self.counter += direction
            elif self.counter + direction >= 0:
                self.counter += direction
            self.position = (self.counter + self.page -2 ) if (self.counter > 1) else -1



