import pygame
import numpy as np
import random
from math import sin, cos, pi
from utils import scale_points

red = (255, 0, 0)

class Enemy(pygame.sprite.Sprite):

    def __init__(self, start_pos):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(red)
        self.rect = self.surf.get_rect(center=(200, 300))
        self.position = np.array(start_pos, dtype=float)
        self.destination = None
        self.path = []
        self.speed = 2
        self.radius = 5
        self.following_roadmap = False

    def update_position(self, obstacles, scale_x, scale_y, offset_x, offset_y):
        if not self.path:
            return  
        destination = np.array(self.path[0])
        direction = destination - self.position
        distance_to_destination = np.linalg.norm(direction)
    
        if distance_to_destination < self.speed:
            if not self.collides_with_obstacles(destination, obstacles, scale_x, scale_y, offset_x, offset_y):
                self.position = destination
                self.rect.center = self.position
            self.path.pop(0)
        else:
            direction_norm = direction / distance_to_destination
            new_position = self.position + direction_norm * self.speed
            if self.collides_with_obstacles(new_position, obstacles, scale_x, scale_y, offset_x, offset_y) and not self.following_roadmap:
                self.set_random_target((1000,1000))
                self.start_following_roadmap()

            if not self.collides_with_obstacles(new_position, obstacles, scale_x, scale_y, offset_x, offset_y):
                self.position = new_position
                self.rect.center = self.position

    def collides_with_obstacles(self, new_position, obstacles, scale_x, scale_y, offset_x, offset_y):
        num_points = 100 
        angles = np.linspace(0, 2 * pi, num_points, endpoint=False)
        points = [(self.radius * cos(angle) + new_position[0], self.radius * sin(angle) + new_position[1]) for angle in angles]

        for obstacle in obstacles:
            scaled_obstacle = scale_points(obstacle.points, scale_x, scale_y, offset_x, offset_y)
            obstacle_rect = pygame.Rect(min(p[0] for p in scaled_obstacle), min(p[1] for p in scaled_obstacle),
                                        max(p[0] for p in scaled_obstacle) - min(p[0] for p in scaled_obstacle),
                                        max(p[1] for p in scaled_obstacle) - min(p[1] for p in scaled_obstacle))

            for point in points:
                if obstacle_rect.collidepoint(point):
                    return True

        return False
    
    def set_roadmap(self, roadmap, points):
        self.roadmap = [(points[i][0], points[i][1]) for i in roadmap]

    def start_following_roadmap(self):
        if self.roadmap:
            self.following_roadmap = True
            self.path = self.roadmap

    def set_random_target(self, game_area):
        # game_area is expected to be a tuple (width, height)
        self.target = (random.randint(0, game_area[0]), random.randint(0, game_area[1]))
        self.path = [self.target]  # Reset the path with the new target

    def stop_following_roadmap(self):
        self.following_roadmap = False

