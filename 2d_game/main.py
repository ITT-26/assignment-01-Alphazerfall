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
        self.alien_batch = pyglet.graphics.Batch()
        self.spawn_aliens()

        self.lasers = []
        self.lasers_batch = pyglet.graphics.Batch()

        self.obstacles = []
        self.obstacle_batch = pyglet.graphics.Batch()
        self.spawn_obstacles()

        self.score = 0
        self.lives = 3
        self.score_label = pyglet.text.Label(f'Score: {self.score}', font_size=18, x=10, y=WINDOW_HEIGHT - 30)
        self.lives_label = pyglet.text.Label(f'Lives: {self.lives}', font_size=18, x=510, y=WINDOW_HEIGHT - 30)

        
    def update(self, dt):
        self.player.move()
        self.move_aliens()

        #if sensor.get_value("button_1") | sensor.get_value("button_2") | sensor.get_value("button_3"):
        #    self.player.shoot()
        if self.player.laser:
            if self.player.laser.update(dt):
                self.player.laser = None
            else:
                hit_alien = self.player.laser.collides_with(self.aliens)
                if hit_alien:
                    self.aliens.remove(hit_alien)
                    self.player.laser = None
                    self.alien_tickrate = max(10, self.alien_tickrate - 2) # increase speed as aliens are killed
                    self.score += 100
                    if len(self.aliens) == 0:
                        self.score += 1000  # bonus for clearing all aliens
                        self.spawn_aliens(self.alien_batch)

        # random Alien shooting 
        for alien in self.aliens:
            if np.random.rand() < 0.0005:  # 0.05% chance to shoot each frame
                self.lasers.append(alien.shoot(self.lasers_batch))
        for laser in self.lasers:
            if laser.update(dt):
                self.lasers.remove(laser)
        for laser in self.lasers:
                hit_player = laser.collides_with([self.player])
                if hit_player:
                    self.lasers.remove(laser)
                    self.lives -= 1
                    if self.lives <= 0:
                        print("Game Over! Final Score:", self.score)
                        sys.exit(0)

        self.tick += 1

    def spawn_obstacles(self):
        for i in range(3):
            self.obstacles.append(Obstacle(150 + i * 150, 150, 50, 30, (0, 255, 0), batch=self.obstacle_batch))

    def spawn_aliens(self):
        for i in range(6):
            for j in range(8):
                self.aliens.append(Alien(70 + j * 60, 250 + i * 35, 25, 25, (255, 255, 255), batch=self.alien_batch))


    def move_aliens(self):
        if self.tick % self.alien_tickrate == 0:
            for alien in self.aliens:
                if (self.alien_direction == -1 and alien.shape.x <= 15) or (self.alien_direction == 1 and alien.shape.x >= WINDOW_WIDTH - alien.shape.width - 15):
                    self.alien_direction *= -1
                    for a in self.aliens:
                        a.shape.y -= 35
                    return
            for alien in self.aliens:
                alien.shape.x += 20 * self.alien_direction

    def draw(self):
        self.player.shape.draw()
        self.alien_batch.draw()
        self.lasers_batch.draw()
        self.obstacle_batch.draw()
        #self.player.laser.shape.draw() if self.player.laser else None
        self.score_label.text = f'Score: {self.score}'
        self.score_label.draw()
        self.lives_label.text = f'Lives: {self.lives}'
        self.lives_label.draw()

    

class Player:
    def __init__(self, x, y, width, height, color):
        self.shape = shapes.Rectangle(x, y, width, height, color)
        self.laser = None

    def shoot(self, batch):
        if self.laser is None:
            self.laser = Laser(self.shape.x + self.shape.width // 2 - 5, self.shape.y + self.shape.height, 3, 10, (255, 255, 255), direction=1, batch=batch)

    def move(self):
        #self.player.shape.x -= np.clip(sensor.get_value("accelerometer")["x"] * 5, -5, 5)  # move player
        if self.shape.x < 0:
            self.shape.x = 0
        elif self.shape.x + self.shape.width > WINDOW_WIDTH:
            self.shape.x = WINDOW_WIDTH - self.shape.width




class Alien:
    def __init__(self, x, y, width, height, color, batch):
        self.shape = shapes.Rectangle(x, y, width, height, color, batch=batch)

    def shoot(self, batch):
        return Laser(self.shape.x + self.shape.width // 2 - 5, self.shape.y, 3, 10, (255, 255, 255), direction=-1, batch=batch)


class Obstacle:
    def __init__(self, x, y, width, height, color, batch):
        self.health = 30
        self.shape = shapes.Rectangle(x, y, width, height, color, batch=batch)
    

class Laser:
    def __init__(self, x, y, width, height, color, direction=1, batch=None):
        self.shape = shapes.Rectangle(x, y, width, height, color, batch=batch)
        self.direction = direction

    def update(self, dt):
        self.shape.y += 200 * dt * self.direction # move laser
        if self.shape.y > WINDOW_HEIGHT or self.shape.y < 0:
            return True

    def collides_with(self, targets):
        for target in targets:
            if (self.shape.x < target.shape.x + target.shape.width and
                    self.shape.x + self.shape.width > target.shape.x and
                    self.shape.y < target.shape.y + target.shape.height and
                    self.shape.y + self.shape.height > target.shape.y):
                return target
        return False



if __name__ == '__main__':
    win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    game = Game()

    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.Q:
            win.close()
            sys.exit(0)
        if symbol == pyglet.window.key.SPACE:
            game.player.shoot(game.lasers_batch)
        if symbol == pyglet.window.key.RIGHT:
            game.player.shape.x += 10
        if symbol == pyglet.window.key.LEFT:
            game.player.shape.x -= 10

    @win.event
    def on_draw():
        win.clear()
        game.draw()

    pyglet.clock.schedule_interval(game.update, 1/60.0) # 60 FPS
    pyglet.app.run()

