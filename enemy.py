import pygame
red = (255, 0, 0)

class Enemy(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(red)
        self.rect = self.surf.get_rect(center=(200, 300))