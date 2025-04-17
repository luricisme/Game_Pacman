import pygame
import sys
import copy
import global_var
from ui import *
from pacman import Pacman
from ghost import Ghost
from read_map import *

# Khởi tạo pygame
pygame.init()

# Cài đặt màn hình
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Font chữ
title_font = pygame.font.Font('freesansbold.ttf', 70)
title_font_sm = pygame.font.Font('freesansbold.ttf', 50)
menu_font = pygame.font.Font('freesansbold.ttf', 30)
instruction_font = pygame.font.Font('freesansbold.ttf', 35)
score_font = pygame.font.Font('freesansbold.ttf', 25)
backmenu_font = pygame.font.Font('freesansbold.ttf', 18)

# Tải hình ảnh
ghost_imgs = {
    "red_ghost": pygame.transform.scale(pygame.image.load('./assets/ghosts/red.png'), (45, 45)),
    "pink_ghost": pygame.transform.scale(pygame.image.load('./assets/ghosts/pink.png'), (45, 45)),
    "blue_ghost": pygame.transform.scale(pygame.image.load('./assets/ghosts/blue.png'), (45, 45)),
    "orange_ghost": pygame.transform.scale(pygame.image.load('./assets/ghosts/orange.png'), (45, 45)),
}
spooked_img = pygame.transform.scale(pygame.image.load('./assets/ghosts/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load('./assets/ghosts/dead.png'), (45, 45))
pacman_img = pygame.transform.scale(pygame.image.load('./assets/pacman/1.png'), (45, 45))

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def draw_diamonds_fadeout(surface, x, y, sz):
    # Blinking diamond effect
    size = sz
    time_now = pygame.time.get_ticks()

    # Tạo độ mờ dao động theo thời gian (dạng sin hoặc tam giác)
    # Fade chu kỳ 1000ms (1s)
    alpha = abs(255 * ((time_now % 1000) - 500) / 500)
    alpha = int(alpha)

    # Tạo surface riêng có hỗ trợ alpha
    diamond_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
    diamond_color = (*LIGHT_PURPLE, alpha)  # RGB + alpha

    points = [
        (size + 1, 1),               # Top
        (size * 2 + 1, size + 1),    # Right
        (size + 1, size * 2 + 1),    # Bottom
        (1, size + 1)                # Left
    ]

    pygame.draw.polygon(diamond_surf, diamond_color, points)
    surface.blit(diamond_surf, (x - size, y - size))

def draw_diamonds_changecolor(surface, x, y, sz):
    # Blinking diamond effect
    size = sz
    time_now = pygame.time.get_ticks()

    # Mỗi 500ms thì đổi màu
    if (time_now // 500) % 2 == 0:
        diamond_color = LIGHT_PURPLE
    else:
        diamond_color = WHITE  # Hoặc BLACK, hoặc một màu gì nổi hơn

    points = [
        (x, y - size),     # Top
        (x + size, y),     # Right
        (x, y + size),     # Bottom
        (x - size, y)      # Left
    ]

    pygame.draw.polygon(surface, diamond_color, points)

def main_menu():
    """Màn hình menu chính"""
    while True:
        screen.fill(DARK_PURPLE)
        draw_diamonds_changecolor(screen, 590, 255, 4)
        draw_diamonds_fadeout(screen, 300, 230, 5)
        draw_diamonds_changecolor(screen, 100, 200, 10)
        draw_diamonds_changecolor(screen, 770, 40, 11)
        draw_diamonds_changecolor(screen, 140, 450, 7)
        draw_diamonds_changecolor(screen, 100, 200, 10)
        draw_diamonds_fadeout(screen, 830, 150, 6)
        draw_diamonds_changecolor(screen, 750, 820, 10)
        draw_diamonds_fadeout(screen, 50, 80, 5)
        draw_diamonds_changecolor(screen, 100, 850, 11)
        draw_diamonds_fadeout(screen, 290, 890, 4)
        draw_diamonds_fadeout(screen, 850, 900, 7)
        draw_diamonds_changecolor(screen, 855, 500, 9)
        draw_diamonds_fadeout(screen, 720, 600, 4)
        draw_diamonds_fadeout(screen, 180, 710, 4)
        
        # Vẽ tiêu đề
        draw_text('PACMAN GAME', title_font, PURPLE, screen, WIDTH//2, 100)
        draw_text('GROUP 3', title_font_sm, LIGHT_PURPLE, screen, WIDTH//2, 190)
        
        # Vẽ các lựa chọn level
        level_buttons = []
        base_y = 300
        gap = 85
        
        colors = [
            (BLUE, DARK_BLUE, 'Level 1 - Blue Ghost'),
            (PINK, DARK_PINK, 'Level 2 - Pink Ghost'),
            (ORANGE, BROWN, 'Level 3 - Orange Ghost'),
            (RED, LIGHT_RED, 'Level 4 - Red Ghost'),
            (WHITE, BLACK, 'Level 5 - All Ghosts'),
            (TEAL, DARK_TEAL, 'Level 6 - Pacman Mode')
        ]
        
        for idx, (bg_color, text_color, label) in enumerate(colors):
            y_pos = base_y + idx * gap
            width = 450 if idx in [2, 5] else 400
            pygame.draw.rect(screen, bg_color, [WIDTH//2 - width // 2, y_pos, width, 55], 0, 10)
            draw_text(label, menu_font, text_color, screen, WIDTH//2, y_pos + 30)
            level_buttons.append(pygame.Rect(WIDTH//2 - 200, y_pos, 400, 55))  # Button hitbox

        # Vẽ nút Exit
        exit_button_rect = pygame.Rect(WIDTH//2 - 75, base_y + 6 * gap + 30, 150, 50)
        pygame.draw.rect(screen, GREY, exit_button_rect, 0, 10)
        draw_text('Exit', menu_font, DARK_PURPLE, screen, WIDTH//2, base_y + 6 * gap + 55)
        
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                for i, button in enumerate(level_buttons):
                    if button.collidepoint(mouse_pos):
                        return i + 1  # Trả về level được chọn (1-6)

                if exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def run_game(level):
    # Khởi động bàn cờ
    if level == 6: # Bàn cờ đầy đủ
        level_data = copy.deepcopy(boards)
    else:
        level_data = copy.deepcopy(board_only_ghost)

    ghost_speed = 2
    # Màu sắc cho từng level
    level_colors = {
        1: 'mediumblue',
        2: 'deeppink',
        3: 'orangered',
        4: 'firebrick',
        5: 'slategray',
        6: 'teal'
    }
    board_color = level_colors.get(level, 'darkmagenta')  # màu mặc định nếu không tìm thấy

    graph = extract_graph(level_data)
    
    # Game state
    # (800, 50), (450, 663), (800, 800), (200, 300), (50, 800)
    player = Pacman(800, 50)
    # player = Pacman(450, 663)
    # player = Pacman(800, 800)
    # player = Pacman(200, 300)
    # player = Pacman(50, 800)
    run = True
    
    # Mảng chứa ghosts
    ghosts = []
    # Target mặc định là vị trí bắt đầu của pacman
    targets = [(450, 663), (450, 663), (450, 663), (450, 663)] 

    # Thêm ghost vào dựa vào từng level
    if level == 1:  
        print("---------------\nLevel 1")
        # Blue Ghost
        ghosts.append(Ghost('blue', 428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level_data, spooked_img, dead_img))
    elif level == 2:  
        print("---------------\nLevel 2")
        # Pink Ghost
        ghosts.append(Ghost('pink', 428, 386, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level_data, spooked_img, dead_img))
    elif level == 3:  
        print("---------------\nLevel 3")
        # Orange Ghost
        ghosts.append(Ghost('orange', 428, 386, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level_data, spooked_img, dead_img))
    elif level == 4:  
        print("---------------\nLevel 4")
        # Red Ghost
        ghosts.append(Ghost('red', 428, 386, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level_data, spooked_img, dead_img))
    elif level == 5:  # All Ghosts
        print("---------------\nLevel 5")
        ghosts = [
            Ghost('red', 478, 436, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level_data, spooked_img, dead_img, spawn_delay=0),
            Ghost('pink', 428, 436, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level_data, spooked_img, dead_img, spawn_delay=0),
            Ghost('blue', 428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level_data, spooked_img, dead_img, spawn_delay=0),
            Ghost('orange', 378, 436, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level_data, spooked_img, dead_img, spawn_delay=0),
        ]
    elif level == 6:  # Pacman Mode (Pacman tránh ma)
        print("---------------\nLevel 6")
        ghosts = [
            Ghost('red', 478, 436, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level_data, spooked_img, dead_img, spawn_delay=0),
            Ghost('pink', 428, 436, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level_data, spooked_img, dead_img, spawn_delay=0),
            Ghost('blue', 428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level_data, spooked_img, dead_img, spawn_delay=0),
            Ghost('orange', 378, 436, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level_data, spooked_img, dead_img, spawn_delay=0),
        ]
    
    def draw_board():
        num1 = TILE_HEIGHT
        num2 = TILE_WIDTH
        for i in range(len(level_data)):
            for j in range(len(level_data[i])):
                x = j * num2 + (0.5 * num2)
                y = i * num1 + (0.5 * num1)
                tile = level_data[i][j]
                if tile == 1:
                    pygame.draw.circle(screen, 'white', (x, y), 4)
                elif tile == 2 and not player.flicker:
                    pygame.draw.circle(screen, 'white', (x, y), 10)
                elif tile == 3:
                    pygame.draw.line(screen, board_color, (x, y - 0.5 * num1), (x, y + 0.5 * num1), 3)
                elif tile == 4:
                    pygame.draw.line(screen, board_color, (x - 0.5 * num2, y), (x + 0.5 * num2, y), 3)
                elif tile == 5:
                    pygame.draw.arc(screen, board_color, [x - 0.9 * num2, y, num2, num1], 0, 0.5 * 3.14, 3)
                elif tile == 6:
                    pygame.draw.arc(screen, board_color, [x, y, num2, num1], 0.5 * 3.14, 3.14, 3)
                elif tile == 7:
                    pygame.draw.arc(screen, board_color, [x, y - 0.9 * num1, num2, num1], 3.14, 4.71, 3)
                elif tile == 8:
                    pygame.draw.arc(screen, board_color, [x - 0.9 * num2, y - 0.9 * num1, num2, num1], 4.71, 6.28, 3)
                elif tile == 9:
                    pygame.draw.line(screen, 'white', (x - 0.5 * num2, y), (x + 0.5 * num2, y), 3)

    def draw_misc():
        # Hiển thị số điểm và thông tin khác
        score_text = score_font.render(f"Score: {player.score}", True, 'white')
        # level_text = score_font.render(f"Level: {level}", True, 'white')
        screen.blit(score_text, (300, 920))
        # screen.blit(level_text, (300, 920))
        
    
    def back_menu():
        level_text = score_font.render(f"Level: {level}", True, 'white')
        menu_text = backmenu_font.render("Press ESC to return to Menu", True, 'white')
        screen.blit(level_text, (30, 920))
        screen.blit(menu_text, (620, 922))

    def draw_misc():
        # Hiển thị số điểm và thông tin khác
        score_text = score_font.render(f"Score: {player.score}", True, 'white')
        level_text = score_font.render(f"Level: {level}", True, 'white')
        screen.blit(score_text, (30, 920))
        screen.blit(level_text, (300, 920))
        
        if  global_var.powerup:
            pygame.draw.circle(screen, 'blue', (550, 930), 15)

    # Game loop
    while run:
        clock.tick(FPS)

        if player.counter < 19:
            player.counter += 1
            if player.counter > 2:
                player.flicker = False
        else:
            player.counter = 0
            player.flicker = True
        
        screen.fill('black')
        draw_board()
        back_menu()
        
        # Hiện lên player
        player.draw(screen)
        player_rect = pygame.Rect(player.x, player.y, 40, 40)
        status_set = set()
        # Hiện lên ghost tương ứng với từng level
        for ghost in ghosts:
            ghost.rect = ghost.draw()
            ghost.start_pathfinding(player.get_position(), graph, player, status_set)
            print("PLAYER RECT: ", player_rect)
            print("GHOST RECT: ", ghost.rect)
            print("COLLIDE: ", player_rect.colliderect(ghost.rect))
            if global_var.powerup and player_rect.colliderect(ghost.rect) and not ghost.dead and not player.eaten_ghosts[ghost.id]:
                ghost.dead = True
                player.eaten_ghosts[ghost.id] = True

        if level == 6:
            # print("LEVEL 06 LOGIC CODE")
            if global_var.powerup and player.power_counter < 200:
                player.power_counter += 1
            elif  global_var.powerup and player.power_counter >= 200:
                player.power_counter = 0
                global_var.powerup = False
                player.eaten_ghost = [False, False, False, False, False]
            
            if player.startup_counter < 50:
                player.moving = False
                player.startup_counter += 1
            else:
                player.moving = True

            player.turns_allowed = player.check_position(level_data)
            if player.moving:
                player.move()
            player.check_collisions(level_data)
            draw_misc()

            key_press = pygame.key.get_pressed()
            if key_press[pygame.K_RIGHT]:
                player.direction_command = 0
            elif key_press[pygame.K_LEFT]:
                player.direction_command = 1
            if key_press[pygame.K_UP]:
                player.direction_command = 2
            elif key_press[pygame.K_DOWN]:
                player.direction_command = 3

            if player.x > 900:
                player.x = -47
            elif player.x < -50:
                player.x = 897

            for i in range(4):
                if player.direction_command == i and player.turns_allowed[i]:
                    player.direction = i

        if not player.isLive:
            run = False
            continue
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Quay lại menu chính
        pygame.display.flip()

    # Kết thúc game
    screen.fill(DARK_PURPLE)
    draw_text('GAME OVER', title_font, RED, screen, WIDTH//2, HEIGHT//2 - 50)
    draw_text(f'Score: {player.score}', menu_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 50)
    draw_text('Press ESC to return to Menu', menu_font, WHITE, screen, WIDTH//2, HEIGHT//2 + 100)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Trở về menu khi nhấn ESC
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    run_game(level)
    return  # Trở về menu khi kết thúc

# Game loop chính
def main():
    while True:
        level = main_menu()
        run_game(level)

if __name__ == "__main__":
    main()