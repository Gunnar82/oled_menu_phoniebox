""" Scrollable menu window """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings

class MenuBase(WindowBase):
    def __init__(self, windowmanager, title):
        super().__init__(windowmanager)
        self.counter = 0
        self.page = 0
        self.menu = []
        self.title = title
        self.left_pressed = False
        self.right_pressed = False
        self.drawtextx = 0

    def render(self):
        if self.left_pressed:
            self.left_pressed = False
            self.on_key_left()
            return


        if self.right_pressed:
            self.right_pressed = False
            self.on_key_right()
            return

        font = ImageFont.truetype(settings.FONT_TEXT, size=12)
        faicons = ImageFont.truetype(settings.FONT_ICONS, size=11)
        with canvas(self.device) as draw:
            #Back button and selection arrow
            if self.counter == 0:
                draw.text((1, 1), text="\uf137", font=faicons, fill="white")
                draw.text((110, 1), text="\uf106", font=faicons, fill="white")
            elif self.counter == 1:
                draw.text((1, 1), text="\uf104", font=faicons, fill="white")
                draw.text((110, 1), text="\uf139", font=faicons, fill="white")

            else:
                draw.text((1, 1), text="\uf104", font=faicons, fill="white")
                draw.text((110, 1), text="\uf106", font=faicons, fill="white")
                #Selection arrow
                draw.polygon(((1, 7+(self.counter-1)*12), (1, 11+(self.counter-1)*12),
                                        (5, 9+(self.counter-1)*12)), fill="white")

            #Calculate title coordinate from text lenght
            draw.text(((128-len(self.title)*5)/2, 1), text=self.title, font=font, fill="white")

            #Playlists
            for i in range(4 if len(self.menu) >= 4 else len(self.menu)):
                if self.counter +self.page -2  == i + self.page:
                    drawtext = self.menu[i+self.page]
                    if font.getsize(drawtext[self.drawtextx:])[0] > 127:
                        self.drawtextx += 1
                    else:
                        self.drawtextx = 0
                    draw.text((8, 17+i*12), drawtext[self.drawtextx:], font=font, fill="white")
                else:
                    draw.text((8, 17+i*12), self.menu[i+self.page], font=font, fill="white")


    def on_key_left(self):
        raise NotImplementedError()

    def on_key_right(self):
        raise NotImplementedError()

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        if key:
            if key == 'left':
                self.left_pressed = True
            if key == 'right':
                self.right_pressed = True
                return

        if self.counter + direction >= 0:
            #first 4 items in long menu
            if len(self.menu) > 4 and (self.counter-1) + direction <= 4 and self.page == 0:
                self.counter += direction
            #other items in long menu
            elif len(self.menu) > 4 and self.page + direction + 4 <= len(self.menu):
                self.page += direction
            #short menu < 4 items
            elif len(self.menu) <= 4 and (self.counter-1) + direction <= len(self.menu):
                self.counter += direction


