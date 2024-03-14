import pygame
import numpy as np
from obstacles import load_obstacles_from_csv
from math import cos, sin, pi
from utils import scale_points

blue = (0, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 12
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, blue, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(400, 300))

    def update(self, pressed_keys, obstacles, scale_x, scale_y, offset_x, offset_y):
        dx = dy = 0
        if pressed_keys[pygame.K_w]: dy = -5
        if pressed_keys[pygame.K_s]: dy = 5
        if pressed_keys[pygame.K_a]: dx = -5
        if pressed_keys[pygame.K_d]: dx = 5

        if not self.collides_with_obstacles(dx, dy, obstacles, scale_x, scale_y, offset_x, offset_y):
            self.rect.move_ip(dx, dy)

    def collides_with_obstacles(self, dx, dy, obstacles, scale_x, scale_y, offset_x, offset_y):
        new_center = np.array([self.rect.centerx + dx, self.rect.centery + dy])
        num_points = 10 
        angles = np.linspace(0, 2 * pi, num_points, endpoint=False)
        points = [(self.radius * cos(angle) + new_center[0], self.radius * sin(angle) + new_center[1]) for angle in angles]

        for obstacle in obstacles:
            scaled_obstacle = scale_points(obstacle.points, scale_x, scale_y, offset_x, offset_y)
            obstacle_rect = pygame.Rect(min(p[0] for p in scaled_obstacle), min(p[1] for p in scaled_obstacle),
                                        max(p[0] for p in scaled_obstacle) - min(p[0] for p in scaled_obstacle),
                                        max(p[1] for p in scaled_obstacle) - min(p[1] for p in scaled_obstacle))

            for point in points:
                if obstacle_rect.collidepoint(point):
                    return True

        return False