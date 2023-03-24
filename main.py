import pygame, random, math, os
from os import listdir
import time
from os.path import isfile, join
from pygame import mixer
pygame.init()

WIDTH, HEIGHT = 1324, 745

pygame.display.set_caption("LEG DAY")

mixer.music.load('assets/Music/bgmusic.mp3')
mixer.music.play(-1)

BG_COLOR = (255, 255, 255)

FPS = 60 
PLAYER_VEL = 6

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height) , pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0 , width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "IndustrialTile_27.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

def get_block2(size):
    path = join("assets", "Terrain", "IndustrialTile_14.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

def get_block3(size):
    path = join("assets", "Objects", "pad.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Characters", "Cyborg", 48, 48, True)
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.radius = 25
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 600 #600 because the fps is 60
        self.maximum_health = 600
        self.health_bar_length = 400
        self.health_ratio = self.maximum_health / self.health_bar_length

    def basic_health(self):
        pygame.draw.rect(window, (0,234,76),(10,10,self.health / self.health_ratio, 25))
        pygame.draw.rect(window, (0,0,0),(10,10,self.health_bar_length, 25), 4)

    def get_damage(self,amount):
        if self.health > 0:
            self.health -= amount
            self.hit = True
            self.hit_count = 0
        if self.health <= 0:
            self.health = 0

    def get_health(self, amount):
        if self.health < self.maximum_health:
            self.health += amount
        if self.health >= self.maximum_health:
            self.health = self.maximum_health

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * .3:
            self.hit = False

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= 1
    
    def create_bullet(self):
        if self.direction == "right":
            return Bullet(self.rect.x + 75, self.rect.y + 43, self.direction)
        else:
            return Bullet(self.rect.x + 30, self.rect.y + 43, self.direction)
        
    def update_sprite(self):
        keys = pygame.key.get_pressed()
        sprite_sheet = "Cyborg_idle"
        if self.hit:
            sprite_sheet = "Cyborg_hurt"
            if self.health > 0:
                self.health -= 1
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "Cyborg_jump" 
                path = join('assets', 'SFX', 'jump.wav')
                impact = mixer.Sound(path)
                impact.play()
            elif self.jump_count == 2:
                sprite_sheet = "Cyborg_doublejump"
                path = join('assets', 'SFX', 'jump.wav')
                impact = mixer.Sound(path)
                impact.play()
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "Fall"
        elif self.x_vel != 0:
            sprite_sheet = "Cyborg_run"
        elif keys [pygame.K_SPACE]:
            sprite_sheet = "shoot"
            
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        self.basic_health()
    
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self,pos_x,pos_y, name):
        super().__init__()
        self.image = pygame.image.load("assets/Objects/7_1.png")
        self.image.fill((225,0,0))
        self.rect = self.image.get_rect(center = (pos_x,pos_y))
        self.direction = name

    def update(self):
        if self.direction == "right":
            self.rect.x += 10
        elif self.direction == "left":
            self.rect.x -= 10
            
        if self.rect.x >= WIDTH + 200:
            self.kill()

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block2(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block3(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Enemy(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    SPRITES = load_sprite_sheets("Characters", "Enemy", 48, 48, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.health = 120
        self.hit = False
        self.hit_count = 0
        self.life = True
        self.deathani = 0

    def get_damage(self,amount):
        if self.health > 0:
            self.health -= amount
            self.hit = True
            self.hit_count = 0
        if self.health <= 0:
            self.health = 0

    def move(self, dx):
        if self.health > 0:
            self.rect.x += dx
        else:
            self.rect.x = self.rect.x

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0


    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps):
        self.move(self.x_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * .3:
            self.hit = False
        
        if self.health <= 0:
            self.deathani += 1
        if self.deathani > fps * .46:
            self.life = False

        self.update_sprite()


    def update_sprite(self):
        image = "Walk_attack"

        it = 0

        if self.hit:
            image = "Punk_hurt"
            if self.health > 0:
                self.health -= 1
        elif self.health <= 0:
            image = "Punk_death"
        

        sprite_sheet_name = image + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
    
def draw(window, player, objects,offset_x, enemy, health):
    

    for obj in objects:
        obj.draw(window, offset_x)

    health.draw(window, offset_x)

    player.draw(window, offset_x)

    enemy.draw(window, offset_x)
    
    pygame.display.update()

def handle_vertical_collison(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

        collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object
            
def handle_move(player, enemy, objects, scroll):
    keys = pygame.key.get_pressed()


    player.x_vel = 0
    if keys[pygame.K_a] and player.rect.x > 0:
        player.move_left(PLAYER_VEL)
        scroll -= 5
    elif keys[pygame.K_d] and player.rect.x < 1400:
        player.move_right(PLAYER_VEL)
        scroll += 5

    
    ENEMY_VEL = 3
    if enemy.rect.x < -10:
        enemy.move_right(ENEMY_VEL)
    elif enemy.rect.x > 1260:
        enemy.move_left(ENEMY_VEL)



        
    handle_vertical_collison(player, objects, player.y_vel)


def main(window):
    clock = pygame.time.Clock()

    scroll = 0

    bg_images = []
    for i in range(1,7):
        bg_image = pygame.image.load(f"assets/Background/city 6/bg-{i}.png").convert_alpha()
        bg_image = pygame.transform.smoothscale(bg_image, (1324, 745))
        bg_images.append(bg_image)
    bg_width = bg_images[0].get_width()

    def draw_bg():
        for x in range(100):
            speed = 1
            for i in bg_images:
                window.blit(i, ((x * bg_width) - scroll * speed, 0))
                speed += .05

    block_size = 32

    floor_level = 100

    bullet_group = pygame.sprite.Group()
    bullet = bullet_group

    enemy_pos = HEIGHT - floor_level - 96

    health = Block3(100,HEIGHT - floor_level - 178 , 192)
    player = Player(WIDTH / 2, HEIGHT - floor_level - 2, 48, 48)
    enemy = Enemy(-12, enemy_pos, 48, 48)
    floor = [Block(i * block_size, HEIGHT - floor_level, block_size)
              for i in range(400)]
    floor2 = [Block2((i * block_size), HEIGHT - 70, block_size)
              for i in range(400)] 
    floor3 = [Block2((i * block_size) - 50, HEIGHT - 40, block_size)
              for i in range(400)] 
    floor4 = [Block2((i * block_size), HEIGHT - 10, block_size)
              for i in range(400)] 
    
    objects = [ *floor, *floor2, *floor3, *floor4]
    
    offset_x = 0
    scroll_area_width = 10

    run = True
    while run:
        clock.tick(FPS)

        draw_bg()

        if pygame.sprite.collide_rect(enemy, player):
                player.get_damage(.5)
        elif pygame.sprite.collide_rect(health, player):
                player.get_health(1)
        elif pygame.sprite.spritecollideany(enemy, bullet):
                enemy.get_damage(20)
                for b in bullet:
                    b.kill()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
                elif event.key == pygame.K_SPACE:
                    bullet_group.add(player.create_bullet())

                

        player.loop(FPS)
        enemy.loop(FPS)
        handle_move(player, enemy, objects, scroll)
        bullet.draw(window)
        bullet_group.update()
        draw(window, player, objects, offset_x, enemy, health)

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0 and scroll < 1500):
            offset_x += player.x_vel
            scroll += 2
        elif ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 and scroll > 0):
            offset_x += player.x_vel
            scroll -= 2

        if player.health == 0:
            break


    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)