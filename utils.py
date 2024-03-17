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


def scale_points(points, scale_x, scale_y, offset_x, offset_y):
    return [(x * scale_x + offset_x, y * scale_y + offset_y) for x, y in points]


def draw_prm_roadmap(
    screen, roadmap, points, point_color=(0, 0, 0), line_color=(0, 0, 0), point_radius=5
):
    for point_index, connected_points in roadmap.items():
        for connection_index in connected_points:
            pygame.draw.line(
                screen, line_color, points[point_index], points[connection_index]
            )
    for point in points:
        pygame.draw.circle(
            screen, point_color, (int(point[0]), int(point[1])), point_radius
        )


def interpolate_points(p1, p2, num_points=5):
    return [
        (
            p1[0] + i * (p2[0] - p1[0]) / num_points,
            p1[1] + i * (p2[1] - p1[1]) / num_points,
        )
        for i in range(num_points + 1)
    ]


def getRobotPlacement(q, robot_width, robot_height):
    vertices = [
        [q[0] - robot_width * 0.5, q[1] - robot_height * 0.5],  # Bottom left
        [q[0] + robot_width * 0.5, q[1] - robot_height * 0.5],  # Bottom right
        [q[0] + robot_width * 0.5, q[1] + robot_height * 0.5],  # Top right
        [q[0] - robot_width * 0.5, q[1] + robot_height * 0.5],  # Top left
    ]
    ctheta = math.cos(q[2])
    stheta = math.sin(q[2])
    rotated_vertices = [
        (x * ctheta - y * stheta + q[0], x * stheta + y * ctheta + q[1])
        for x, y in [(vx - q[0], vy - q[1]) for vx, vy in vertices]
    ]
    return rotated_vertices


class Value:
    def __init__(self, f, g):
        self.g = g
        self.f = f


class OrderedSet:
    """An ordered list of elements"""

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

    def __init__(self, order=min, f=lambda v: v):
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


def is_point_inside_any_obstacle(
    point, obstacles, scale_x, scale_y, offset_x, offset_y, size=None
):
    if size is None:
        for obstacle in obstacles:
            if obstacle.contains_point(point, scale_x, scale_y, offset_x, offset_y):
                return True
    else:
        half_width, half_height = size[0] / 2, size[1] / 2
        corners = [
            (point[0] - half_width, point[1] - half_height),
            (point[0] + half_width, point[1] - half_height),
            (point[0] + half_width, point[1] + half_height),
            (point[0] - half_width, point[1] + half_height),
        ]
        for corner in corners:
            if is_point_inside_any_obstacle(
                corner, obstacles, scale_x, scale_y, offset_x, offset_y
            ):
                return True
    return False


def interpolate_points(p1, p2, num_points=10):
    return [
        (
            p1[0] + i * (p2[0] - p1[0]) / (num_points - 1),
            p1[1] + i * (p2[1] - p1[1]) / (num_points - 1),
        )
        for i in range(num_points)
    ]


def is_edge_valid(
    point1, point2, obstacles, scale_x, scale_y, offset_x, offset_y, size=(25, 25)
):
    interpolated_points = interpolate_points(point1, point2)
    for point in interpolated_points:
        if is_point_inside_any_obstacle(
            point, obstacles, scale_x, scale_y, offset_x, offset_y, size
        ):
            return False
    return True


# functions to improve roadmap
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

    # print(f"Number of loops removed: {len(remove_list)}")

    return roadmap


def is_in_cluster(new_point, current_points, min_dist=30):
    for point in current_points:
        if np.linalg.norm(np.array(new_point) - np.array(point)) < min_dist:
            return True
    return False


# roadmap creation
def build_roadmap(
    num_points,
    connection_radius,
    game_area,
    obstacles,
    scale_x,
    scale_y,
    offset_x,
    offset_y,
):
    points = []
    roadmap = {}
    while len(points) < num_points:
        point = (random.uniform(0, game_area[0]), random.uniform(0, game_area[1]))
        if not is_point_inside_any_obstacle(
            point, obstacles, scale_x, scale_y, offset_x, offset_y, size=(25, 25)
        ) and not is_in_cluster(point, points):
            points.append(point)
    for i, point in enumerate(points):
        roadmap[i] = []
        for j, other_point in enumerate(points):
            if (
                i != j
                and np.linalg.norm(np.array(point) - np.array(other_point))
                < connection_radius
            ):
                if is_edge_valid(
                    point,
                    other_point,
                    obstacles,
                    scale_x,
                    scale_y,
                    offset_x,
                    offset_y,
                    size=(25, 25),
                ):
                    roadmap[i].append(j)
    remove_loops(roadmap)
    return roadmap, points


# pathfinding logic for enemy
def heuristic(current_point, player_position):
    return np.linalg.norm(np.array(current_point) - np.array(player_position))


def closest_point_index(position, points):
    return min(
        range(len(points)),
        key=lambda i: np.linalg.norm(np.array(position) - np.array(points[i])),
    )


def find_path(start_idx, roadmap, points, player_position):
    frontier = PriorityQueue()
    frontier.put(start_idx, 0)
    came_from = {start_idx: None}
    cost_so_far = {start_idx: 0}

    while not frontier.empty():
        current = frontier.pop()
        current_point = points[current]

        if heuristic(current_point, player_position) < 0.5:
            break

        for next_idx in roadmap[current]:
            next_point = points[next_idx]
            new_cost = cost_so_far[current] + np.linalg.norm(
                np.array(current_point) - np.array(next_point)
            )
            if next_idx not in cost_so_far or new_cost < cost_so_far[next_idx]:
                cost_so_far[next_idx] = new_cost
                priority = new_cost * 2 + heuristic(next_point, player_position)
                frontier.put(next_idx, priority)
                came_from[next_idx] = current

    path = [current]
    while came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()

    return path


def update_enemy_path(enemy, player_position, roadmap, points):
    if not enemy.locked_on_path:
        goal_idx = closest_point_index(player_position, points)
        path_indices = find_path(goal_idx, roadmap, points, player_position)
        enemy.path = [points[i] for i in path_indices]


def get_direction(dx, dy):
    norm = np.sqrt(dx**2 + dy**2)
    return (dx / norm, dy / norm)  # Normalize the direction vector

def get_distance_category(distance):
    # Example thresholds, adjust based on your game's scale
    if distance < 100:
        return "close"
    elif distance < 200:
        return "medium"
    else:
        return "far"


def quantify_state(direction, distance, obstacle_proximity):
    # This method should convert the qualitative state description into a numeric or otherwise hashable state
    # For simplicity, you can concatenate the state components if your state space is not too large
    return f"{direction}_{distance}_{obstacle_proximity}"


def calculate_reward(player_position, new_enemy_position, old_enemy_position):
    # Calculate Euclidean distance to the player before and after the move
    distance_before = np.sqrt(
        (old_enemy_position[0] - player_position[0]) ** 2
        + (old_enemy_position[1] - player_position[1]) ** 2
    )
    distance_after = np.sqrt(
        (new_enemy_position[0] - player_position[0]) ** 2
        + (new_enemy_position[1] - player_position[1]) ** 2
    )

    # Reward for getting closer, penalty for moving away
    if distance_after < distance_before:
        return 1  # Reward for moving closer
    else:
        return -1  # Penalty for moving away or staying the same


class HidingSpot(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((64, 64, 64))  # Example color: dark grey
        self.rect = self.image.get_rect(topleft=(x, y))
