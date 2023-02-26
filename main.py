import pygame, random, math, os
from os import listdir
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
    path = join("assets", "Terrain", "IndustrialTile_72.png")
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
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

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

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= 1
    

    def update_sprite(self):
        keys = pygame.key.get_pressed()
        sprite_sheet = "Cyborg_idle"
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
        elif keys [pygame.K_9]:
            sprite_sheet = "Angry"
        elif keys [pygame.K_k]:
            sprite_sheet = "Cyborg_punch"
        elif keys [pygame.K_j]:
            sprite_sheet = "Cyborg_attack3"
        

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
    
    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

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

class Enemy(Object):
    ANIMATION_DELAY = 4
    def __init__(self, x, y, width, height, end):
        self.vel = 2
        self.x = x
        self.y = y
        self.path = [x, end]
        
        super().__init__(x, y, width, height, "enemy")
        self.ENEMY = load_sprite_sheets("Characters", "Enemy", 48, 48)
        self.image = self.ENEMY["Punk_idle"][0]
        self.direction = "left"
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation = "Punk_idle"

    def active(self):
            pass
        
    def loop(self):
        sprites = self.ENEMY[self.animation]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def draw(window, player, objects,offset_x, enemy):
    

    for obj in objects:
        obj.draw(window, offset_x)

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
            

def handle_move(player, objects, scroll):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_a] and player.rect.x > 0:
        player.move_left(PLAYER_VEL)
        scroll -= 5
    elif keys[pygame.K_d] and player.rect.x < 1500:
        player.move_right(PLAYER_VEL)
        scroll += 5
        

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

    enemy_pos = HEIGHT - floor_level - 96


    player = Player(WIDTH / 2, HEIGHT - floor_level - 2, 48, 48)
    enemy = Enemy(100, enemy_pos, 48, 48, 450)
    enemy.active()
    floor = [Block(i * block_size, HEIGHT - floor_level, block_size)
              for i in range(1000)]
    floor2 = [Block2((i * block_size) + 80, HEIGHT - floor_level * 2.5, block_size)
              for i in range(10)] 
    floor3 = [Block2((i * block_size) + 420, HEIGHT - floor_level * 4, block_size)
              for i in range(15)]
    floor4 = [Block2((i * block_size) + 1000, HEIGHT - floor_level * 4, block_size)
              for i in range(10)]
    floor5 = [Block2((i * block_size) + 1400, HEIGHT - floor_level * 3, block_size)
              for i in range(10)] 
    
    objects = [*floor, *floor2, *floor3, *floor4, *floor5]
    
    offset_x = 0
    scroll_area_width = 10

    run = True
    while run:
        clock.tick(FPS)

        draw_bg()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        enemy.loop()
        handle_move(player, objects, scroll)
        draw(window, player, objects, offset_x, enemy)

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0 and scroll < 1500):
            offset_x += player.x_vel
            scroll += 2
        elif ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0 and scroll > 0):
            offset_x += player.x_vel
            scroll -= 2

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)