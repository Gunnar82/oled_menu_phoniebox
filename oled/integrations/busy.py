""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings


font = ImageFont.truetype(settings.FONT_TEXT, size=12)
faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
faiconsbig = ImageFont.truetype(settings.FONT_ICONS, size=35)



def render(device,activewindow):
    with canvas(device) as draw:

        mwidth = font.getsize(settings.PLEASE_WAIT)
        draw.text(((64 - int(mwidth[0]/2)), 5), text=settings.PLEASE_WAIT, font=font, fill="white") #sanduhr

        mwidth = faiconsbig.getsize(activewindow.busysymbol)
        draw.text(((64 - int(mwidth[0]/2)), 25), text=activewindow.busysymbol, font=faiconsbig, fill="white") #sanduhr

