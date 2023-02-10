import pygame

WIDTH, HEIGHT = 900, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

WHITE = (255,255,255)

FPS = 60

PLAYER = pygame.image.load("assets/player.png")

def draw_window():
    WINDOW.fill(WHITE)
    WINDOW.blit(PLAYER, (0,0))
    pygame.display.update()

def main():
    clock = pygame.time.Clock()

    carryOn = True
    while carryOn:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False

        draw_window()

    pygame.quit()

if __name__ == "__main__":
    main()