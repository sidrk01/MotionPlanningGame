import pygame
import numpy as np
from math import cos, sin, pi
from utils import scale_points

blue = (0, 0, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 12
        self.start_position = (400, 300)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, blue, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(400, 300))
        self.is_hiding = False

    def reset(self, position=None):
        if position is None:
            position = self.start_position
        self.rect.center = position

    def update(
        self,
        pressed_keys,
        obstacles,
        hiding_spots,
        scale_x,
        scale_y,
        offset_x,
        offset_y,
    ):
        dx = dy = 0
        if pressed_keys[pygame.K_w]:
            dy = -3
        if pressed_keys[pygame.K_s]:
            dy = 3
        if pressed_keys[pygame.K_a]:
            dx = -3
        if pressed_keys[pygame.K_d]:
            dx = 3

        if not self.collides_with_obstacles(
            dx, dy, obstacles, scale_x, scale_y, offset_x, offset_y
        ):
            self.rect.move_ip(dx, dy)

        currently_hiding = any(
            self.rect.colliderect(spot.rect) for spot in hiding_spots
        )
        # self.is_hiding = currently_hiding

        if currently_hiding and not self.is_hiding:
            self.is_hiding = True
            print("Player is just hidden.")

        # If the player is not overlapping with any hiding spots, set is_hiding to False
        elif not currently_hiding and self.is_hiding:
            self.is_hiding = False
            print("Player is no longer hidden.")

    def collides_with_obstacles(
        self, dx, dy, obstacles, scale_x, scale_y, offset_x, offset_y
    ):
        new_center = np.array([self.rect.centerx + dx, self.rect.centery + dy])
        num_points = 100
        angles = np.linspace(0, 2 * pi, num_points, endpoint=False)
        points = [
            (
                self.radius * cos(angle) + new_center[0],
                self.radius * sin(angle) + new_center[1],
            )
            for angle in angles
        ]

        for obstacle in obstacles:
            scaled_obstacle = scale_points(
                obstacle.points, scale_x, scale_y, offset_x, offset_y
            )
            obstacle_rect = pygame.Rect(
                min(p[0] for p in scaled_obstacle),
                min(p[1] for p in scaled_obstacle),
                max(p[0] for p in scaled_obstacle) - min(p[0] for p in scaled_obstacle),
                max(p[1] for p in scaled_obstacle) - min(p[1] for p in scaled_obstacle),
            )

            for point in points:
                if obstacle_rect.collidepoint(point):
                    return True

        return False

    @property
    def position(self):
        return self.rect.center
