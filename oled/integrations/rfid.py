""" Shutdown menu """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont
import settings


font = ImageFont.truetype(settings.FONT_TEXT, size=12)
faicons = ImageFont.truetype(settings.FONT_ICONS, size=18)
faiconsxl = ImageFont.truetype(settings.FONT_ICONS, size=30)



def render(device,activewindow):
    with canvas(device) as draw:

        mwidth = faiconsxl.getsize(settings.SYMBOL_CARD_READ)
        draw.text( (int(64 - mwidth[0]/2) , 5), settings.SYMBOL_CARD_READ, font=faiconsxl, fill="white")

        mwidth = font.getsize(settings.CARD_READ)
        draw.text(((64 - int(mwidth[0]/2)), 45), text=settings.CARD_READ, font=font, fill="white") 

