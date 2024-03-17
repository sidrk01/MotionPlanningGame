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
        self.points = []
        self.roadmap = []
        self.speed = 2
        self.radius = 5
        self.get_other_enemies_positions = None
        self.following_roadmap = False
        self.locked_on_path = False  
        self.locked_time = 0 
        self.last_position = np.array(start_pos, dtype=float)  


    def reset(self, start_pos):
        self.position = np.array(start_pos, dtype=float)

    def set_params(self, speed, following_roadmap, destination):
        self.speed = speed
        self.following_roadmap = following_roadmap
        self.destination = destination

    def update_position(self, obstacles, scale_x, scale_y, offset_x, offset_y, get_other_enemies_positions, current_time):
        self.get_other_enemies_positions = get_other_enemies_positions
        self.current_time = current_time 

        if not self.path:
            return

        if self.locked_on_path and self.current_time <= self.locked_time:

            self.move_along_path(obstacles, scale_x, scale_y, offset_x, offset_y)
        elif not self.locked_on_path or self.current_time > self.locked_time:
            self.locked_on_path = False  
            destination = np.array(self.path[0])
            direction = destination - self.position
            distance_to_destination = np.linalg.norm(direction)

            if distance_to_destination < self.speed:
                self.position = destination
                self.rect.center = self.position
                if len(self.path) > 0: 
                    self.path.pop(0)
            else:
                direction_norm = direction / distance_to_destination
                new_position = self.position + direction_norm * self.speed
                if not self.collides_with_obstacles(new_position, obstacles, scale_x, scale_y, offset_x, offset_y):
                    self.position = new_position
                    self.rect.center = self.position
                else:
                    if not self.following_roadmap:
                        self.set_nearest_roadmap_path()

        self.last_position = np.array(self.position)  
 
        

    def move_along_path(self, obstacles, scale_x, scale_y, offset_x, offset_y):
        if len(self.path) > 0:
            destination = np.array(self.path[0])
            direction = destination - self.position
            new_position = self.position + direction / np.linalg.norm(direction) * self.speed

        if not self.collides_with_obstacles(new_position, obstacles, scale_x, scale_y, offset_x, offset_y):
            self.position = new_position
            self.rect.center = self.position

            if np.linalg.norm(direction) < self.speed:
                self.path.pop(0)  

    def set_nearest_roadmap_path(self):
        if self.points:
            closest_indices = sorted(range(len(self.points)), key=lambda i: np.linalg.norm(self.position - np.array(self.points[i])))[:5]
            self.path = [self.points[i] for i in closest_indices]
            self.locked_on_path = True
            self.locked_time = self.current_time + 3000 


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
                
        if self.get_other_enemies_positions:
            other_enemies_positions = self.get_other_enemies_positions()
            for pos in other_enemies_positions:
                if np.linalg.norm(new_position - np.array(pos)) < self.radius * 2:  
                    return True

        return False
    
    def set_roadmap(self, roadmap, points):
        self.roadmap_indices = list(roadmap.keys())  
        unique_points_indices = set(self.roadmap_indices)
        for connected_points in roadmap.values():
            unique_points_indices.update(connected_points)
        self.points = [points[i] for i in unique_points_indices]


    def start_following_roadmap(self):
        if self.roadmap:
            self.following_roadmap = True
            self.path = self.roadmap

    def set_random_target(self, game_area):
        self.target = (random.randint(0, game_area[0]), random.randint(0, game_area[1]))
        self.path = [self.target] 

    def stop_following_roadmap(self):
        self.following_roadmap = False
