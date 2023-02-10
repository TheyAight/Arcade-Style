import pygame

WIDTH, HEIGHT = 900, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LEG DAY")

WHITE = (255,255,255)
BLUE = (0, 0, 225)
GRAY = (220, 220, 220)

BORDER = pygame.Rect(0, HEIGHT - 20, WIDTH, 30)

FPS = 60
VEL = 10

PWIDTH , PHEIGHT = 62, 62

PLAYER = pygame.image.load("assets/player.png")
PLYR = pygame.transform.scale(PLAYER, (PWIDTH, PHEIGHT))

def draw_window(play):
    WINDOW.fill(GRAY)
    pygame.draw.rect(WINDOW, BLUE, BORDER)
    WINDOW.blit(PLYR, (play.x, play.y))
    pygame.display.update()

def player_handle_movement(keys_pressed, play):
    if keys_pressed[pygame.K_LEFT] and play.x - VEL + 13 > 0:
        play.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and play.x + VEL + play.width - 12 < WIDTH:
        play.x += VEL
    if keys_pressed[pygame.K_UP] and play.y - VEL + 13 > 0:
        play.y -= VEL
    if keys_pressed[pygame.K_DOWN] and play.y + VEL + play.height - 12 < BORDER.y:
        play.y += VEL

def main():
    play = pygame.Rect(100, 300, PWIDTH, PHEIGHT)

    clock = pygame.time.Clock()

    carryOn = True
    while carryOn:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False

        keys_pressed = pygame.key.get_pressed()
        player_handle_movement(keys_pressed, play)
        draw_window(play)

    pygame.quit()

if __name__ == "__main__":
    main()