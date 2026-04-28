import numpy as np
import pyglet
from pyglet import window, shapes
from DIPPID import SensorUDP
from pathlib import Path

PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
ALIEN_TICKRATE_START = 60
AUDIO_PATH = Path("2d_game/assets/audio")
#SHOOT_SOUND = pyglet.resource.media(AUDIO_PATH + r"\shoot.wav", streaming=False)
EXPLOSION_SOUND = pyglet.media.load(str(AUDIO_PATH / "explosion.wav"), streaming=False)
SPRITE_PATH = Path("2d_game/assets/sprites/invaders")


class Game:
    def __init__(self):
        self.tick = 0
        self.alien_tickrate = ALIEN_TICKRATE_START
        self.alien_direction = 1

        self.player = Player(300, 20)

        self.aliens = []
        self.alien_batch = pyglet.graphics.Batch()
        self.spawn_aliens()

        self.obstacles = []
        self.obstacle_batch = pyglet.graphics.Batch()
        self.spawn_obstacles()

        self.lasers = []
        self.lasers_batch = pyglet.graphics.Batch()

        self.explosions = []
        self.explosion_batch = pyglet.graphics.Batch()

        self.score = 0
        self.lives = 3
        pyglet.font.add_file(r".\2d_game\assets\fonts\space_invaders.ttf")
        self.score_label = pyglet.text.Label(f"Score: {self.score}", font_name="Space Invaders", font_size=12, x=10, y=WINDOW_HEIGHT - 30)
        self.lives_label = pyglet.text.Label(f"Lives: {self.lives}", font_name="Space Invaders", font_size=12, x=510, y=WINDOW_HEIGHT - 30)

        
    def update(self, dt):
        self.player.move()
        self.move_aliens()

        if sensor.get_value("button_1") | sensor.get_value("button_2") | sensor.get_value("button_3"):
            self.player.shoot(batch=self.lasers_batch)

        if self.player.laser:
            if self.player.laser.update(dt):
                self.player.laser = None
            else:
                hit_alien = self.player.laser.collides_with(self.aliens)
                if hit_alien:
                    self.spawn_explosion(hit_alien.sprite.x, hit_alien.sprite.y, hit_alien)
                    self.aliens.remove(hit_alien)
                    self.player.laser = None
                    self.alien_tickrate = max(10, self.alien_tickrate - 2) # increase speed as aliens are killed
                    self.score += 100
                    if len(self.aliens) == 0:
                        self.score += 1000  # bonus for clearing all aliens
                        self.spawn_aliens(self.alien_batch)
        

        # random Alien shooting 
        for alien in self.aliens:
            if np.random.rand() < 0.0002:  # 0.02% chance to shoot each frame
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
                        pyglet.app.exit()

        for explosion in self.explosions:
            if explosion.update(dt):
                self.explosions.remove(explosion)
        self.tick += 1

    def spawn_obstacles(self):
        for i in range(4):
            self.obstacles.append(Obstacle(150 + i * 150, 100, batch=self.obstacle_batch))

    def spawn_aliens(self):
        for i in range(6):
            for j in range(8):
                self.aliens.append(Alien(70 + j * 60, 250 + i * 35, batch=self.alien_batch))
    
    def spawn_explosion(self, x, y, object):
        self.explosions.append(Explosion(x, y, object, batch=self.explosion_batch))

    def move_aliens(self):
        if self.tick % self.alien_tickrate == 0:
            for alien in self.aliens:
                if (self.alien_direction == -1 and alien.sprite.x <= 15) or (self.alien_direction == 1 and alien.sprite.x >= WINDOW_WIDTH - alien.sprite.width - 15):
                    self.alien_direction *= -1
                    for a in self.aliens:
                        a.sprite.y -= 35
                    return
            for alien in self.aliens:
                alien.sprite.x += 20 * self.alien_direction

    def draw(self):
        self.player.sprite.draw()
        self.alien_batch.draw()
        self.obstacle_batch.draw()
        self.lasers_batch.draw()
        self.explosion_batch.draw()
        self.score_label.text = f'Score: {self.score}'
        self.score_label.draw()
        self.lives_label.text = f'Lives: {self.lives}'
        self.lives_label.draw()
    

class Player:
    def __init__(self, x, y):
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0006_Player.png")), x=x, y=y)
        self.sprite.color = (0, 255, 0)  # make player green
        self.laser = None

    def shoot(self, batch):
        if self.laser is None:
            self.laser = Laser(self.sprite.x + self.sprite.width // 2 - 5, self.sprite.y + self.sprite.height, 3, 10, (255, 255, 255), direction=1, batch=batch)

    def move(self):
        self.sprite.x -= np.clip(sensor.get_value("accelerometer")["x"] * 5, -5, 5)  # move player
        if self.sprite.x < 0:
            self.sprite.x = 0
        elif self.sprite.x + self.sprite.width > WINDOW_WIDTH:
            self.sprite.x = WINDOW_WIDTH - self.sprite.width


class Alien:
    def __init__(self, x, y, batch):
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0000_A1.png")), x=x, y=y, batch=batch)

    def shoot(self, batch):
        return Laser(self.sprite.x + self.sprite.width // 2 - 5, self.sprite.y, 3, 10, (255, 255, 255), direction=-1, batch=batch)


class Obstacle:
    def __init__(self, x, y, batch):
        self.health = 30
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0008_ShieldFull.png")), x=x, y=y, batch=batch)
        self.sprite.color = (0, 255, 0)  # make obstacle green


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
            if (self.shape.x < target.sprite.x + target.sprite.width and
                    self.shape.x + self.shape.width > target.sprite.x and
                    self.shape.y < target.sprite.y + target.sprite.height and
                    self.shape.y + self.shape.height > target.sprite.y):
                return target
        return False

class Explosion:
    def __init__(self, x, y, object, batch):
        if isinstance(object, Player):
            self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0009_EnemyExplosion.png")), x=x, y=y, batch=batch)
        else:
            self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0010_PlayerExplosion.png")), x=x, y=y, batch=batch)
        self.lifetime = 0.5  # explosion lasts for 0.5 seconds
        EXPLOSION_SOUND.play()

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            return True


if __name__ == '__main__':
    win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    game = Game()

    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.Q:
            pyglet.app.exit()


    @win.event
    def on_draw():
        win.clear()
        game.draw()

    pyglet.clock.schedule_interval(game.update, 1/60.0) # 60 FPS
    pyglet.app.run()

