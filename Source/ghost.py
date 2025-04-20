import pygame
import global_var
from ui import *
from levels.level01 import *
from levels.level02 import *

class Ghost:
    def __init__(self, type, x, y, speed, img, direct, dead, box, id, screen, level, spooked_img, dead_img, spawn_delay=0):
        self.type = type
        self.x_pos = y * TILE_WIDTH - TILE_WIDTH *0.3
        self.y_pos = x * TILE_HEIGHT - TILE_HEIGHT *0.3
        self.center_x = int(self.x_pos + 22)
        self.center_y = int(self.y_pos + 22)
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.screen = screen
        self.level = level
        self.spooked_img = spooked_img
        self.dead_img = dead_img
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()
        self.spawn_delay = spawn_delay
        self.delay_counter = 0
        self.path = []
    
    def start_pathfinding(self, player_pos, graph, player, status_set):
        if self.type == 'red':
            self.move_red(player_pos, graph, player, status_set)
        elif self.type == 'pink':
            self.move_pink(player_pos, graph, player, status_set)
        elif self.type == 'blue':
            self.move_blue(player_pos, graph, player, status_set)
        elif self.type == 'orange':
            self.move_orange(player_pos, graph, player, status_set)

    def draw(self):
        if (not global_var.powerup and not self.dead) or (global_var.eaten_ghosts[self.id] and global_var.powerup and not self.dead):
            self.screen.blit(self.img, (self.x_pos, self.y_pos))
        elif global_var.powerup and not self.dead and not global_var.eaten_ghosts[self.id]:
            self.screen.blit(self.spooked_img, (self.x_pos, self.y_pos))
        else:
            self.screen.blit(self.dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (36, 36))
        ghost_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (36, 36))
        return ghost_rect
    
    def get_map_position(self):
        return (int(self.y_pos + TILE_HEIGHT*0.3+1)//TILE_HEIGHT, int(self.x_pos + TILE_WIDTH*0.3 + 1)//TILE_WIDTH)

    def check_collisions(self):
        num1 = ((HEIGHT - 50) // 33)
        num2 = (WIDTH // 30)
        num3 = 13
        self.turns = [False, False, False, False]
        level = self.level

        if 0 < self.center_x // 30 <= 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 or (
                    level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 or (
                    level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 or (
                    level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 or (
                    level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[2] = True

        if self.direction == 2 or self.direction == 3:
            if 12 <= self.center_x % num2 <= 18:
                if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                        or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                        self.in_box or self.dead)):
                    self.turns[3] = True
                if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                        or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                        self.in_box or self.dead)):
                    self.turns[2] = True
            if 12 <= self.center_y % num1 <= 18:
                if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                        or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                        self.in_box or self.dead)):
                    self.turns[1] = True
                if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                        or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                        self.in_box or self.dead)):
                    self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_to_node(self, node):        
        node_x = node[1] * TILE_WIDTH - TILE_WIDTH *0.3
        node_y = node[0] * TILE_HEIGHT - TILE_HEIGHT *0.3
        # Di chuyển ghost đến vị trí của node
        if self.x_pos < node_x:            
            self.x_pos += self.speed
            if self.x_pos > node_x:
                self.x_pos = node_x
        elif self.x_pos > node_x:
            self.x_pos -= self.speed  
            if self.x_pos < node_x:
                self.x_pos = node_x      
        if self.y_pos < node_y:
            self.y_pos += self.speed
            if self.y_pos > node_y:
                self.y_pos = node_y
        elif self.y_pos > node_y:
            self.y_pos -= self.speed
            if self.y_pos < node_y:
                self.y_pos = node_y
        return node_x == self.x_pos and node_y == self.y_pos

    def move_to_box(self, graph):
        if self.in_box:
            return False
        box_pos = (14, 14)  # Vị trí box của ghost
        self.speed = 8  # Tốc độ di chuyển về box
        # Di chuyển ghost về box
        if self.path and self.path[-1] == box_pos:
            next_node = self.path[0]
            if self.move_to_node(next_node):
                self.path.pop(0)
                if not self.path:
                    self.in_box = True
                    self.speed = 2  # Đặt lại tốc độ về bình thường
                    return True
            return False
        # Tính toán đường đi về box
        from levels.level04 import astar_search
        result = astar_search(self.get_map_position(), box_pos, graph)
        if result:
            self.path = result['path']
            next_node = self.path[0]
            if self.move_to_node(next_node):
                self.path.pop(0)
                if not self.path:
                    self.in_box = True
                    self.speed = 2          # Đặt lại tốc độ về bình thường
                    return True
        return False

    # Cải tiến: Đi hết path cũ rồi mới cập nhật lại path mới
    def move_orange(self, pacman_pos, graph, player, status_set):
        ghost_pos = self.get_map_position()

        # Nếu ghost đã chết và không ở trong box thì di chuyển về box
        if self.dead:
            if not self.in_box:
                if self.move_to_box(graph):
                    self.in_box = True
                    self.path = []
            return False
        
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False

        if self.in_box and self.dead:
            self.path = []
            return False        
        
        if pacman_pos == ghost_pos and not global_var.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        # Nếu global_var.powerup
        if global_var.powerup:
            # Tính toán đường đi mới khi cần (nếu hết path hoặc cooldown = 0)
            if not self.path or self.path[-1] != pacman_pos or getattr(self, "path_update_cooldown", 0) <= 0:
                from levels.level03 import escape_path_for_powerup
                self.path = escape_path_for_powerup(ghost_pos, pacman_pos, graph)
                self.path_update_cooldown = 60  # Ví dụ: cập nhật path mỗi 60 frame
                # print("Orange ghost escaping from powered-up Pacman!")
            else:
                self.path_update_cooldown -= 1
            return False
        else:
            if not self.path:  # Hết đường thì mới tính lại
                from levels.level03 import orange_ghost_path
                self.path = orange_ghost_path(ghost_pos, pacman_pos, graph)

        # Di chuyển theo path hiện tại
        if self.path:
            next_node = self.path[0]

            if next_node in status_set:
                return False
            
            if self.move_to_node(next_node):
                self.path.pop(0)
                status_set.add(next_node)
            return True

        return False

    def move_red(self, pacman_pos, graph, player, status_set):
        ghost_pos = self.get_map_position()

        # Nếu ghost đã chết và không ở trong box thì di chuyển về box
        if self.dead:
            if not self.in_box:
                if self.move_to_box(graph):
                    self.in_box = True
                    self.path = []
            return False
        
        # Delay khi spawn
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False
                
        if pacman_pos == ghost_pos and not global_var.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        if global_var.powerup:
            # Tính toán đường đi mới khi cần (nếu hết path hoặc cooldown = 0)
            if not self.path or self.path[-1] != pacman_pos or getattr(self, "path_update_cooldown", 0) <= 0:
                from levels.level04 import escape_path_for_powerup
                self.path = escape_path_for_powerup(ghost_pos, pacman_pos, graph)
                self.path_update_cooldown = 60  # Ví dụ: cập nhật path mỗi 60 frame
                # print("Red ghost escaping from powered-up Pacman!")
            else:
                self.path_update_cooldown -= 1

            if self.path:
                next_node = self.path[0]

                if next_node in status_set:
                    return False
                
                if self.move_to_node(next_node):
                    self.path.pop(0)
                    status_set.add(next_node)
                return True
            return False

        # Nếu không global_var.powerup: chỉ tính path mới khi path hiện tại rỗng
        if not self.path:
            from levels.level04 import red_ghost_path
            self.path = red_ghost_path(ghost_pos, pacman_pos, graph)

        if self.path:
            next_node = self.path[0]

            if next_node in status_set:
                return False
            
            if self.move_to_node(next_node):
                self.path.pop(0)
                status_set.add(next_node)
            return True

        return False

    def move_blue(self, pacman_pos, graph, player, status_set):
        # Nếu ghost đã chết và không ở trong box thì di chuyển về box
        if self.dead:
            if not self.in_box:
                if self.move_to_box(graph):
                    self.in_box = True
                    self.path = []
            return False
        
        # Delay khi spawn
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False

        ghost_pos = self.get_map_position()

        # Nếu ghost đang ở trạng thái bị Pacman global_var.powerup), tạm thời không di chuyển
        if global_var.powerup:
            return False

        # Nếu ghost và pacman cùng vị trí, ăn Pacman
        if pacman_pos == ghost_pos and not global_var.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        # Tính path mới CHỈ khi path hiện tại đã đi hết
        if not self.path:
            self.path = blue_ghost_path(ghost_pos, pacman_pos, graph)

        # Nếu không có path thì đứng yên
        if not self.path:
            return False

        # Di chuyển theo path hiện tại
        next_node = self.path[0]
        if next_node in status_set:
            return False
        if self.move_to_node(next_node):
            self.path.pop(0)
            status_set.add(next_node)
        return True
    
    def move_pink(self, pacman_pos, graph, player, status_set):
        # Nếu ghost đã chết và không ở trong box thì di chuyển về box
        if self.dead:
            if not self.in_box:
                if self.move_to_box(graph):
                    self.in_box = True
                    self.path = []
            return False
        
        # Delay khi spawn
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False

        ghost_pos = self.get_map_position()

        # Nếu ghost global_var.powerup, không di chuyển và reset path
        if global_var.powerup:
            self.path = []
            return False        

        # Nếu ghost ăn pacman thì ghost sẽ không di chuyển
        if pacman_pos == ghost_pos and not global_var.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        # Nếu chưa có đường đi, hoặc đã đi hết đường cũ, thì tính lại path mới
        if not self.path:
            self.path = pink_ghost_path(ghost_pos, pacman_pos, graph)

        # Nếu không tìm thấy path thì ghost sẽ không di chuyển
        if not self.path:
            return False

        # Di chuyển theo path hiện tại
        next_node = self.path[0]
        if next_node in status_set:
            return False
        if self.move_to_node(next_node):
            self.path.pop(0)
            status_set.add(next_node)
        return True
