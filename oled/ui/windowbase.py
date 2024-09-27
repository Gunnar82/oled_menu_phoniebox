""" View class to inherit other views from """

import settings

import config.colors as colors
import config.symbols as symbols

import asyncio

from PIL import ImageFont
from luma.core.render import canvas

import time

from luma.core.render import canvas


from integrations.logging_config import *

logger = setup_logger(__name__)

font = ImageFont.truetype(settings.FONT_TEXT, size=settings.WINDOWBASE_BUSYFONT)
busyfont = ImageFont.truetype(settings.FONT_TEXT, size=settings.LISTBASE_ENTRY_SIZE)
busyfaicons = ImageFont.truetype(settings.FONT_ICONS, size=settings.WINDOWBASE_BUSYFAICONS)
busyfaiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=settings.WINDOWBASE_BUSYFAICONSBIG)


class WindowBase():
    changerender = False
    fontheading = ImageFont.truetype(settings.FONT_TEXT, size=settings.WINDOWBASE_HEADING_SIZE)
    timeout = True
    contrasthandle = True
    windowtitle = "untitled"
    timeoutwindow="idle"
    window_on_back = "mainmenu"
    symbol = "s"
    error = "err"
    busysymbol = symbols.SYMBOL_SANDCLOCK
    busytext1 = settings.PLEASE_WAIT
    busytext2 = ""
    busytext3 = ""
    render_busy_progressbar = False
    busytext4 = ""
    busyrendertime = 3
    _rendertime = 0.25
    counter = 0
    page = 0
    handle_key_back = True


    new_busyrender = False
    is_busy = False
    busymenu = []
    busydrawtextx = 0
    lastbusytext = ""
    busyprogressbarpos = 0
    
    busyentrylinewidth, busyentrylineheight = busyfont.getsize("000")
    busytitlelineheight = busyfont.getsize("ZZZ")[1] + 3
    busydisplaylines = (settings.DISPLAY_HEIGHT - busytitlelineheight) // busyentrylineheight - 1# letzte Zeile gesondert
    startleft, selected_symbol_height = busyfaicons.getsize(symbols.SYMBOL_LIST_SELECTED)


    def __init__(self, windowmanager,loop):
        self.start_busyrendertime = time.monotonic()
        self.loop = loop
        self.windowmanager = windowmanager
        self.device = self.windowmanager.device

    def clear_window(self):
        self.device.clear()

    def set_busy(self,busytext1,busysymbol=symbols.SYMBOL_SANDCLOCK,busytext2="", busyrendertime=3,busytext3="",set_window=False):

        self.busytext1 = busytext1
        self.busysymbol = busysymbol

        self.busytext3 = busytext3
        if busyfont.getsize(busytext2)[0] > settings.DISPLAY_WIDTH:
            pos = len(busytext2) // 2
            self.busytext4 = busytext2[:pos]
            self.busytext2 = busytext2[pos:]

        else:
            self.busytext4 = ""
            self.busytext2 = busytext2

        self.busyrendertime = busyrendertime

        self.start_busyrendertime = time.monotonic()
        self.busy = True

        if set_window:
            self.loop.create_task(self.set_window(self.window_on_back))

    def renderbusy(self,symbolcolor = colors.COLOR_RED, textcolor1=colors.COLOR_WHITE, textcolor2=colors.COLOR_WHITE):
        with canvas(self.device) as draw:
            self.renderbusydraw(draw,symbolcolor,textcolor1,textcolor2)

    def renderbusydraw(self, draw, symbolcolor = colors.COLOR_RED, textcolor1=colors.COLOR_WHITE, textcolor2=colors.COLOR_WHITE):
        mwidth1,mheight1 = busyfont.getsize(self.busytext1)
        mwidth2,mheight2 = busyfont.getsize(self.busytext2)
        mwidth3,mheight3 = busyfont.getsize(self.busytext3)
        mwidth4,mheight4 = busyfont.getsize(self.busytext4)
        mwidth,mheight = busyfaiconsbig.getsize(self.busysymbol)

        draw.text(((settings.DISPLAY_WIDTH - mwidth1) / 2, 5), text=self.busytext1, font=busyfont, fill=textcolor1)

        if (self.busytext3 != ""):
            draw.text(((settings.DISPLAY_WIDTH - mwidth3) / 2, mheight1 + 3), text=self.busytext3, font=busyfont, fill=textcolor2) #sanduhr

        if (self.busytext2 != ""):
            draw.text(((settings.DISPLAY_WIDTH - mwidth2) / 2, settings.DISPLAY_HEIGHT - mheight2 - 3), text=self.busytext2, font=busyfont, fill=textcolor2) #sanduhr

        if (self.busytext4 != ""):
            draw.text(((settings.DISPLAY_WIDTH - mwidth4) / 2, settings.DISPLAY_HEIGHT - mheight2 - 3  - mheight4 - 3), text=self.busytext4, font=busyfont, fill=textcolor2) #sanduhr

        draw.text(((settings.DISPLAY_WIDTH - mwidth) / 2, (settings.DISPLAY_HEIGHT - mheight) / 2), text=self.busysymbol, font=busyfaiconsbig, fill=symbolcolor) #sanduhr

    def render_progressbar_draw(self,draw, pos=0, color1=colors.COLOR_YELLOW, color2=colors.COLOR_RED, buttom_top=True):
        logger.debug(f"render_progressbar_pos: started, pos: {pos}")
        try:
            mypos = int(pos * settings.DISPLAY_HEIGHT)

            if buttom_top:
                mypos = settings.DISPLAY_HEIGHT - mypos
                color1, color2 = color2, color1

            #schwarzer hintergrund
            draw.rectangle((settings.DISPLAY_WIDTH - 3, 0 , settings.DISPLAY_WIDTH , settings.DISPLAY_HEIGHT),outline="black", fill="black")

            draw.rectangle((settings.DISPLAY_WIDTH - 2, 0 , settings.DISPLAY_WIDTH, mypos - 3),outline=color1, fill=color1)
            draw.rectangle((settings.DISPLAY_WIDTH - 2, mypos + 3 , settings.DISPLAY_WIDTH, settings.DISPLAY_HEIGHT),outline=color2, fill=color2)

        except Exception as error:
            logger.debug(f"render_progressbarpos_draw: {error}")


    async def set_window(self,windowid):
        await asyncio.sleep(self.busyrendertime)
        self.windowmanager.set_window(windowid)

    def activate(self):
        self.clear_window()

    def deactivate(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()

    def push_callback(self,lp=False):
        raise NotImplementedError()

    def turn_callback(self, direction, key=None):
        raise NotImplementedError()

    # new busy handling
    def append_busytext(self,item="Verarbeite..."):
        logger.debug(f"append busyitem: {item}")
        self.busymenu.append(item)
        self.pop_busymenu()

    def append_busyerror(self,item="Fehler..."):
        logger.debug(f"append busyitem: {item}")
        self.busymenu.append([item,self.error])
        self.pop_busymenu()


    def append_busysymbol(self,item=None):
        logger.debug(f"append busysymbol: {item}")
        if item is None: item  = self.busysymbol  # Zugriff auf die Klassenvariable via self
        width,height = busyfaiconsbig.getsize(item)

        self.busymenu.append([item,self.symbol,width,height])
        self.pop_busymenu()


    def pop_busymenu(self):
        try:
            if len(self.busymenu) >= self.busydisplaylines : del (self.busymenu[0])
        except Exception as error:
            pass

    def clear_busymenu(self):
        self.busymenu = []
        self.set_lastbusytextline()

    def set_window_busy(self, state=True, with_symbol = True, clear_busymenu = True, render_progressbar = False, wait=1):

        self.render_busy_progressbar = render_progressbar

        if state and clear_busymenu: self.clear_busymenu()
        if not state and self.new_busyrender: time.sleep(wait)
        if with_symbol and state: self.append_busysymbol()
        self.is_busy = state
        self.set_lastbusytextline()


    def set_lastbusytextline(self, text=""):
        self.lastbusytext = text

    def new_renderbusy(self):
        try:
            with canvas (self.device) as draw:
                menulen = len(self.busymenu)
                position = len(self.busymenu)

                seite = position // self.busydisplaylines
                pos = position % self.busydisplaylines
                maxpos = (self.busydisplaylines if (seite + 1) * self.busydisplaylines <= menulen else (menulen % self.busydisplaylines))
                current_y = 0 # bei 0 beginnen

                for i in range(maxpos):
                    logger.debug(f"new_renderbusy: pos:{pos}, seite{seite}, position: {position}, i: {i}")

                    scrolling = False
                    selected_element = self.busymenu[seite * self.busydisplaylines + i]
                    is_symbol = False

                    progresscolor = colors.COLOR_GREEN


                    if isinstance(selected_element,list):
                        drawtext = selected_element[0]

                        try:
                            if selected_element[1] == self.symbol:
                                is_symbol = True
                        except:
                            pass


                        try:
                            if selected_element[1] == self.error:
                                progresscolor = colors.COLOR_ERROR

                        except:
                            pass
                    else:
                        drawtext = selected_element

                    if position  == seite * self.busydisplaylines + i + 1 and not is_symbol: #selected
                        progresscolor = colors.COLOR_SELECTED

                        if (time.monotonic()-settings.lastinput) > 2:
                            if busyfont.getsize(drawtext[self.busydrawtextx:])[0] > settings.DISPLAY_WIDTH -1 - self.startleft:
                                self.busydrawtextx += 1
                                scrolling = True
                            else:
                                self.busydrawtextx = 0

                        draw.text((self.startleft , current_y), drawtext[self.busydrawtextx:], font=busyfont, fill=colors.COLOR_SELECTED)

                    else:

                        if is_symbol:
                            draw.text(((settings.DISPLAY_WIDTH - selected_element[2]) / 2, current_y), drawtext, font=busyfaiconsbig, fill=colors.COLOR_RED)
                            current_y += selected_element[3] # Symbolhöhe

                        else:
                            draw.text((self.startleft, current_y), drawtext, font=busyfont, fill=progresscolor)
                            current_y += self.busyentrylineheight

                if self.lastbusytext != "":
                        draw.text((self.startleft, self.busydisplaylines * self.busyentrylineheight), self.lastbusytext, font=busyfont, fill=colors.COLOR_YELLOW)

                if self.render_busy_progressbar: self.render_progressbar_draw(draw,self.busyprogressbarpos)


        except Exception as error:
             logger.error(f"new_renderbusy: {error}")