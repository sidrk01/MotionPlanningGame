import numpy as np

class QLearningAgent:
    def __init__(self, state_space_size=100, action_space_size=4, learning_rate=0.1, discount_factor=0.95, exploration_rate=1.0, exploration_decay=0.99):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.q_table = np.zeros((state_space_size, action_space_size))

    def update_q_table(self, current_state, action, reward, next_state):
        next_max = np.max(self.q_table[next_state])
        self.q_table[current_state, action] = self.q_table[current_state, action] + \
                                              self.learning_rate * (reward + self.discount_factor * next_max - self.q_table[current_state, action])

    def choose_action(self, current_state):
        if np.random.rand() < self.exploration_rate:
            return np.random.randint(4)  # Assuming 4 actions: up, down, left, right
        return np.argmax(self.q_table[current_state])

    def decay_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay
