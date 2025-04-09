import pygame
import sys
from ui import *
from pacman import Pacman
from ghost import Ghost
from read_map import *
# Khởi tạo pygame
pygame.init()
# 5 Vị trí bắt đầu của Pacman
player_pos = [(2, 5), (30, 22), (20, 22), (27, 12), (2, 27), (15, 25)]
# Cài đặt màn hình
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Font chữ
title_font = pygame.font.Font('freesansbold.ttf', 70)
menu_font = pygame.font.Font('freesansbold.ttf', 40)
instruction_font = pygame.font.Font('freesansbold.ttf', 35)
score_font = pygame.font.Font('freesansbold.ttf', 25)
backmenu_font = pygame.font.Font('freesansbold.ttf', 18)

# Tải hình ảnh
ghost_imgs = {
    "red_ghost": pygame.transform.scale(pygame.image.load('Source/assets/ghosts/red.png'), (45, 45)),
    "pink_ghost": pygame.transform.scale(pygame.image.load('Source/assets/ghosts/pink.png'), (45, 45)),
    "blue_ghost": pygame.transform.scale(pygame.image.load('Source/assets/ghosts/blue.png'), (45, 45)),
    "orange_ghost": pygame.transform.scale(pygame.image.load('Source/assets/ghosts/orange.png'), (45, 45)),
}
spooked_img = pygame.transform.scale(pygame.image.load('Source/assets/ghosts/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load('Source/assets/ghosts/dead.png'), (45, 45))
pacman_img = pygame.transform.scale(pygame.image.load('Source/assets/pacman/1.png'), (45, 45))

def draw_text(text, font, color, surface, x, y):
    """Vẽ text lên màn hình tại tọa độ x, y"""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def main_menu():
    """Màn hình menu chính"""
    while True:
        screen.fill(BLACK)
        
        # Vẽ tiêu đề
        draw_text('PAC-MAN', title_font, YELLOW, screen, WIDTH//2, 150)
        
        # Vẽ hướng dẫn
        draw_text('MENU', instruction_font, WHITE, screen, WIDTH//2, 250)
        
        # Vẽ các lựa chọn level
        level_buttons = []
        
        # Level 1 - Blue Ghost
        pygame.draw.rect(screen, BLUE, [WIDTH//2 - 225, 320, 450, 70], 0, 10)
        draw_text('Level 1 - Blue Ghost', menu_font, WHITE, screen, WIDTH//2, 355)
        level_buttons.append(pygame.Rect(WIDTH//2 - 200, 320, 400, 70))
        
        # Level 2 - Pink Ghost
        pygame.draw.rect(screen, PINK, [WIDTH//2 - 225, 420, 450, 70], 0, 10)
        draw_text('Level 2 - Pink Ghost', menu_font, BLACK, screen, WIDTH//2, 455)
        level_buttons.append(pygame.Rect(WIDTH//2 - 200, 420, 400, 70))
        
        # Level 3 - Orange Ghost
        pygame.draw.rect(screen, ORANGE, [WIDTH//2 - 250, 520, 500, 70], 0, 10)
        draw_text('Level 3 - Orange Ghost', menu_font, BLACK, screen, WIDTH//2, 555)
        level_buttons.append(pygame.Rect(WIDTH//2 - 200, 520, 400, 70))
        
        # Level 4 - Red Ghost
        pygame.draw.rect(screen, RED, [WIDTH//2 - 225, 620, 450, 70], 0, 10)
        draw_text('Level 4 - Red Ghost', menu_font, WHITE, screen, WIDTH//2, 655)
        level_buttons.append(pygame.Rect(WIDTH//2 - 200, 620, 400, 70))
        
        # Level 5 - All Ghosts
        pygame.draw.rect(screen, WHITE, [WIDTH//2 - 225, 720, 450, 70], 0, 10)
        draw_text('Level 5 - All Ghosts', menu_font, BLACK, screen, WIDTH//2, 755)
        level_buttons.append(pygame.Rect(WIDTH//2 - 200, 720, 400, 70))

        # Level 6 - Pacman Mode
        pygame.draw.rect(screen, YELLOW, [WIDTH//2 - 250, 820, 500, 70], 0, 10)
        draw_text('Level 6 - Pacman Mode', menu_font, BLACK, screen, WIDTH//2, 855)
        level_buttons.append(pygame.Rect(WIDTH//2 - 200, 820, 400, 70))
        
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Kiểm tra xem người dùng đã nhấp vào nút nào
                for i, button in enumerate(level_buttons):
                    if button.collidepoint(mouse_pos):
                        return i + 1  # Trả về level được chọn (1-6)
        
        pygame.display.flip()
        clock.tick(FPS)

def run_game(level):
    """Khởi động trò chơi với level được chọn"""
    # Constants
    if level == 6:
        level_data = boards
    else:
        level_data = board_only_ghost
    score = 0
    powerup = False
    power_counter = 0
    eaten_ghosts = [False, False, False, False]
    startup_counter = 0
    moving = True
    counter = 0
    lives = 3
    ghost_speed = 2
    graph = extract_graph(level_data)
    

    # Game state
    player = None
    player = Pacman(450, 663)  # Chỉ tạo pacman cho level 6
    counter = 0
    flicker = False
    run = True
    
    # Khởi tạo ghost dựa vào level
    targets = [(450, 663), (450, 663), (450, 663), (450, 663)]  # Target mặc định là vị trí bắt đầu của pacman
    ghosts = []
    
    if level == 1:  
        print("---------------\nLevel 1")
        # Blue Ghost
        ghosts.append(Ghost(428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img))
    elif level == 2:  
        print("---------------\nLevel 2")
        # Pink Ghost
        ghosts.append(Ghost(428, 386, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img))
    elif level == 3:  
        print("---------------\nLevel 3")
        # Orange Ghost
        ghosts.append(Ghost(428, 386, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img))
    elif level == 4:  
        print("---------------\nLevel 4")
        # Red Ghost
        ghosts.append(Ghost(428, 386, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img))
    elif level == 5:  # All Ghosts
        ghosts = [
            Ghost(478, 436, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
            Ghost(428, 436, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
            Ghost(428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
            Ghost(378, 436, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
        ]
    elif level == 6:  # Pacman Mode (Pacman tránh ma)
        # Mặc định là cả 4 ma, với mode đặc biệt nếu cần
        ghosts = [
            Ghost(478, 436, targets[0], ghost_speed, ghost_imgs["red_ghost"], 0, False, True, 0, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
            Ghost(428, 436, targets[1], ghost_speed, ghost_imgs["pink_ghost"], 0, False, True, 1, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
            Ghost(428, 386, targets[2], ghost_speed, ghost_imgs["blue_ghost"], 0, False, True, 2, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
            Ghost(378, 436, targets[3], ghost_speed, ghost_imgs["orange_ghost"], 0, False, True, 3, screen, level_data, eaten_ghosts, powerup, spooked_img, dead_img),
        ]
        # Có thể thêm logic đặc biệt cho level 6 ở đây
    
    def draw_board():
        num1 = TILE_HEIGHT
        num2 = TILE_WIDTH
        color = 'darkmagenta'
        for i in range(len(level_data)):
            for j in range(len(level_data[i])):
                x = j * num2 + (0.5 * num2)
                y = i * num1 + (0.5 * num1)
                tile = level_data[i][j]
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
        
        if powerup:
            pygame.draw.circle(screen, 'blue', (550, 930), 15)
        
        # Hiển thị số mạng
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
        
        if level == 1:
            # pacman đứng yên và blue ghost di chuyển
            if player:
                player.x = int((player_pos[0][1] - 0.5) * TILE_WIDTH) 
                player.y = int((player_pos[0][0] - 0.5) * TILE_HEIGHT)
                player.check_position(level_data)
                player.direction_command = 0
                player.move([False, False, False, False])
                player.draw(screen)
                
                
            # Xử lý ma di chuyển
            for ghost in ghosts:
                ghost.powerup = False
                ghost.eaten_ghost = [False, False, False, False]
                ghost.draw()
                if ghost.move_blue(player.get_position(), graph=graph):
                    ghost.draw()
                    ghost.check_collisions()    
                else:
                    continue
                    

        if level == 2:
            # pacman đứng yên và pink ghost di chuyển
            if player:
                player.x = int((player_pos[0][1] - 0.5) * TILE_WIDTH) 
                player.y = int((player_pos[0][0] - 0.5) * TILE_HEIGHT) 
                player.check_position(level_data)
                player.move([False, False, False, False])
                player.draw(screen)
            # Xử lý ma di chuyển
            for ghost in ghosts:
                ghost.powerup = False
                ghost.eaten_ghost = [False, False, False, False]
                ghost.draw()
                if ghost.move_pink(player.get_position(), graph=graph):
                    ghost.draw()
                    ghost.check_collisions()
                else:
                    continue


        # Xử lý pacman và powerup chỉ khi level 6
        if level == 6 and player:
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
    
        if level == 6 and player:
            player.counter = counter
        
        screen.fill('black')
        draw_board()

        back_menu()
        # Vẽ và xử lý pacman chỉ khi level 6
        if level == 6 and player:
            player.draw(screen)
            turns_allowed = player.check_position(level_data)
            if moving:
                player.move(turns_allowed)
            player.score, player.powerup, player.power_counter, player.eaten_ghosts = player.check_collisions(level_data)
            draw_misc()
            turns_allowed = player.check_position(level_data)
            if moving:
                player.move(turns_allowed)
            player.score, player.powerup, player.power_counter, player.eaten_ghosts = player.check_collisions(level_data)
    
        for ghost in ghosts:
            if level == 6 and player:
                ghost.powerup = player.powerup
                ghost.eaten_ghost = player.eaten_ghosts

            ghost.draw()
            
            # Thêm logic di chuyển ma tương ứng với từng loại ma
            if ghost.id == 0:  # Red ghost
                pass  # ghost.move_red()
            elif ghost.id == 1:  # Pink ghost
                ghost.move_pink(player.get_position(), graph=graph)
            elif ghost.id == 2:  # Blue ghost
                ghost.move_blue(player.get_position(), graph=graph)
            elif ghost.id == 3:  # Orange ghost
                pass  # ghost.move_orange()
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # run = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.direction = 0
                elif event.key == pygame.K_LEFT:
                    player.direction = 1
                elif event.key == pygame.K_UP:
                    player.direction = 2
                elif event.key == pygame.K_DOWN:
                    player.direction = 3
                elif event.key == pygame.K_ESCAPE:
                    return
            
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
        if level == 6 and player:
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
        #xử lý pacman đụng phải ghost
        if level == 6 and player:
            for ghost in ghosts:
                if player.get_position() == ghost.get_map_position():
                    if player.powerup:
                        ghost.in_box = True
                        ghost.dead = True
                        player.score += 200
                        eaten_ghosts[ghost.id] = True
                    else:
                        lives -= 1
                        if lives <= 0:
                            run = False
                            break
        else:
            for ghost in ghosts:
                if player.get_position() == ghost.get_map_position():                    
                    lives -= 1
                    if lives <= 0:
                        run = False
                        break
        pygame.display.flip()
    # Kết thúc game
    screen.fill(BLACK)
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