from random import choice, randint
from pygame import *
from time import time as now

SCREEN_SIZE = (1920, 1080)
SPRITE_SIZE = 50


# Базовый класс для спрайтов
class GameSprite(sprite.Sprite):
    def __init__(self, x, y, speed, texture, image_scale=1):
        super().__init__()
        self.image = transform.scale(
                            image.load(texture),
                            (SPRITE_SIZE // image_scale  , SPRITE_SIZE // image_scale  ))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def show(self):
        scene.blit(self.image, (self.rect.x, self.rect.y))


class LifeDrop(GameSprite):
    def __init__(self, x, y, speed, texture, image_scale=1):
        super().__init__(x, y, speed, 'rocket.png', image_scale)
    
    def use(self):
        player.hp += 1
    
    def update(self):
        self.rect.y += self.speed

class AtomicDrop(GameSprite):
    def __init__(self, x, y, speed, texture, image_scale=1):
        super().__init__(x, y, speed, 'atomic.png', 1)
    
    def use(self):
        for e in enemies:
            e.rect.x = randint(0, SCREEN_SIZE[0]-SPRITE_SIZE)
            e.rect.y = 0
            e.restore_hp()
            killed_counter.count += 1
            killed_counter.render_text() 

    def update(self):
        self.rect.y += self.speed 

drops = sprite.Group()

class Animation(sprite.Sprite):
    def __init__(self, x, y, texture):
        super().__init__()
        self.image = transform.scale(image.load(texture), (SPRITE_SIZE*8*2, SPRITE_SIZE*2))
        self.pos = (x-SPRITE_SIZE//2, y-SPRITE_SIZE//2 )
        self.frames = []
        self.frame_width = SPRITE_SIZE*2
        self.frame_height = SPRITE_SIZE*2
        for i in range(0, self.image.get_width(), self.frame_width):
            frame = Rect(i, 0, self.frame_width, self.frame_height)
            self.frames.append(frame)
        self.frame_index  = 0
    
    def update(self):
        if self.frame_index < len(self.frames):
            scene.blit(self.image, self.pos, self.frames[self.frame_index])
            self.frame_index += 1

anims = sprite.Group()

# Класс для игрока
class Player(GameSprite):
    def __init__(self, x, y, speed, texture, hp=3):
        super().__init__(x, y, speed, texture)
        self.last_shoot = 0
        self.hp = hp
        self.hp_image = transform.scale(
                            image.load(texture),
                            (SPRITE_SIZE // 2, SPRITE_SIZE // 2))
        self.hp_image_width = self.hp_image.get_rect().width

    def draw_hp(self):
        for i in range(1, self.hp+1):
            scene.blit(self.hp_image, (SCREEN_SIZE[0] - i * (5 + self.hp_image_width), 5))

    def update(self):
        k = key.get_pressed()
        if k[K_a]:
            self.rect.x -= self.speed
            if self.rect.x <= - SPRITE_SIZE:
                self.rect.x = SCREEN_SIZE[0] - SPRITE_SIZE
        if k[K_d]:
            self.rect.x += self.speed
            if self.rect.x >= SCREEN_SIZE[0]:
                self.rect.x = - SPRITE_SIZE
        if k[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
        if k[K_s] and self.rect.y < SCREEN_SIZE[1] - SPRITE_SIZE:
            self.rect.y += self.speed
        if k[K_SPACE]:
            if now() - self.last_shoot >= .2:
                self.shoot()
                self.last_shoot = now()
    
    def shoot(self):
        new_bullet = Bullet(self.rect.x + SPRITE_SIZE // 3, self.rect.y-5, 7, 'bullet.png')
        bullets.add(new_bullet)
        mixer.Sound('fire.ogg').play()


# Класс для врага
class Enemy(GameSprite):
    def __init__(self, x, y, speed, texture):
        if speed == 1:
            image_scale = 1
        else:
            image_scale = 2
        super().__init__(x, y, speed, texture, image_scale)
        self.restore_hp()

    def restore_hp(self):
        if self.speed == 1:
            self.hp = 3
        else:
            self.hp = 1

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= SCREEN_SIZE[1]:
            self.rect.y = 0
            self.rect.x = randint(0, SCREEN_SIZE[0]-SPRITE_SIZE)
            missed_counter.count += 1
            missed_counter.render_text()

class Asteroid(GameSprite):
    def __init__(self, x, y, speed, texture, image_scale=1):
        super().__init__(x, y, speed, texture, image_scale)
        self.angle = 0
        self.rotated_image = self.image
        self.rotated_rect = self.image.get_rect(center=(SPRITE_SIZE//2, SPRITE_SIZE//2))

    def rotate(self):
        self.angle += 1
        self.angle = self.angle % 360
        self.rotated_image = transform.rotate(self.image, self.angle)
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)

    def update(self):
        self.rect.y += self.speed
        shift_x = 1
        if self.rect.x > player.rect.x:
            self.rect.x -= shift_x
        else:
            self.rect.x += shift_x       
        if self.rect.y >= SCREEN_SIZE[1]:
            self.rect.y = 0
            self.rect.x = randint(0, SCREEN_SIZE[0]-SPRITE_SIZE)
        
        self.rotate()

    def show(self):
        scene.blit(self.rotated_image, self.rotated_rect)

# Класс Пуля
class Bullet(sprite.Sprite):
    def __init__(self, x, y, speed, texture):
        super().__init__()
        self.image = transform.scale(
                            image.load(texture),
                            (SPRITE_SIZE // 3, SPRITE_SIZE // 3))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        self.rect.y -= self.speed

bullets = sprite.Group()

font.init()
class Counter:
    def __init__(self, x, y, text, text_size, text_color, font_name='Arial'):
        self.pos = (x, y)
        self.text = text
        self.text_size = text_size
        self.text_color = text_color
        self.font_name = font_name
        self.count = 0

    def render_text(self):
        f = font.SysFont(self.font_name, self.text_size)
        self.image = f.render(self.text + str(self.count), True, self.text_color)
    
    def show_text(self):
        scene.blit(self.image, self.pos)
    


# Игровая сцена
scene = display.set_mode (SCREEN_SIZE)
display.set_caption("Шутер")
# Загрузка картинки для игровой сцены
bg = transform.scale(
        image.load('galaxy.jpg'),
        SCREEN_SIZE
)
# Фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
# Создание спрайтов
player = Player(SCREEN_SIZE[0]//2 - SPRITE_SIZE//2, 
                SCREEN_SIZE[1] - SPRITE_SIZE, 
                SCREEN_SIZE[0] // 120, 
                'rocket.png')
# Создание счетчиков
missed_counter = Counter(10, 10, 'Количество пропущенных: ', 18, (255, 255, 255))
missed_counter.render_text()
killed_counter = Counter(10, 30, 'Количество уничтоженных: ', 18, (255, 255, 255))
killed_counter.render_text()


asteroid = Asteroid(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), 0, 1, 'asteroid.png')
# Создание врагов
enemies = sprite.Group()
for _ in range(5):
    enemies.add(Enemy(randint(0, SCREEN_SIZE[0]-SPRITE_SIZE), 0, randint(1,3), 'ufo.png'))


# Игровой таймер
clock = time.Clock()
# Игровой цикл
game = True
finished = False
while game:
    # FPS
    clock.tick(60)
    scene.blit(bg, (0, 0))
    if finished is False:
        if randint(1, 400) == 1:
            class_name = choice([AtomicDrop, LifeDrop])
            drops.add(class_name(randint(0, SCREEN_SIZE[0] - SPRITE_SIZE), 0, 1, '', 2))
        player.update()
        player.show()
        player.draw_hp()
        enemies.update()
        enemies.draw(scene)
        bullets.update()
        bullets.draw(scene)
        missed_counter.show_text()
        killed_counter.show_text()
        collisions = sprite.groupcollide(enemies, bullets, False, True)
        for enemy in collisions.keys():
            new_anim = Animation(enemy.rect.x, enemy.rect.y, 'explosion.png')
            anims.add(new_anim)
            enemy.hp -= 1
            if enemy.hp <= 0:
                enemy.restore_hp()
                enemy.rect.y = 0
                enemy.rect.x = randint(0, SCREEN_SIZE[0] - SPRITE_SIZE)
                killed_counter.count += 1
                killed_counter.render_text()
                if killed_counter.count >= 50:
                    final_text = 'You WIN!'
                    finished = True
        anims.update()
        asteroid.update()
        asteroid.show()
        drops.update()
        drops.draw(scene)
        if sprite.spritecollideany(player, drops):
            drop = sprite.spritecollideany(player, drops)
            drop.use()
            drops.remove(drop)

        if sprite.collide_rect(player, asteroid):
            asteroid.rect.y = 0
            asteroid.rect.x = randint(0, SCREEN_SIZE[0] - SPRITE_SIZE)    
            player.hp -= 1

        if sprite.spritecollideany(player, enemies):
            enemy = sprite.spritecollideany(player, enemies)
            enemy.rect.y = 0
            enemy.rect.x = randint(0, SCREEN_SIZE[0] - SPRITE_SIZE) 
            player.hp -= 1
        if player.hp <= 0:
            final_text = 'You lose'
            finished = True
    else:
        final_caption = font.SysFont('Tahoma', 50).render(final_text, True, (255,0,0))
        scene.blit(final_caption, ((SCREEN_SIZE[0] - final_caption.get_width())//2, (SCREEN_SIZE[1] - final_caption.get_height())//2))
    display.update()
    
    # Выход из цикла при нажатии ALF+F4 или на крестик в окне
    for e in event.get():
        if e.type == QUIT:
            game = False

