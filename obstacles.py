# obstacles.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the author.
# 
# Authors: Ioannis Karamouzas (ioannis@cs.ucr.edu)
#

# simple class for AABB obstacles
import csv

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

def load_obstacles_from_csv(filename):
    obstacles = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 8: 
                obstacle_points = [(float(row[i]), float(row[i+1])) for i in range(0, 8, 2)]
                obstacles.append(BoxObstacle(obstacle_points))
    return obstacles

