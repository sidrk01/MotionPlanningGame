# utils.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the author.
# 
# Authors: Ioannis Karamouzas (ioannis@cs.ucr.edu)
#

import math 
import pygame
import random
import numpy as np

#used for scaling obstacles to full-screen
def scale_points(points, scale_x, scale_y, offset_x, offset_y):
    return [(x * scale_x + offset_x, y * scale_y + offset_y) for x, y in points]

def draw_prm_roadmap(screen, roadmap, points, point_color=(0, 0, 0), line_color=(0, 0, 0), point_radius=5):
    for point_index, connected_points in roadmap.items():
        for connection_index in connected_points:
            pygame.draw.line(screen, line_color, points[point_index], points[connection_index])

    for point in points:
        pygame.draw.circle(screen, point_color, (int(point[0]), int(point[1])), point_radius)

""" Returns the oriented bounding box of a given configuration q """
def getRobotPlacement(q, robot_width, robot_height):
    
    vertices = [# coordinates assuming theta is 0 
        [q[0] - robot_width*0.5, q[1] - robot_height*0.5], # bottom left
        [q[0] + robot_width*0.5, q[1] - robot_height*0.5], # bottom right ....
        [q[0] + robot_width*0.5, q[1] + robot_height*0.5],
        [q[0] - robot_width*0.5, q[1] + robot_height*0.5],
    ]
    ctheta = math.cos(q[2])
    stheta = math.sin(q[2])
    points = []
    for x, y in vertices:
        # place center of obb at the origin
        x -= q[0] 
        y -= q[1] 
        # apply rotation
        x_new = x * ctheta - y * stheta
        y_new = x * stheta + y * ctheta 
        points.append([x_new + q[0], -y_new + q[1]]) # the neg sign is due to the fact that the y axis is flipped in canvas

    return points

class Value():
    """A helper class for adding f & g values to your PriorityQueue """

    def __init__(self, f, g):
        self.g = g
        self.f = f

class OrderedSet:
    """ An ordered list of elements """
    
    def __init__(self):
        self._container = []
    
    def add(self, item):
        if item in self._container:
            self._container.append(item)
        else:
            self._container.append(item)

    def has(self, item):
        return self._container.__contains__

    def remove(self, item):
        if item in self._container:
            self._container.remove(item)
    
    def clear(self):
        self._container.clear()
    
    def __contains__(self, item):
        return self._container.__contains__(item)

    def __len__(self):
        return self._container.__len__()
    
    def __iter__(self):
        return self._container.__iter__()
    
    def pop(self, last=True):
        if last:
            e = self._container.pop()
        else:
            e = self._container.pop(0)
        return e

class PriorityQueue:
    """
        A Queue in which the minimum (or maximum) element (as determined by f and
        order) is returned first.
    """
    def __init__(self, order=min, f=lambda v:v):
        if order == min or order == "min":
            self.order = min
        elif order == max or order == "max":
            self.order = max
        else:
            raise KeyError("order must be min or max")
        self.f = f

        self._dict = {}
  
    def get(self, item):
        return self._dict.__getitem__(item)

    def put(self, item, value):
        if item not in self._dict:
            self._dict[item] = value
        else:
            self._dict[item] = value

    def has(self, item):
        return self._dict.__contains__(item)

    def remove(self, item):
        if item in self._dict:
            del self._dict[item]

    def pop(self):
        if len(self._dict) > 0:
            tar = self.order(self._dict, key=lambda k: self.f(self._dict.get(k)))
            val = self._dict[tar]
            del self._dict[tar]
            return tar, val
        raise IndexError("pop from empty priority queue")

    def __iter__(self):
        return self._dict.__iter__()
    
    def __contains__(self, item):
        return self._dict.__contains__(item)

    def __len__(self):
        return self._dict.__len__()

    def __getitem__(self, key):
        return self._dict.__getitem__(key)
    
    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)
    
    def __delitem__(self, key):
        return self._dict.__delitem__(key)
    
    ## added empty for astar simplicity
    def empty(self):
        return len(self._dict) == 0

def remove_loops(roadmap):
    visited = set()
    remove_list = []

    def dfs(current, parent):
        if current in visited:
            return True
        visited.add(current)
        for neighbor in roadmap[current]:
            if neighbor == parent:
                continue  # Skip the edge leading back to the parent
            if dfs(neighbor, current):  # A loop is detected
                if (current, neighbor) not in remove_list:
                    remove_list.append((current, neighbor))

    for point in list(roadmap.keys()):
        dfs(point, None)

    for edge in remove_list:
        roadmap[edge[0]].remove(edge[1])

    return roadmap

def is_edge_valid(point1, point2, obstacles):
    for obstacle in obstacles:
        if obstacle.intersects_edge(point1, point2):
            return False
    return True

def build_roadmap(num_points, connection_radius, game_area, obstacles):
    points = []
    roadmap = {}
    
    while len(points) < num_points:
        point = (random.uniform(0, game_area[0]), random.uniform(0, game_area[1]))
        if not is_point_inside_obstacles(point, obstacles):
            points.append(point)
    
    for i, point in enumerate(points):
        roadmap[i] = []
        for j, other_point in enumerate(points):
            if i != j and np.linalg.norm(np.array(point) - np.array(other_point)) < connection_radius:
                if is_edge_valid(point, other_point, obstacles):
                    roadmap[i].append(j)
    
    roadmap = remove_loops(roadmap)
    return roadmap, points

def is_point_inside_obstacles(point, obstacles):
    for obstacle in obstacles:
        if obstacle.contains_point(point):
            return True
    return False
