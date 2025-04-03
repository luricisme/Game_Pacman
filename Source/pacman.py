import pygame
import math

class Player:
    def __init__(self, x_pos, y_pos):
        # Position and movement
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 24
        self.direction = 0  # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        self.direction_command = 0
        self.speed = 2
        self.turns_allowed = [False, False, False, False]
        
    def draw(self, screen, counter, player_images):
        """Draw the player on the screen"""
        # Update center position
        self.center_x = self.x_pos + 23
        self.center_y = self.y_pos + 24
        
        # Create collision circle
        player_circle = pygame.draw.circle(screen, 'black', (self.center_x, self.center_y), 20, 2)
        
        # Draw player sprite based on direction
        if self.direction == 0:  # Right
            screen.blit(player_images[counter // 5], (self.x_pos, self.y_pos))
        elif self.direction == 1:  # Left
            screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (self.x_pos, self.y_pos))
        elif self.direction == 2:  # Up
            screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (self.x_pos, self.y_pos))
        elif self.direction == 3:  # Down
            screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (self.x_pos, self.y_pos))
            
        return player_circle
            
    def check_position(self, level):
        """Check what directions the player can move in"""
        turns = [False, False, False, False]  # R, L, U, D
        num1 = (950 - 50) // 32  # HEIGHT - 50 // 32
        num2 = 900 // 30         # WIDTH // 30
        num3 = 15                # Fudge factor
        
        # Check if we can move right
        if self.center_x // num2 < 29:
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3:
                turns[0] = True
                
        # Check if we can move left
        if self.center_x // num2 > 0:
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3:
                turns[1] = True
                
        # Check if we can move up
        if self.center_y // num1 > 0:
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3:
                turns[2] = True
                
        # Check if we can move down
        if self.center_y // num1 < 31:
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3:
                turns[3] = True
                
        # Special case for tunnel
        if self.center_x // 30 == 0 or self.center_x // 30 == 29:
            turns[0] = True
            turns[1] = True
            
        return turns
        
    def update(self, level):
        """Update player position based on direction and allowed turns"""
        # Check what turns are allowed
        self.turns_allowed = self.check_position(level)
        
        # Handle keyboard command changes
        if self.direction_command == 0 and self.turns_allowed[0]:
            self.direction = 0
        if self.direction_command == 1 and self.turns_allowed[1]:
            self.direction = 1
        if self.direction_command == 2 and self.turns_allowed[2]:
            self.direction = 2
        if self.direction_command == 3 and self.turns_allowed[3]:
            self.direction = 3
            
        # Move player
        if self.direction == 0 and self.turns_allowed[0]:  # Right
            self.x_pos += self.speed
        elif self.direction == 1 and self.turns_allowed[1]:  # Left
            self.x_pos -= self.speed
        elif self.direction == 2 and self.turns_allowed[2]:  # Up
            self.y_pos -= self.speed
        elif self.direction == 3 and self.turns_allowed[3]:  # Down
            self.y_pos += self.speed
            
        # Handle screen wraparound
        if self.x_pos > 900:
            self.x_pos = -47
        elif self.x_pos < -50:
            self.x_pos = 897
            
        return self.x_pos, self.y_pos
    
    def check_collisions(self, level, score, powerup, power_counter, eaten_ghosts):
        """Check if player has collected dots or power pellets"""
        num1 = (950 - 50) // 32
        num2 = 900 // 30
        
        # Only check if player is within game bounds
        if 0 < self.x_pos < 870:
            # Check if player is on a dot
            if level[self.center_y // num1][self.center_x // num2] == 1:
                level[self.center_y // num1][self.center_x // num2] = 0
                score += 10
            # Check if player is on a power pellet
            elif level[self.center_y // num1][self.center_x // num2] == 2:
                level[self.center_y // num1][self.center_x // num2] = 0
                score += 50
                powerup = True
                power_counter = 0
                eaten_ghosts = [False, False, False, False]
                
        return score, powerup, power_counter, eaten_ghosts
    
    def key_to_direction(self, key):
        """Convert keyboard key to direction value"""
        if key == pygame.K_RIGHT:
            return 0
        elif key == pygame.K_LEFT:
            return 1
        elif key == pygame.K_UP:
            return 2
        elif key == pygame.K_DOWN:
            return 3
        return self.direction