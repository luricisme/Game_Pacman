import pygame
import threading
from ui import *
from levels.level01 import blue_ghost_path
from levels.level02 import pink_ghost_path

class Ghost:
    def __init__(self, type, x_coord, y_coord, target, speed, img, direct, dead, box, id, screen, level, eaten_ghost, powerup,
                  spooked_img, dead_img, spawn_delay=0):
        self.type = type
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.screen = screen
        self.level = level
        self.eaten_ghost = eaten_ghost
        self.powerup = powerup
        self.spooked_img = spooked_img
        self.dead_img = dead_img
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()
        self.spawn_delay = spawn_delay
        self.delay_counter = 0
        self.path = []
        self.pathfinding_thread = None
        self.pathfinding_lock = threading.Lock()
        self.is_pathfinding = False
        self.path = []
        self.pathfinding_cooldown = 0
    
    def start_pathfinding(self, player_pos, graph, other_ghost_positions, player):
        if not self.is_pathfinding and (self.pathfinding_thread is None or not self.pathfinding_thread.is_alive()):
            self.is_pathfinding = True
            self.pathfinding_thread = threading.Thread(
                target=self.pathfinding_worker,
                args=(player_pos, graph, other_ghost_positions, player)
            )
            self.pathfinding_thread.start()

    
    def pathfinding_worker(self, player_pos, graph, other_ghost_positions, player):
        try:
            if self.type == 'red':
                self.move_red(player_pos, graph, other_ghost_positions, player)
            elif self.type == 'pink':
                self.move_pink(player_pos, graph, other_ghost_positions, player)
            elif self.type == 'blue':
                self.move_blue(player_pos, graph, other_ghost_positions, player)
            elif self.type == 'orange':
                self.move_orange(player_pos, graph, other_ghost_positions, player)
        finally:
            self.is_pathfinding = False

    def draw(self):
        if (not self.powerup and not self.dead) or (self.eaten_ghost[self.id] and self.powerup and not self.dead):
            self.screen.blit(self.img, (self.x_pos, self.y_pos))
        elif self.powerup and not self.dead and not self.eaten_ghost[self.id]:
            self.screen.blit(self.spooked_img, (self.x_pos, self.y_pos))
        else:
            self.screen.blit(self.dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect
    
    def get_map_position(self):
        return ((self.y_pos+TILE_HEIGHT//4)//TILE_HEIGHT, (self.x_pos+TILE_WIDTH//4)//TILE_WIDTH)

    def check_collisions(self):
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        num3 = 15
        self.turns = [False, False, False, False]
        level = self.level

        if 0 < self.center_x // 30 < 29:
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
        node_x = node[1] * TILE_WIDTH - TILE_WIDTH // 4
        node_y = node[0] * TILE_HEIGHT - TILE_HEIGHT // 4
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

    def move_to_box(self):
        pass

    # Cải tiến: Đi hết path cũ rồi mới cập nhật lại path mới
    def move_orange(self, pacman_pos, graph, other_ghost_positions, player):
        ghost_pos = self.get_map_position()

        if self.dead and not self.in_box:
            return False

        if self.in_box and not self.dead:
            if self.move_to_node((12, 14)):
                self.in_box = False
            self.path = []
            return False

        if pacman_pos == ghost_pos and not self.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        # Nếu đang powerup
        if self.powerup:
            if not self.path:  # Hết đường đi thì tính lại
                self.target = pacman_pos
                from levels.level03 import escape_path_for_powerup
                self.path = escape_path_for_powerup(ghost_pos, pacman_pos, graph)
                print("Orange ghost escaping from powered-up Pacman!")

        else:
            if not self.path:  # Hết đường thì mới tính lại
                self.target = pacman_pos
                from levels.level03 import orange_ghost_path
                self.path = orange_ghost_path(ghost_pos, pacman_pos, graph, other_ghost_positions)

        # Di chuyển theo path hiện tại
        if self.path:
            if self.move_to_node(self.path[0]):
                self.path.pop(0)
            return True

        return False

    def move_red(self, pacman_pos, graph, other_ghost_positions, player):
        ghost_pos = self.get_map_position()

        # Delay khi spawn
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False

        # Nếu ghost đã chết và không ở trong box thì không di chuyển
        if self.dead and not self.in_box:
            return False

        # Nếu ghost đang ở trong box thì di chuyển ra ngoài box
        if self.in_box and not self.dead:
            if self.move_to_node((12, 14)):
                self.in_box = False
            self.path = []
            return False

        # Nếu ghost ăn pacman thì ghost sẽ không di chuyển
        if pacman_pos == ghost_pos and not self.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        if self.powerup:
            # Tính toán đường đi mới khi cần (nếu hết path hoặc cooldown = 0)
            if not self.path or self.target != pacman_pos or getattr(self, "path_update_cooldown", 0) <= 0:
                self.target = pacman_pos
                from levels.level04 import escape_path_for_powerup
                self.path = escape_path_for_powerup(ghost_pos, pacman_pos, graph)
                self.path_update_cooldown = 60  # Ví dụ: cập nhật path mỗi 60 frame
                print("Red ghost escaping from powered-up Pacman!")
            else:
                self.path_update_cooldown -= 1

            if self.path:
                if self.move_to_node(self.path[0]):
                    self.path.pop(0)
                return True
            return False

        # Nếu không có powerup: chỉ tính path mới khi path hiện tại rỗng
        if not self.path:
            from levels.level04 import red_ghost_path
            self.path = red_ghost_path(ghost_pos, pacman_pos, graph)

        if self.path:
            if self.move_to_node(self.path[0]):
                self.path.pop(0)
            return True

        return False

    
    def move_blue(self, pacman_pos, graph, other_ghost_positions, player):
        # Delay khi spawn
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False

        ghost_pos = self.get_map_position()

        # Nếu ghost đang ở trạng thái bị Pacman ăn (powerup), tạm thời không di chuyển
        if self.powerup:
            return False

        # Nếu ghost đã chết và không ở trong box thì không di chuyển
        if self.dead and not self.in_box:
            return False

        # Nếu ghost đang ở trong box thì di chuyển ra ngoài box
        if self.in_box and not self.dead:
            if self.move_to_node((12, 14)):
                self.in_box = False
            self.path = []
            return False

        # Nếu ghost và pacman cùng vị trí, ăn Pacman
        if pacman_pos == ghost_pos and not self.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        # Tính path mới CHỈ khi path hiện tại đã đi hết
        if not self.path:
            self.path = blue_ghost_path(ghost_pos, pacman_pos, graph, other_ghost_positions)

        # Nếu không có path thì đứng yên
        if not self.path:
            return False

        # Di chuyển theo path hiện tại
        if self.move_to_node(self.path[0]):
            self.path.pop(0)
        return True
    
    def move_pink(self, pacman_pos, graph, other_ghost_positions, player):
        # Delay khi spawn
        if self.delay_counter < self.spawn_delay:
            self.delay_counter += 1
            return False

        ghost_pos = self.get_map_position()

        # Nếu ghost đang powerup, không di chuyển và reset path
        if self.powerup:
            self.path = []
            return False

        # Nếu ghost đã chết và không ở trong box thì không di chuyển
        if self.dead and not self.in_box:
            return False

        # Nếu ghost đang ở trong box thì di chuyển ra ngoài box
        if self.in_box and not self.dead:
            if self.move_to_node((12, 14)):
                self.in_box = False
            self.path = []
            return False

        # Nếu ghost ăn pacman thì ghost sẽ không di chuyển
        if pacman_pos == ghost_pos and not self.powerup:
            print("Pacman eaten")
            player.isLive = False
            self.path = []
            return False

        # Nếu chưa có đường đi, hoặc đã đi hết đường cũ, thì tính lại path mới
        if not self.path:
            self.path = pink_ghost_path(ghost_pos, pacman_pos, graph, other_ghost_positions)

        # Nếu không tìm thấy path thì ghost sẽ không di chuyển
        if not self.path:
            return False

        # Di chuyển theo đường đã tính
        if self.move_to_node(self.path[0]):
            self.path.pop(0)
        return True