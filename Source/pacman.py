import pygame
import math
from ui import *
import global_var

PI = math.pi

class Pacman:
    def __init__(self, x, y):
        self.images = [pygame.transform.scale(pygame.image.load(f'Source/assets/pacman/{i}.png'), (40, 40)) for i in range(1, 5)]
        self.x = y*TILE_WIDTH - TILE_WIDTH//4
        self.y = x*TILE_HEIGHT - TILE_HEIGHT//4

        self.isLive = True
        self.direction = 0
        self.direction_command = 0
        self.speed = 2
        self.turns_allowed = [False, False, False, False]

        self.counter = 0
        self.startup_counter = 0
        self.flicker = False

        self.score = 0
        self.moving = True
        self.power_counter = 0   

    def draw(self, screen):
        if self.direction == 0:
            screen.blit(self.images[self.counter // 5], (self.x, self.y))
        elif self.direction == 1:
            screen.blit(pygame.transform.flip(self.images[self.counter // 5], True, False), (self.x, self.y))
        elif self.direction == 2:
            screen.blit(pygame.transform.rotate(self.images[self.counter // 5], 90), (self.x, self.y))
        elif self.direction == 3:
            screen.blit(pygame.transform.rotate(self.images[self.counter // 5], 270), (self.x, self.y))
        else:
            screen.blit(self.images[self.counter // 5], (self.x, self.y))
            
    
    def move(self):
        if self.direction == 0 and self.turns_allowed[0]:
            self.x += self.speed
        elif self.direction == 1 and self.turns_allowed[1]:
            self.x -= self.speed
        elif self.direction == 2 and self.turns_allowed[2]:
            self.y -= self.speed
        elif self.direction == 3 and self.turns_allowed[3]:
            self.y += self.speed
    
    def get_position(self):
        return ((self.y +TILE_HEIGHT//4)//TILE_HEIGHT, (self.x + TILE_WIDTH//4)//TILE_WIDTH)

    def check_position(self, level):
        turns = [False, False, False, False]
        num1 = TILE_HEIGHT
        num2 = TILE_WIDTH
        num3 = 13
        centerx = self.x + 20
        centery = self.y + 20

        if centerx // 30 < 29:
            if self.direction == 0:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
            if self.direction == 1:
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
            if self.direction == 2:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
            if self.direction == 3:
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True

            if self.direction in [2, 3]:
                if 10 <= centerx % num2 <= 18:
                    if level[(centery + num3) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if level[(centery - num3) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 10 <= centery % num1 <= 18:
                    if level[centery // num1][(centerx - num2) // num2] < 3:
                        turns[1] = True
                    if level[centery // num1][(centerx + num2) // num2] < 3:
                        turns[0] = True
            if self.direction in [0, 1]:
                if 10 <= centerx % num2 <= 18:
                    if level[(centery + num1) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if level[(centery - num1) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 10 <= centery % num1 <= 18:
                    if level[centery // num1][(centerx - num3) // num2] < 3:
                        turns[1] = True
                    if level[centery // num1][(centerx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns

    def check_collisions(self, level):
        num1 = TILE_HEIGHT
        num2 = TILE_WIDTH
        center_x = self.x + 20  # ~nửa kích thước Pac-Man (45/2)
        center_y = self.y + 20

        if 0 < center_x < 770:
            row = center_y // num1
            col = center_x // num2
            if level[row][col] == 1:
                level[row][col] = 0
                self.score += 10
            elif level[row][col] == 2:
                level[row][col] = 0
                self.score += 50
                global_var.powerup = True
                # print("POWER UP IN PACMAN: ", global_var.powerup)
                self.power_counter = 0
                self.eaten_ghosts = [False, False, False, False]
        
        
