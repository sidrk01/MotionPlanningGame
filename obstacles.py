import csv
from utils import scale_points
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

    def intersects_edge(self, p1, p2):
        """
        Check if the line segment between p1 and p2 intersects this BoxObstacle.
        """
        # Check if either end of the line segment is inside the box
        if self.x_min <= p1[0] <= self.x_max and self.y_min <= p1[1] <= self.y_max:
            return True
        if self.x_min <= p2[0] <= self.x_max and self.y_min <= p2[1] <= self.y_max:
            return True

        # Check for intersection with each side of the box
        box_corners = [(self.x_min, self.y_min), (self.x_max, self.y_min),
                       (self.x_max, self.y_max), (self.x_min, self.y_max)]
        box_edges = [(box_corners[i], box_corners[(i + 1) % 4]) for i in range(4)]

        for box_edge_start, box_edge_end in box_edges:
            if self.line_segments_intersect(p1, p2, box_edge_start, box_edge_end):
                return True

        return False

    @staticmethod
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    @staticmethod
    def line_segments_intersect(p1, p2, p3, p4):
        return BoxObstacle.ccw(p1, p3, p4) != BoxObstacle.ccw(p2, p3, p4) and BoxObstacle.ccw(p1, p2, p3) != BoxObstacle.ccw(p1, p2, p4)

def load_obstacles(filename):
    obstacles = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 8: 
                obstacle_points = [(float(row[i]), float(row[i+1])) for i in range(0, 8, 2)]
                obstacles.append(BoxObstacle(obstacle_points))
    return obstacles
