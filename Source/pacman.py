import pygame
import math
from ui import *

PI = math.pi

class Pacman:
    def __init__(self, x, y):
        self.images = [pygame.transform.scale(pygame.image.load(f'Source/assets/pacman/{i}.png'), (45, 45)) for i in range(1, 5)]
        self.x = x
        self.y = y

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
        self.powerup = False
        self.power_counter = 0
        self.eaten_ghosts = [False, False, False, False]        

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
        return ((self.y+TILE_HEIGHT//2)//TILE_HEIGHT, (self.x+TILE_HEIGHT//2)//TILE_WIDTH)

    def check_position(self, level):
        turns = [False, False, False, False]
        num1 = TILE_HEIGHT
        num2 = TILE_WIDTH
        num3 = 15
        centerx = self.x + 23
        centery = self.y + 24

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
                if 12 <= centerx % num2 <= 18:
                    if level[(centery + num3) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if level[(centery - num3) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if level[centery // num1][(centerx - num2) // num2] < 3:
                        turns[1] = True
                    if level[centery // num1][(centerx + num2) // num2] < 3:
                        turns[0] = True
            if self.direction in [0, 1]:
                if 12 <= centerx % num2 <= 18:
                    if level[(centery + num1) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if level[(centery - num1) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if level[centery // num1][(centerx - num3) // num2] < 3:
                        turns[1] = True
                    if level[centery // num1][(centerx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns

    def check_collisions(self, level):
        num1 = (HEIGHT - 50) // 32
        num2 = WIDTH // 30
        center_x = self.x + 22  # ~nửa kích thước Pac-Man (45/2)
        center_y = self.y + 22

        if 0 < center_x < 870:
            row = center_y // num1
            col = center_x // num2
            if level[row][col] == 1:
                level[row][col] = 0
                self.score += 10
            elif level[row][col] == 2:
                level[row][col] = 0
                self.score += 50
                self.powerup = True
                self.power_counter = 0
                self.eaten_ghosts = [False, False, False, False]
        return self.score, self.powerup, self.power_counter, self.eaten_ghosts
        
        
