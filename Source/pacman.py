import pygame

class Pacman:
    def __init__(self, start_pos, map_data):
        self.pos = start_pos
        self.map = map_data

    def move(self, direction):
        x, y = self.pos
        dx, dy = {
            "UP": (0, -1), "DOWN": (0, 1),
            "LEFT": (-1, 0), "RIGHT": (1, 0)
        }[direction]
        new_x, new_y = x + dx, y + dy

        if self.map[new_y][new_x] != "1":  # không phải tường
            self.pos = (new_x, new_y)

    def render(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (self.pos[0]*32+16, self.pos[1]*32+16), 16)
