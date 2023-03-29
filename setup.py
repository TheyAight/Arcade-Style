import pygame, random, math, os
from os import listdir
import time
from os.path import isfile, join
from pygame import mixer
pygame.init()

WIDTH, HEIGHT = 1324, 745

pygame.display.set_caption("Arcade Style")

mixer.music.load('assets/Music/bgmusic.mp3')
mixer.music.play(-1)

smallfont = pygame.font.SysFont("comicsansms", 25)

BG_COLOR = (255, 255, 255)

FPS = 60 
PLAYER_VEL = 8
ENEMY_VEL = 2

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
        self.score = 0

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
        
    def create_enemy(self):
        x_placement = random.randint(20, 1260)
        return Enemy(x_placement, HEIGHT - 196, 48, 48)
        
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
        elif keys [pygame.K_SPACE] and not self.hit:
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
        self.health = 60
        self.hit = False
        self.hit_count = 0
        self.life = True
        self.deathani = 0
        self.image = pygame.image.load("assets/Objects/blankimage.png")

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
    
    def update(self, win, offset_x, player):
        self.move(self.x_vel)

        if self.rect.x < -10 or self.rect.x < player.rect.x:
            self.move_right(ENEMY_VEL)
        elif self.rect.x > 1260 or self.rect.x > player.rect.x:
            self.move_left(ENEMY_VEL)
        elif self.rect.x == player.rect.x and self.direction == 'right' and player.hit:
            self.rect.x = self.rect.x -70
        elif self.rect.x == player.rect.x and self.direction == 'left' and player.hit:
            self.rect.x = self.rect.x + 70

        if self.hit:
            self.hit_count += 1
        if self.hit_count > 60 * .3:
            self.hit = False
        
        image = "Walk_attack"

        if self.hit and not self.health <= 0:
            image = "Punk_hurt"
        elif self.health <= 0:
            image = "death"

        
        sprite_sheet_name = image + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

        if self.health <= 0:
            if sprite_index == 6:
                player.score += 2
                self.kill()

        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

def score(score, win):
    text = smallfont.render("Score: "+str(score), True, BG_COLOR)
    win.blit(text, [10, 50])

def end_score(score, win):
    text = smallfont.render("Score: "+str(score), True, (0, 0, 0))
    win.blit(text, [600, 600])

def draw(window, player, objects,offset_x):
    

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    score(player.score, window)
    
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
            
def handle_move(player, objects):
    keys = pygame.key.get_pressed()


    player.x_vel = 0
    if keys[pygame.K_a] and player.rect.x > 0:
        player.move_left(PLAYER_VEL)
    elif keys[pygame.K_d] and player.rect.x < 1250:
        player.move_right(PLAYER_VEL)



        
    handle_vertical_collison(player, objects, player.y_vel)


def play(window):
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

    enemy_group = pygame.sprite.Group()
    enemies = enemy_group

    player = Player(WIDTH / 2, HEIGHT - floor_level - 2, 48, 48)
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

    enemy_delay = 4000 # 4 seconds
    enemy_event = pygame.USEREVENT + 1
    pygame.time.set_timer(enemy_event, enemy_delay)

    player_delay = 30000 # 30 seconds
    player_event = pygame.USEREVENT + 2
    pygame.time.set_timer(player_event, player_delay)

    run = True
    while run:
        clock.tick(FPS)

        draw_bg()
        
        for e in enemies:
            if pygame.sprite.spritecollideany(e , bullet):
                if e.health > 0:
                    e.get_damage(20)
        for b in bullet:
            if pygame.sprite.spritecollideany(b , enemies):
                    b.kill()
        if pygame.sprite.spritecollideany(player, enemies) and player.y_vel == 0:
            player.get_damage(.003)
            

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
                elif event.key == pygame.K_SPACE and player.x_vel == 0 and not player.hit:
                    bullet_group.add(player.create_bullet())
                    path = join('assets', 'SFX', 'cannon_x.wav')
                    impact = mixer.Sound(path)
                    impact.play()
            if event.type == enemy_event:
                enemy_group.add(player.create_enemy())
                enemy_group.add(player.create_enemy())
                enemy_group.add(player.create_enemy())
            if event.type == player_event:
                player.score += 8
                if player.health < player.maximum_health:
                    player.health += 20

                
        if player.health == 0:
            end_menu(window, player)
            run = False

        player.loop(FPS)
        handle_move(player, objects)
        bullet.draw(window)
        bullet_group.update()
        enemies.draw(window)
        enemy_group.update(window, offset_x, player)
        draw(window, player, objects, offset_x)


    pygame.quit()
    quit()

def end_menu(window, player):

    end_src = pygame.image.load("assets\Background\endscreen.png").convert_alpha()

    def draw_end():
        
        window.blit(end_src, (0,0))

    run = True
    while run:

        window.fill((225, 0, 0))

        draw_end()

        end_score(player.score, window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                    break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    play(window)
                    run = False

        pygame.display.update()

    pygame.quit()
    quit()

def main_menu(window):

    menu_scr = pygame.image.load("assets\Background\Mainmenu.png").convert_alpha()

    def draw_menu():
        window.blit(menu_scr, (0, 0))

    

    run = True
    while run:
        window.fill((225, 0, 0))

        draw_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play(window)
                    run = False

        pygame.display.update()

    pygame.quit()
    quit()

main_menu(window)