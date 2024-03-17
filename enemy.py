import pygame
from q_learning_agent import QLearningAgent
red = (255, 0, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(red)
        self.rect = self.surf.get_rect(center=(200, 300))
        self.ai = QLearningAgent()  # Initialize the Q-Learning agent here
    
    def get_current_state(self, game_state):
        # Implement the logic to determine the current state
        # This might involve calculating the relative position of the enemy to the player
        # and converting that into a state index or representation
        state = 0  # Placeholder value
        return state

    def update(self, game_state, player):
        # Implement the logic to update the enemy's position based on Q-Learning
        current_state = self.get_current_state(game_state)
        action = self.ai.choose_action(current_state)
        self.execute_action(action, game_state)  # You'll need to implement this method
        next_state = self.get_current_state(game_state)  # Get new state after action
        # reward = self.get_reward(next_state, player)  # Implement reward logic
        reward = self.get_reward(player)  # Implement reward logic
        self.ai.update_q_table(current_state, action, reward, next_state)
        self.ai.decay_exploration_rate()

    def execute_action(self, action, game_state):
        # Define the action execution logic here
        speed = 5  # Adjust as necessary for your game's scale
        if action == 0:  # Up
            self.rect.move_ip(0, -speed)
        elif action == 1:  # Down
            self.rect.move_ip(0, speed)
        elif action == 2:  # Left
            self.rect.move_ip(-speed, 0)
        elif action == 3:  # Right
            self.rect.move_ip(speed, 0)
        # Add additional conditions for other actions if necessary
            
    def get_reward(self, player):
        # Simple reward function that prioritizes getting closer to the player
        # Calculate the distance between the enemy and the player before and after the move
        # For simplicity, this example assumes you have access to player_position and the enemy's previous position (prev_position)
        # new_distance = self.calculate_distance(self.rect.center, player.rect.center)
        # prev_distance = self.calculate_distance(self.prev_position, player.rect.center)

        new_distance = self.calculate_distance(self.rect.center, self.rect.center)
        prev_distance = self.calculate_distance(self.rect.center, self.rect.center)

        # Check for collision or reaching the player - these would require additional logic
        collision = False  # Placeholder for actual collision detection
        reached_player = new_distance < 10  # Define some_threshold as appropriate

        if collision:
            return -100  # Large negative reward for collision
        elif reached_player:
            return 100  # Large positive reward for reaching the player
        elif new_distance < prev_distance:
            return 10  # Positive reward for getting closer
        else:
            return -10  # Negative reward for getting further away or no improvement

    def calculate_distance(self, point_a, point_b):
        # A simple method to calculate the distance between two points
        return ((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2) ** 0.5