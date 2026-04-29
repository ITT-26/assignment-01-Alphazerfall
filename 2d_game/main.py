import numpy as np
import random
import pyglet
from pyglet import window, shapes
from pathlib import Path
from DIPPID import SensorUDP

PORT = 5700
sensor = SensorUDP(PORT)

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
ALIEN_TICKRATE_START = 60
PLAYER_SHOOT_COOLDOWN = 0.3

SPRITE_PATH = Path("2d_game/assets/sprites/invaders")
AUDIO_PATH = Path("2d_game/assets/audio")
SHOOT_SOUND = pyglet.media.load(str(AUDIO_PATH / "shoot.wav"), streaming=False)
EXPLOSION_SOUND = pyglet.media.load(str(AUDIO_PATH / "explosion.wav"), streaming=False)
pyglet.font.add_file(r".\2d_game\assets\fonts\space_invaders.ttf")


class Game:
    def __init__(self):
        self.tick = 0
        self.alien_tickrate = ALIEN_TICKRATE_START
        self.alien_direction = 1

        self.player = Player(300, 20)

        self.aliens, self.aliens_batch = self._new_layer()
        self.obstacles, self.obstacles_batch = self._new_layer()
        self.lasers, self.lasers_batch = self._new_layer()
        self.explosions, self.explosions_batch = self._new_layer()
        self.labels, self.labels_batch = self._new_layer()

        self.spawn_aliens()
        self.spawn_obstacles()

        self.score = 0
        self.lives = 3
        self.score_label = pyglet.text.Label(f"Score: {self.score}", font_name="Space Invaders", font_size=12, x=10, y=WINDOW_HEIGHT - 30, batch=self.labels_batch)
        self.lives_label = pyglet.text.Label(f"Lives: {self.lives}", font_name="Space Invaders", font_size=12, x=510, y=WINDOW_HEIGHT - 30, batch=self.labels_batch)
        self.crt = CRT(WINDOW_WIDTH, WINDOW_HEIGHT)

    def update(self, dt):
        self.player.update(dt)
        self.move_aliens()
        self.handle_shooting()
        self.lasers = [laser for laser in self.lasers if not laser.update(dt)]
        self.explosions = [ex for ex in self.explosions if not ex.update(dt)]
        self.handle_collisions()
        self.score_label.text = f"Score: {self.score}"
        self.lives_label.text = f"Lives: {self.lives}"
        self.tick += 1

    def draw(self):
        self.player.sprite.draw()
        self.aliens_batch.draw()
        self.obstacles_batch.draw()
        self.lasers_batch.draw()
        self.explosions_batch.draw()
        self.labels_batch.draw()
        self.crt.draw()

    def spawn_aliens(self):
        rows = [("space__0000_A1.png", "space__0001_A2.png", 30, 0)] \
             + [("space__0002_B1.png", "space__0003_B2.png", 20, 0)] * 2 \
             + [("space__0004_C1.png", "space__0005_C2.png", 10, 10)] * 2
        for i, (image_name, alternate_image_name, points, x_offset) in enumerate(rows):
            image = pyglet.image.load(str(SPRITE_PATH / image_name))
            alt_image = pyglet.image.load(str(SPRITE_PATH / alternate_image_name))
            for j in range(11):
                self.aliens.append(Alien(100 + x_offset + j * 40, 500 - i * 40, points, image, alt_image, batch=self.aliens_batch))

    def spawn_obstacles(self):
        for i in range(4):
            self.obstacles.append(Obstacle(40 + i * 150, 75, self.obstacles_batch, self.labels_batch))

    def spawn_explosion(self, x, y, object):
        self.explosions.append(Explosion(x, y, object, batch=self.explosions_batch))

    def move_aliens(self):
        if self.tick % self.alien_tickrate == 0:
            for alien in self.aliens:
                if (self.alien_direction == -1 and alien.sprite.x <= 15) or (self.alien_direction == 1 and alien.sprite.x >= WINDOW_WIDTH - alien.sprite.width - 15):
                    self.alien_direction *= -1
                    for a in self.aliens:
                        a.sprite.y -= 35
                        a.toggle_sprite()  # toggle sprite for simple animation
                    return
            for alien in self.aliens:
                alien.sprite.x += 5 * self.alien_direction
                alien.toggle_sprite()
                if alien.sprite.y <= 0:  # if any alien reaches the bottom, it's game over
                    self.game_over()

    def handle_shooting(self):
        # player shooting
        if sensor.get_value("button_1") | sensor.get_value("button_2") | sensor.get_value("button_3"):
            laser = self.player.shoot(batch=self.lasers_batch)
            if laser:
                self.lasers.append(laser)

        # random alien shooting
        for alien in self.aliens:
            if np.random.rand() < 0.0003:  # 0.03% chance to shoot each frame
                self.lasers.append(alien.shoot(self.lasers_batch))

    def handle_collisions(self):
        for laser in self.lasers[:]:  # iterate over a copy since we may modify the list
            if hit_obstacle := laser.collides_with(self.obstacles):
                self.hit_obstacle(hit_obstacle)
                self.lasers.remove(laser)
            elif laser.direction == 1 and (hit_alien := laser.collides_with(self.aliens)):
                self.kill_alien(hit_alien)
                self.lasers.remove(laser)
            elif laser.direction == -1 and laser.collides_with([self.player]):
                self.hit_player()
                self.lasers.remove(laser)

    def kill_alien(self, alien):
        self.spawn_explosion(alien.sprite.x, alien.sprite.y, alien)
        self.aliens.remove(alien)
        self.score += alien.point_value
        self.alien_tickrate = max(10, self.alien_tickrate - 2) # increase speed as aliens are killed
        if len(self.aliens) == 0:
            self.score += 200  # bonus for clearing all aliens
            self.aliens.clear()  # remove any remaining alien sprites
            self.spawn_aliens() # respawn aliens when all are killed
    
    def hit_player(self):
        self.spawn_explosion(self.player.sprite.x, self.player.sprite.y, self.player)
        self.lives -= 1
        if self.lives <= 0:
            self.player.sprite.delete()  # remove player sprite on death
            self.game_over()
    
    def hit_obstacle(self, obstacle):
        obstacle.health -= 1
        obstacle.refresh_health_label()
        if obstacle.health <= 0:
            self.obstacles.remove(obstacle)
            self.spawn_explosion(obstacle.sprite.x, obstacle.sprite.y, obstacle)
    
    def game_over(self):
        print("Game Over! Final Score:", self.score)
        pyglet.app.exit()

    def _new_layer(self):
        return [], pyglet.graphics.Batch()

class Player:
    def __init__(self, x, y):
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0006_Player.png")), x=x, y=y)
        self.sprite.color = (0, 255, 0)  # make player green
        self.cooldown = 0

    def shoot(self, batch):
        if self.cooldown <= 0:
            SHOOT_SOUND.play()
            self.cooldown = PLAYER_SHOOT_COOLDOWN
            return Laser(self.sprite.x + self.sprite.width // 2 - 5, self.sprite.y + self.sprite.height, 3, 10, (255, 255, 255), direction=1, batch=batch)

    def move(self):
        self.sprite.x -= np.clip(sensor.get_value("accelerometer")["x"] * 5, -5, 5)  # move player by tilting DIPPID device
        if self.sprite.x < 0:
            self.sprite.x = 0
        elif self.sprite.x + self.sprite.width > WINDOW_WIDTH:
            self.sprite.x = WINDOW_WIDTH - self.sprite.width

    def update(self, dt):
        self.move()
        if self.cooldown > 0:
            self.cooldown -= dt


class Alien:
    def __init__(self, x, y, point_value, image, alternate_image, batch):
        self.point_value = point_value
        self.images = [image, alternate_image]
        self.sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch)
        
    def shoot(self, batch):
        return Laser(self.sprite.x + self.sprite.width // 2 - 5, self.sprite.y, 3, 10, (255, 255, 255), direction=-1, batch=batch)

    def toggle_sprite(self):
        self.images.reverse()
        self.sprite.image = self.images[0]


class Obstacle:
    def __init__(self, x, y, sprite_batch, labels_batch):
        self.health = 30
        self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0008_ShieldFull.png")), x=x, y=y, batch=sprite_batch)
        self.sprite.color = (0, 255, 0)
        self.health_label = pyglet.text.Label(str(self.health), font_name="Space Invaders", font_size=12, x=x + 12, y=y + 12, color=(50, 50, 50), batch=labels_batch)

    def refresh_health_label(self):
        self.health_label.text = str(self.health)


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
            self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0010_PlayerExplosion.png")), x=x, y=y, batch=batch)
        else:
            self.sprite = pyglet.sprite.Sprite(pyglet.image.load(str(SPRITE_PATH / "space__0009_EnemyExplosion.png")), x=x, y=y, batch=batch)
        self.lifetime = 0.5  # explosion lasts for 0.5 seconds
        EXPLOSION_SOUND.play()

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            return True


class CRT:
    # CRT shader effect based on https://github.com/clear-code-projects/Space-invaders
    def __init__(self, width, height):    
        image = pyglet.image.load("2d_game/assets/sprites/tv.png")
        self.tv = pyglet.sprite.Sprite(image)
        self.tv.color = (255, 255, 255)
        
        self.line_batch = pyglet.graphics.Batch()
        self.lines = [
            shapes.Rectangle(0, y, width, 1, color=(0, 0, 0), batch=self.line_batch)
            for y in range(0, height, 3)
        ]

    def draw(self):
        # Flicker
        alpha = random.randint(75, 90)
        self.tv.opacity = alpha
        for line in self.lines:
            line.opacity = alpha
        self.tv.draw()
        self.line_batch.draw()


if __name__ == '__main__':
    win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Space Invaders", resizable=False)
    pyglet.gl.glClearColor(50/255, 50/255, 50/255, 1.0)
    game = Game()

    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.Q:
            pyglet.app.exit()

    @win.event
    def on_draw():
        win.clear()
        game.draw()

    pyglet.clock.schedule_interval(game.update, 1/60.0)  # 60 FPS
    pyglet.app.run()

