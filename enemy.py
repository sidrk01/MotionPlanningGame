import pygame
import numpy as np

red = (255, 0, 0)

class Enemy(pygame.sprite.Sprite):

    def __init__(self, start_pos, color=red):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center=(200, 300))
        self.position = start_pos
        self.destination = None
        self.path = []
        self.speed = 3

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
