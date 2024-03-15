import pygame
import numpy as np

red = (255, 0, 0)

class Enemy(pygame.sprite.Sprite):

    def __init__(self, start_pos):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(red)
        self.rect = self.surf.get_rect(center=(200, 300))
        self.position = start_pos
        self.destination = None
        self.path = []
        self.speed = 5

    def update_screen_position(self, scale_x, scale_y, offset_x, offset_y):
        # Scale the position to screen coordinates
        scaled_x = self.position[0] * scale_x + offset_x
        scaled_y = self.position[1] * scale_y + offset_y
        self.rect.x, self.rect.y = scaled_x, scaled_y

    def update_position(self):
        if not self.path:
            return  
        destination = self.path[0]
        direction = np.subtract(destination, self.position)
        distance_to_destination = np.linalg.norm(direction)
        
        if distance_to_destination < self.speed:
            self.position = destination
            self.path.pop(0)
        else:
            direction_norm = direction / distance_to_destination
            self.position += direction_norm * self.speed
