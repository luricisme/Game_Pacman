import pygame
from ui import boards
from pacman import Pacman
from ghost import Ghost

pygame.init()

# Constants
WIDTH = 900
HEIGHT = 950
FPS = 80

# Setup
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Pac-Man")
font = pygame.font.Font('freesansbold.ttf', 20)
clock = pygame.time.Clock()
level = boards
score = 0
powerup = False
power_counter = 0
eaten_ghosts = [False, False, False, False]
startup_counter = 0
moving = True
counter = 0
lives = 3
ghost_speed = 2

# Load images
ghost_imgs = {
    "red_ghost": pygame.transform.scale(pygame.image.load('assets/ghosts/red.png'), (45, 45)),
    "pink_ghost": pygame.transform.scale(pygame.image.load('assets/ghosts/pink.png'), (45, 45)),
    "blue_ghost": pygame.transform.scale(pygame.image.load('assets/ghosts/blue.png'), (45, 45)),
    "orange_ghost": pygame.transform.scale(pygame.image.load('assets/ghosts/orange.png'), (45, 45)),
}
spooked_img = pygame.transform.scale(pygame.image.load('assets/ghosts/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load('assets/ghosts/dead.png'), (45, 45))

# Game state
player = Pacman(450, 663)
counter = 0
flicker = False
run = True

targets = [(player.x, player.y), (player.x, player.y), (player.x, player.y), (player.x, player.y)]
ghosts = [
    Ghost(478, 436, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level, eaten_ghosts, powerup, spooked_img, dead_img),
    Ghost(428, 436, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level, eaten_ghosts, powerup, spooked_img, dead_img),
    Ghost(428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level, eaten_ghosts, powerup, spooked_img, dead_img),
    Ghost(378, 436, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level, eaten_ghosts, powerup, spooked_img, dead_img),
]

def draw_board():
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    color = 'darkmagenta'
    for i in range(len(level)):
        for j in range(len(level[i])):
            x = j * num2 + (0.5 * num2)
            y = i * num1 + (0.5 * num1)
            tile = level[i][j]
            if tile == 1:
                pygame.draw.circle(screen, 'white', (x, y), 4)
            elif tile == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (x, y), 10)
            elif tile == 3:
                pygame.draw.line(screen, color, (x, y - 0.5 * num1), (x, y + 0.5 * num1), 3)
            elif tile == 4:
                pygame.draw.line(screen, color, (x - 0.5 * num2, y), (x + 0.5 * num2, y), 3)
            elif tile == 5:
                pygame.draw.arc(screen, color, [x - 0.9 * num2, y, num2, num1], 0, 0.5 * 3.14, 3)
            elif tile == 6:
                pygame.draw.arc(screen, color, [x, y, num2, num1], 0.5 * 3.14, 3.14, 3)
            elif tile == 7:
                pygame.draw.arc(screen, color, [x, y - 0.9 * num1, num2, num1], 3.14, 4.71, 3)
            elif tile == 8:
                pygame.draw.arc(screen, color, [x - 0.9 * num2, y - 0.9 * num1, num2, num1], 4.71, 6.28, 3)
            elif tile == 9:
                pygame.draw.line(screen, 'white', (x - 0.5 * num2, y), (x + 0.5 * num2, y), 3)

def draw_misc():
    score_text = font.render(f"Score: {player.score}", True, 'white')
    screen.blit(score_text, (405, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player.images[0], (30, 30)), (650 + i * 40, 915))

# Game loop
while run:
    clock.tick(FPS)

    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    
    if player.powerup and player.power_counter < 600:
        player.power_counter += 1
    elif player.powerup and player.power_counter >= 600:
        player.power_counter = 0
        player.powerup = False
        player.eaten_ghosts = [False, False, False, False]
    
    if startup_counter < 180:
        moving = False
        startup_counter += 1
    else:
        moving = True

    player.counter = counter

    screen.fill('black')
    draw_board()
    player.draw(screen)
    draw_misc()
    turns_allowed = player.check_position(level)
    if moving:
        player.move(turns_allowed)
    player.score, player.powerup, player.power_counter, player.eaten_ghosts = player.check_collisions(level)

    for ghost in ghosts:
        ghost.powerup = player.powerup
        ghost.eaten_ghost = player.eaten_ghosts
        ghost.draw()
        # ghost.move_blue()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                player.direction = 0
            elif event.key == pygame.K_LEFT:
                player.direction = 1
            elif event.key == pygame.K_UP:
                player.direction = 2
            elif event.key == pygame.K_DOWN:
                player.direction = 3
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and player.direction_command == 0:
                player.direction_command = player.direction
            elif event.key == pygame.K_LEFT and player.direction_command == 1:
                player.direction_command = player.direction
            elif event.key == pygame.K_UP and player.direction_command == 2:
                player.direction_command = player.direction
            elif event.key == pygame.K_DOWN and player.direction_command == 3:
                player.direction_command = player.direction

    # Update direction if allowed
    if player.direction_command == 0 and turns_allowed[0]:
        player.direction = 0
    elif player.direction_command == 1 and turns_allowed[1]:
        player.direction = 1
    elif player.direction_command == 2 and turns_allowed[2]:
        player.direction = 2
    elif player.direction_command == 3 and turns_allowed[3]:
        player.direction = 3

    player.direction_command = -1

    # warp tunnel
    if player.x > WIDTH:
        player.x = -47
    elif player.x < -50:
        player.x = WIDTH - 3

    pygame.display.flip()

pygame.quit()
