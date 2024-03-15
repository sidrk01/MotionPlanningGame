import csv
from utils import scale_points
import math
import pygame

class BoxObstacle(object):
    def __init__(self, points):
        self.points = points  # the 4 vertices of the box
        
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        
        # AABB representation
        self.x_min = min(xs)
        self.x_max = max(xs)
        self.y_min = min(ys) 
        self.y_max = max(ys)

        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min

    def contains_point(self, point):
        x, y = point
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max
    
def load_obstacles(filename):
    obstacles = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 8: 
                obstacle_points = [(float(row[i]), float(row[i+1])) for i in range(0, 8, 2)]
                obstacles.append(BoxObstacle(obstacle_points))
    return obstacles
