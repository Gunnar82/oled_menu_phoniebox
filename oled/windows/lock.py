""" Start screen """

from ui.mainwindow import MainWindow
from luma.core.render import canvas
from PIL import ImageFont
import settings
import config.colors as colors
import config.symbols as symbols
import random  # Beibehalten, da verwendet

class Lock(MainWindow):
    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
    fontawesome = ImageFont.truetype(settings.FONT_ICONS, size=settings.FONT_SIZE_XXL)
    busysymbol=symbols.SYMBOL_LOCKED

    def __init__(self, windowmanager,loop,usersettings, nowplaying,musicmanager):
        super().__init__(windowmanager, loop,usersettings, nowplaying)
        self.musicmanager = musicmanager
        self.timeout = False
        self.window_on_back = "idle"
        self.busyrendertime = 0.25

        self.timeout = False
        self.unlockindex = -1

        self.currentkey = 0
        self.handle_key_back = False



    def gen_unlockcodes(self):
        """Generiert die möglichen Entsperrcodes."""
        self.unlockcodes = [
            ['up','down','left','right'],
            ['1','2','3','4','5','6','7','8','9','0','a','b','c','d']
        ]

    def reversemap(self,key):
        if key == '2':
            return 'up'
        elif key == '4':
            return 'left'
        elif key == '6':
            return 'right'
        elif key == '8':
            return 'down'
        else:
            return key


    def activate(self):
        """Aktiviert die Entsperrfunktionalität und generiert zufällige Entsperrcodes."""
        self.gen_unlockcodes()
        self.unlockcode = []

        if "gpicase" in settings.INPUTS or "gp280" in settings.INPUTS: self.unlockindex = 0
        elif "keypad4x4" in settings.INPUTS: self.unlockindex = 1
        self.symbolwidth, temp = self.fontawesome.getsize(self.busysymbol)

        if self.unlockindex == -1:
            self.set_busyinfo(item="Kein kompatibler INPUT",symbol=symbols.SYMBOL_ERROR,wait=5,set_window=True)
        else:
            try:
                for r in range(0,4):
                    length = len(self.unlockcodes[self.unlockindex])
                    pos = random.randint(0,length-1)
                    char = self.unlockcodes[ self.unlockindex ][pos]

                    self.unlockcode.append(char)
                    self.unlockcodes[ self.unlockindex ].remove(char)

            except:
                self.gen_unlockcodes()
                self.set_busyinfo(item="Random Fehler",set_window=True)

            self.currentkey = 0
            self.genhint()

    def turn_callback(self,direction, key=None):
        """Überprüft, ob der gedrückte Schlüssel korrekt ist."""
        if "gpicase" in settings.INPUTS:
            key = self.reversemap(key)
        if key.lower() in ['f','key_pause']:
            self.musicmanager.playpause()
        elif key.lower() == self.unlockcode[self.currentkey].lower():
            self.busysymbol = symbols.SYMBOL_PASS
            self.currentkey += 1
        else:
            self.busysymbol = symbols.SYMBOL_FAIL
            self.currentkey = 0

        if self.currentkey >= len(self.unlockcode):
             self.currentkey = 0 
             self.set_busyinfo(item="Gerät entsperrt",symbol=symbols.SYMBOL_UNLOCKED,wait=5,set_window=True)
        else:
            self.genhint()

    def genhint(self):
        """Generiert den Hinweistext für den aktuellen Entsperrcode."""
        self.unlocktext = ' '.join(
            [f"> {char.upper()} <" if i == self.currentkey else char.lower() for i, char in enumerate(self.unlockcode)]
        )
        self.textwidth, _ = self.font.getsize(self.unlocktext)

    def render(self):
        """Rendern des Bildschirms mit dem Entsperrcode."""
        with canvas(self.device) as draw:
            super().render(draw)
            draw.text(((settings.DISPLAY_WIDTH - self.symbolwidth) / 2, settings.DISPLAY_HEIGHT - 5*settings.IDLE_LINE_HEIGHT ), self.busysymbol, font=self.fontawesome, fill=colors.COLOR_RED)
            draw.text(((settings.DISPLAY_WIDTH - self.textwidth) / 2, settings.DISPLAY_HEIGHT - 3*settings.IDLE_LINE_HEIGHT ), self.unlocktext , font=self.font, fill="white")
