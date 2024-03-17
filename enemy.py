import pygame
import numpy as np
import random
from math import sin, cos, pi
from utils import scale_points, get_direction, get_distance_category, quantify_state

red = (255, 0, 0)
import numpy as np


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
        # Q-learning
        self.num_states = 200 
        self.num_actions = 4  # Up, Down, Left, Right
        self.q_table = np.zeros((self.num_states, self.num_actions))
        self.state_to_index = {}  # Maps state representations to integer indices
        self.next_index = 0  # Keeps track of the next available index


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
                if not self.collides_with_obstacles(
                    new_position, obstacles, scale_x, scale_y, offset_x, offset_y
                ):
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

    def set_nearest_roadmap_path(self):
        if self.points:
            closest_indices = sorted(
                range(len(self.points)),
                key=lambda i: np.linalg.norm(self.position - np.array(self.points[i])),
            )[:5]
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

    def get_current_state(self, player_position, obstacles):
        # Determine relative direction and distance to the player
        dx = player_position[0] - self.rect.x
        dy = player_position[1] - self.rect.y

        direction = get_direction(dx, dy)
        distance = get_distance_category(np.sqrt(dx**2 + dy**2))

        # Check for immediate obstacle in direction to player
        obstacle_proximity = self._check_obstacle_proximity(obstacles, direction)

        # Convert to a unique state index or identifier
        state = quantify_state(direction, distance, obstacle_proximity)

        return state
    
    def _check_obstacle_proximity(self, obstacles, direction):
        start_point = (self.rect.centerx, self.rect.centery)
        # Simulate a move in the direction by a fixed distance (e.g., enemy's speed or a nominal distance)
        end_point = (start_point[0] + direction[0] * 10, start_point[1] + direction[1] * 10)  # Example: move 10 units towards the direction
        
        for obstacle in obstacles:
            if self._line_intersects_obstacle(start_point, end_point, obstacle):
                return "near"
        return "none"


    def _line_intersects_obstacle(self, start_point, end_point, obstacle):
        # Placeholder for line-obstacle intersection logic
        # You'd check if the line from start_point to end_point intersects with the obstacle's box
        # This requires implementing or using a line-box intersection algorithm
        
        # Simplified example checking if either point is within the obstacle
        if obstacle.contains_point(start_point, 1, 1, 0, 0) or obstacle.contains_point(end_point, 1, 1, 0, 0):
            return True
        return False

    def get_next_state(self, player_position, new_enemy_position, obstacles):
        return self.get_current_state(
            player_position, obstacles
        )  # Assuming this method exists and is applicable

    def get_state_index(self, state_representation):
        if state_representation not in self.state_to_index:
            if self.next_index >= self.num_states:
                raise ValueError(f"Attempting to generate a new state index {self.next_index} which exceeds the limit {self.num_states}")
            self.state_to_index[state_representation] = self.next_index
            self.next_index += 1
        return self.state_to_index[state_representation]


    def choose_action(self, state_representation, epsilon=0.1):
        state_index = self.get_state_index(state_representation)  # Convert to index
        if np.random.rand() < epsilon:
            return np.random.randint(self.num_actions)  # Explore
        else:
            return np.argmax(self.q_table[state_index])  # Exploit
        
    def execute_action(self, action):
        if action == 0:  # Move up
            self.rect.y -= self.speed
        elif action == 1:  # Move down
            self.rect.y += self.speed
        elif action == 2:  # Move left
            self.rect.x -= self.speed
        elif action == 3:  # Move right
            self.rect.x += self.speed
        elif action == 4:  # Stay still
            pass  # No movement
        # # Ensure the enemy does not move outside the game boundaries
        # self.rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height))

    def update_q_table(self, state_representation, action, reward, next_state_representation, alpha=0.1, gamma=0.9):
        # Convert state and next_state representations to integer indices
        state_index = self.get_state_index(state_representation)
        next_state_index = self.get_state_index(next_state_representation)

        # Find the maximum Q-value for the next state across all possible actions
        max_future_q = np.max(self.q_table[next_state_index])

        # Current Q-value for the specific action taken in the current state
        current_q = self.q_table[state_index, action]

        # Calculate the updated Q-value
        new_q = current_q + alpha * (reward + gamma * max_future_q - current_q)

        # Update the Q-table with the new Q-value
        self.q_table[state_index, action] = new_q

    def reset_learning(self):
        self.q_table = np.zeros((self.num_states, self.num_actions))
