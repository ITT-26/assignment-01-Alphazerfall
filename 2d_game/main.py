import sys
import numpy as np
import pyglet
from pyglet import window, shapes
from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
ALIEN_TICKRATE_START = 60

class Game:
    def __init__(self):
        self.tick = 0
        self.alien_tickrate = ALIEN_TICKRATE_START
        self.alien_direction = 1

        self.player = Player(300, 20, 50, 10, (0, 255, 0))
        self.aliens = []
        for i in range(6):
            for j in range(8):
                self.aliens.append(Alien(70 + j * 60, 500 - i * 48, 20, 20, (255, 255, 255)))
        self.lasers = []
        
    def update(self, dt):
        self.player.shape.x -= np.clip(sensor.get_value("accelerometer")["x"] * 5, -5, 5)
        self.constraint()
        if sensor.get_value("button_1") | sensor.get_value("button_2") | sensor.get_value("button_3"):
            self.player.shoot()

        self.tick += 1
        if self.tick % self.alien_tickrate == 0:
            for alien in self.aliens:
                if (self.alien_direction == -1 and alien.shape.x <= 0) or (self.alien_direction == 1 and alien.shape.x >= WINDOW_WIDTH - alien.shape.width):
                    self.alien_direction *= -1
                    for a in self.aliens:
                        a.shape.y -= 48
                    return
            for alien in self.aliens:
                alien.shape.x += 20 * self.alien_direction

    def draw(self):
        self.player.shape.draw()
        for alien in self.aliens:
            alien.shape.draw()
        for laser in self.lasers:
            laser.shape.draw()

    def constraint(self):
        if self.player.shape.x < 0:
            self.player.shape.x = 0
        elif self.player.shape.x + self.player.shape.width > WINDOW_WIDTH:
            self.player.shape.x = WINDOW_WIDTH - self.player.shape.width

    

class Player:
    def __init__(self, x, y, width, height, color):
        self.shape = shapes.Rectangle(x, y, width, height, color)
        self.laser = None

    def shoot(self):
        if self.laser is None:
            self.laser = Laser(self.shape.x + self.shape.width // 2 - 5, self.shape.y + self.shape.height, 3, 10, (255, 255, 255), direction=1, owner=self)




class Alien:
    def __init__(self, x, y, width, height, color):
        self.shape = shapes.Rectangle(x, y, width, height, color)


class Laser:
    def __init__(self, x, y, width, height, color, direction=1, owner=None):
        self.shape = shapes.Rectangle(x, y, width, height, color)
        self.direction = direction
        self.owner = owner

    def update(self, dt):
        self.shape.y += 20 * dt * self.direction
        if self.shape.y > WINDOW_HEIGHT or self.shape.y < 0:
            self.owner.laser = None
            return True



def main():
    win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    game = Game()

    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.Q:
            win.close()
            sys.exit(0)
        if symbol == pyglet.window.key.SPACE:
            game.player.shoot()

    @win.event
    def on_draw():
        win.clear()
        game.draw()

    pyglet.clock.schedule_interval(game.update, 1/60.0) # 60 FPS
    pyglet.app.run()



if __name__ == '__main__':
    main()