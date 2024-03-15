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

# Used for scaling obstacles to full-screen
def scale_points(points, scale_x, scale_y, offset_x, offset_y):
    return [(x * scale_x + offset_x, y * scale_y + offset_y) for x, y in points]

def draw_prm_roadmap(screen, roadmap, points, point_color=(0, 0, 0), line_color=(0, 0, 0), point_radius=5):
    for point_index, connected_points in roadmap.items():
        for connection_index in connected_points:
            pygame.draw.line(screen, line_color, points[point_index], points[connection_index])
    for point in points:
        pygame.draw.circle(screen, point_color, (int(point[0]), int(point[1])), point_radius)

def interpolate_points(p1, p2, num_points=5):
    """Generate points between p1 and p2."""
    return [(p1[0] + i * (p2[0] - p1[0]) / num_points, p1[1] + i * (p2[1] - p1[1]) / num_points) for i in range(num_points + 1)]

def getRobotPlacement(q, robot_width, robot_height):
    vertices = [
        [q[0] - robot_width*0.5, q[1] - robot_height*0.5],  # Bottom left
        [q[0] + robot_width*0.5, q[1] - robot_height*0.5],  # Bottom right
        [q[0] + robot_width*0.5, q[1] + robot_height*0.5],  # Top right
        [q[0] - robot_width*0.5, q[1] + robot_height*0.5],  # Top left
    ]
    ctheta = math.cos(q[2])
    stheta = math.sin(q[2])
    rotated_vertices = [(x * ctheta - y * stheta + q[0], x * stheta + y * ctheta + q[1]) for x, y in [(vx - q[0], vy - q[1]) for vx, vy in vertices]]
    return rotated_vertices

class Value:
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
        if not self._dict:
            raise IndexError("pop from empty priority queue")
        tar = self.order(self._dict, key=lambda k: self.f(self._dict[k]))
        del self._dict[tar]
        return tar  

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

def is_point_inside_any_obstacle(point, obstacles):
    for obstacle in obstacles:
        if obstacle.contains_point(point): 
            return True
    return False

def interpolate_points(p1, p2, num_points=10):
    return [(p1[0] + i * (p2[0] - p1[0]) / (num_points - 1), p1[1] + i * (p2[1] - p1[1]) / (num_points - 1)) for i in range(num_points)]

def is_edge_valid(point1, point2, obstacles):
    interpolated_points = interpolate_points(point1, point2, 10)  
    for interpolated_point in interpolated_points:
        if is_point_inside_any_obstacle(interpolated_point, obstacles):
            return False
    return True

#functions to improve roadmap
def remove_loops(roadmap):
    visited = set()
    remove_list = []

    def dfs(current, parent):
        if current in visited:
            return True
        visited.add(current)
        for neighbor in roadmap[current]:
            if neighbor == parent:
                continue 
            if dfs(neighbor, current): 
                if (current, neighbor) not in remove_list:
                    remove_list.append((current, neighbor))

    for point in list(roadmap.keys()):
        dfs(point, None)

    for edge in remove_list:
        roadmap[edge[0]].remove(edge[1])

    return roadmap

def write_roadmap_to_file(roadmap, points, filename="roadmap.txt"):
    with open(filename, 'w') as file:
        for idx, connections in roadmap.items():
            point_str = f"Point {idx}: {points[idx]}, Connections: "
            connections_str = ', '.join([f"{i} ({points[i]})" for i in connections])
            file.write(point_str + connections_str + '\n')

def build_roadmap(num_points, connection_radius, game_area, obstacles):
    """Builds a roadmap of interconnected points within a game area, avoiding obstacles."""
    points = []
    roadmap = {}
    while len(points) < num_points:
        point = (random.uniform(0, game_area[0]), random.uniform(0, game_area[1]))
        if not any(obstacle.contains_point(point) for obstacle in obstacles):
            points.append(point)
    for i, point in enumerate(points):
        roadmap[i] = []
        for j, other_point in enumerate(points):
            if i != j and np.linalg.norm(np.array(point) - np.array(other_point)) < connection_radius:
                if is_edge_valid(point, other_point, obstacles):
                    roadmap[i].append(j)
    remove_loops(roadmap)

    write_roadmap_to_file(roadmap, points)
    return roadmap, points

#pathfinding logic for enemy
def heuristic(p1, p2):
    """Euclidean distance heuristic."""
    return np.linalg.norm(np.array(p1) - np.array(p2))

def closest_point_index(position, points):
    """Find the index of the closest point in 'points' to the given 'position'."""
    return min(range(len(points)), key=lambda i: np.linalg.norm(np.array(position) - np.array(points[i])))

def find_path(start_idx, goal_idx, roadmap, points):
    frontier = PriorityQueue()
    frontier.put(start_idx, 0)
    came_from = {start_idx: None}
    cost_so_far = {start_idx: 0}

    while not frontier.empty():
        current = frontier.pop()

        if current == goal_idx:
            break
        print(f"Current: {current}, type: {type(current)}")
        for next_idx in roadmap[current]:
            next_point = points[next_idx]
            current_point = points[current]
            new_cost = cost_so_far[current] + heuristic(current_point, next_point)
            if next_idx not in cost_so_far or new_cost < cost_so_far[next_idx]:
                cost_so_far[next_idx] = new_cost
                priority = new_cost + heuristic(points[goal_idx], next_point)
                frontier.put(next_idx, priority)
                came_from[next_idx] = current

    path = []
    current = goal_idx
    while current is not None: 
        path.append(current)
        current = came_from.get(current)
    path.reverse()

    return path if path[0] == start_idx else [] 

def update_enemy_path(enemy, roadmap, points):
    start_pos = enemy.position
    goal_pos = points[random.randint(0, len(points) - 1)] 
    
    start_idx = closest_point_index(start_pos, points)  
    goal_idx = closest_point_index(goal_pos, points) 

    print(f"start_idx: {start_idx}, type: {type(start_idx)}")
    print(f"goal_idx: {goal_idx}, type: {type(goal_idx)}")
    path_indices = find_path(start_idx, goal_idx, roadmap, points)
    enemy.path = [points[i] for i in path_indices]



def closest_point_index(position, points):
    closest_index = min(range(len(points)), key=lambda i: np.linalg.norm(np.array(position) - np.array(points[i])))
    return closest_index