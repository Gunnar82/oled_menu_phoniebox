""" Start screen """
from ui.windowbase import WindowBase
from luma.core.render import canvas
from PIL import ImageFont

import random
import asyncio
import time
import settings
import integrations.playout as playout

from integrations.logging_config import setup_logger

logger = setup_logger(__name__)


import config.colors as colors

from datetime import datetime

class SnakeGame(WindowBase):

    font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_SMALL)

    def __init__(self, windowmanager, loop):
        super().__init__(windowmanager, loop)
#        self.font = ImageFont.truetype(settings.FONT_TEXT, size=settings.FONT_SIZE_L)
        self.timeout = False
        self._rendertime = 0.1


        self.width = settings.DISPLAY_WIDTH
        self.height = settings.DISPLAY_HEIGHT - 50
        self.snake_size = 20  # Größe der Schlange (5x5 Pixel)
        self.moving_size = 2

    def init_game(self):
        try:
            self.snake = [(self.width // 2, self.height // 2)]  # Startposition der Schlange
            self.direction = (self.moving_size, 0)  # Startbewegung: Nach rechts
            self.food = self.random_food_position()  # Position des Essens
            self.score = 0
            self.speed = 0.1
            self.game_over = False
            self.loop.create_task(self.play_game())
        except Exception as e:
            print (e)


    def activate(self):
        self.init_game()
        self.game_over = True

    async def play_game(self):
        while not self.game_over:
            try:
                if not self.game_over:
                    """Bewegt die Schlange um ein Feld in die aktuelle Richtung."""
                    if self.game_over:
                        return

                    # Neues Kopfteil der Schlange
                    new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

                    # Überprüfung auf Kollisionen mit der Wand oder der Schlange selbst
                    if (new_head[0] < 0 or new_head[0] >= self.width or
                        new_head[1] < 0 or new_head[1] >= self.height or
                        new_head in self.snake):
                        self.game_over = True
                        return

                    # Bewegen der Schlange
                    self.snake.insert(0, new_head)

                    # Überprüfen, ob die Schlange das Essen erreicht hat
                    if self.check_food_collision(new_head):
                        self.score += 1
                        self.food = self.random_food_position()  # Neues Essen
                        self.speed = max(0.05, self.speed * 0.9) 
                    else:
                        self.snake.pop()  # Das letzte Segment der Schlange wird entfernt
            except Exception as e:
                print (e)

            await asyncio.sleep (self.speed)

    def render(self):
        with canvas(self.device) as draw:
            if self.game_over:
                draw.text((20, self.height // 2), "Game Over -  A to start", font=self.font, fill="white")

            else:

                # Zeichne die Schlange
                for segment in self.snake:
                    x, y = segment
                    draw.rectangle((x, y, x + self.snake_size - 1, y + self.snake_size - 1), outline="white", fill="white")


                # Zeichne das Essen (5x5 Pixel großes Rechteck)
                food_x, food_y = self.food
                draw.rectangle((food_x, food_y, food_x + self.snake_size - 1, food_y + self.snake_size - 1), outline="red", fill="red")

                draw.text((0, self.height+20), f"Score: {self.score}", font=self.font, fill="white")
                draw.text((200, self.height+20), f"Speed: {self.speed:.2f}", font=self.font, fill="white")

    def push_callback(self, lp=False):
        if self.game_over:
            self.init_game()

    def turn_callback(self, direction, key=None):
        if key == 'up':
            self.change_direction((0, -self.moving_size))
        elif key == 'down':
            self.change_direction((0, self.moving_size))
        elif key == 'left':
            self.change_direction((-self.moving_size, 0))
        elif key == 'right':
            self.change_direction((self.moving_size, 0))
        elif key == 'q':
            pass

    def deactivate(self):
        self.game_over = True


    # Snake-Spiel

    def random_food_position(self):
        """Generiert eine zufällige Position für das Essen auf dem Spielfeld."""
        while True:
            pos = (random.randint(0, (self.width // self.snake_size) - 1) * self.snake_size,
                   random.randint(0, (self.height // self.snake_size) - 1) * self.snake_size)
            if pos not in self.snake:  # Essen darf nicht auf der Schlange erscheinen
                return pos

    def change_direction(self, direction):
        """Ändert die Bewegungsrichtung der Schlange."""
        if self.game_over:
            return

        # Die Schlange kann nicht direkt in die entgegengesetzte Richtung fahren
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction


    def check_food_collision(self, head):
        """Überprüft, ob die Schlange das Essen berührt (unter Berücksichtigung der Schlangengröße)."""
        head_x, head_y = head
        food_x, food_y = self.food

        # Prüfe, ob das Essen innerhalb des Bereichs des Kopfsegments liegt (inklusive seiner Größe)
        if (food_x < head_x + self.snake_size and
            food_x + self.snake_size > head_x and
            food_y < head_y + self.snake_size and
            food_y + self.snake_size > head_y):
            return True
        return False