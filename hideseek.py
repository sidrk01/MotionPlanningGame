import pygame
import sys
from obstacles import load_obstacles_from_csv

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load obstacles
obstacles = load_obstacles_from_csv('prm1.csv')

# Map limits for scaling
MAP_X_MIN = min(obstacle.x_min for obstacle in obstacles)
MAP_X_MAX = max(obstacle.x_max for obstacle in obstacles)
MAP_Y_MIN = min(obstacle.y_min for obstacle in obstacles)
MAP_Y_MAX = max(obstacle.y_max for obstacle in obstacles)

# Scaling factors
SCALE_X = SCREEN_WIDTH / (MAP_X_MAX - MAP_X_MIN)
SCALE_Y = SCREEN_HEIGHT / (MAP_Y_MAX - MAP_Y_MIN)
OFFSET_X = -MAP_X_MIN * SCALE_X
OFFSET_Y = -MAP_Y_MIN * SCALE_Y

# Player class modified to be a circle
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 12  # Half the size of the square to keep a similar size
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(400, 300))

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_w]: self.rect.move_ip(0, -5)
        if pressed_keys[pygame.K_s]: self.rect.move_ip(0, 5)
        if pressed_keys[pygame.K_a]: self.rect.move_ip(-5, 0)
        if pressed_keys[pygame.K_d]: self.rect.move_ip(5, 0)

# Enemy class (simplified)
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(RED)
        self.rect = self.surf.get_rect(center=(200, 300))

# Main game loop
def main():
    player = Player()
    enemy = Enemy()

    players = pygame.sprite.Group()
    players.add(player)

    enemies = pygame.sprite.Group()
    enemies.add(enemy)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        screen.fill(WHITE)  # Change the background color to white

        # Draw the scaled obstacles
        for obstacle in obstacles:
            scaled_points = [(x * SCALE_X + OFFSET_X, y * SCALE_Y + OFFSET_Y) for (x, y) in obstacle.points]
            pygame.draw.polygon(screen, GRAY, scaled_points)

        # Draw the player (now a circle) and the enemy
        screen.blit(player.image, player.rect)
        screen.blit(enemy.surf, enemy.rect)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
