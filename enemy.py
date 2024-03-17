import pygame
import numpy as np
import random
from math import sin, cos, pi
from utils import scale_points
from utils import heuristic

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

        # Q-learning attributes
        self.is_qlearning = False
        self.q_table = np.zeros((1000, 1000, 8))  # Adjust grid size and actions
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2
        self.actions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def discretize_state(self, position):
        # Convert continuous position to discrete grid state
        grid_x = int(position[0])  # Adjust division factor based on screen size
        grid_y = int(position[1])  # and desired grid size
        return (grid_x, grid_y)

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(8)  # Explore action space
        else:
            return np.argmax(self.q_table[state])  # Exploit learned values

    def update_q_value(self, state, action, reward, next_state):
        future_rewards = np.max(self.q_table[next_state])
        current_q = self.q_table[state + (action,)]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * future_rewards - current_q)
        self.q_table[state + (action,)] = new_q


    def next_q_move(self, action):
        # Implement how the enemy moves based on the chosen action
        dx, dy = self.actions[action]
        return np.array([dx, dy])  # Adjust movement distance as necessary

    def get_reward(self, player_position):
        # Define how rewards are assigned
        distance = np.linalg.norm(self.position - player_position)
        if distance < 33:  # Example condition
            return 100  # Found the player
        return -distance / 100  # Encourage moving closer

    def reset(self, start_pos):
        self.position = np.array(start_pos, dtype=float)

    def set_params(self, speed, following_roadmap, destination, color=red):
        self.speed = speed
        self.following_roadmap = following_roadmap
        self.destination = destination
        self.surf.fill(color)

    def reset(self, start_pos):
        self.position = np.array(start_pos, dtype=float)

    def update_position(
        self,
        obstacles,
        scale_x,
        scale_y,
        offset_x,
        offset_y,
        get_other_enemies_positions,
        current_time,
        player_position,
        is_player_hiding,
    ):
        self.get_other_enemies_positions = get_other_enemies_positions
        self.current_time = current_time

        if is_player_hiding():
            self.patrol(obstacles, scale_x, scale_y, offset_x, offset_y)
            return

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

                if self.is_qlearning:
                    current_state = self.discretize_state(self.position)
                    action = self.choose_action(current_state)
                    next_state = self.discretize_state( self.next_q_move(action) )
                    reward = self.get_reward(player_position)
                    self.update_q_value(current_state, action, reward, next_state)

                if not self.collides_with_obstacles(
                    new_position, obstacles, scale_x, scale_y, offset_x, offset_y
                ):
                    self.position = new_position
                    self.rect.center = self.position
                else:
                    if not self.following_roadmap:
                        self.set_nearest_roadmap_path(player_position)

        self.last_position = np.array(self.position)

    def move_along_path(self, obstacles, scale_x, scale_y, offset_x, offset_y):
        if len(self.path) > 0:
            destination = np.array(self.path[0])
            direction = destination - self.position
            new_position = (
                self.position + direction / np.linalg.norm(direction) * self.speed
            )

        if not self.collides_with_obstacles(
            new_position, obstacles, scale_x, scale_y, offset_x, offset_y
        ):
            self.position = new_position
            self.rect.center = self.position

            if np.linalg.norm(direction) < self.speed:
                self.path.pop(0)

    def set_nearest_roadmap_path(self, player_position):
        if self.points:
            closest_indices = sorted(
                range(len(self.points)),
                key=lambda i: np.linalg.norm(self.position - np.array(self.points[i])),
            )[:5]

        if self.is_qlearning:
            states = [self.discretize_state(np.array(self.points[i])) for i in closest_indices]

            # Check future rewards for each of these states based on the Q-table and choose the state with the highest expected reward
            best_future_reward = -np.inf
            best_action = None
            best_index = None

            current_state = self.discretize_state(self.position)
            for i, state in enumerate(states):
                for action in range(len(self.actions)):
                    potential_future_state = (state[0], state[1], action)
                    if self.q_table[potential_future_state] > best_future_reward:
                        best_future_reward = self.q_table[potential_future_state]
                        best_action = action
                        best_index = closest_indices[i]

            if best_action is not None:
                self.path = [self.points[best_index]]
                reward = self.get_reward(player_position)
                next_state = self.discretize_state(np.array(self.path[0]))
                self.update_q_value(current_state, best_action, reward, next_state)
            else:
                self.path = [self.points[closest_indices[0]]] 
        else:
            self.path = [self.points[i] for i in closest_indices]
            self.locked_on_path = True
            self.locked_time = self.current_time + 3000

    def collides_with_obstacles(
        self, new_position, obstacles, scale_x, scale_y, offset_x, offset_y
    ):
        num_points = 100
        angles = np.linspace(0, 2 * pi, num_points, endpoint=False)
        points = [
            (
                self.radius * cos(angle) + new_position[0],
                self.radius * sin(angle) + new_position[1],
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

    def patrol(self, obstacles, scale_x, scale_y, offset_x, offset_y):
        # Example simple patrol method: change direction randomly
        if (
            not hasattr(self, "patrol_direction") or random.randint(0, 20) == 0
        ):  # Change direction occasionally
            self.patrol_direction = (random.uniform(-1, 1), random.uniform(-1, 1))

        # Move in the chosen direction
        new_position = self.position + np.array(self.patrol_direction) * self.speed
        # Check if moving would cause a collision
        if not self.collides_with_obstacles(
            new_position, obstacles, scale_x, scale_y, offset_x, offset_y
        ):
            self.position = new_position
            self.rect.center = self.position
