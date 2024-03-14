import pygame
import sys
from obstacles import load_obstacles_from_csv

# Define colors
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
gray = (128, 128, 128)
black = (0, 0, 0)  # For the timer text

pygame.init()

# Screen dimensions
screen_width, screen_height = 1000, 1000
screen = pygame.display.set_mode((screen_width, screen_height))

# Load obstacles
obstacles = load_obstacles_from_csv('prm1.csv')

# Helper function to scale points
def scale_points(points, scale_x, scale_y, offset_x, offset_y):
    return [(x * scale_x + offset_x, y * scale_y + offset_y) for x, y in points]

# Scale factors and offsets
map_x_min = min(obstacle.x_min for obstacle in obstacles)
map_x_max = max(obstacle.x_max for obstacle in obstacles)
map_y_min = min(obstacle.y_min for obstacle in obstacles)
map_y_max = max(obstacle.y_max for obstacle in obstacles)
scale_x = screen_width / (map_x_max - map_x_min)
scale_y = screen_height / (map_y_max - map_y_min)
offset_x = -map_x_min * scale_x
offset_y = -map_y_min * scale_y

# Font for timer
font = pygame.font.Font(None, 74)

# Initialize the timer
timer_start = 20  # 100 seconds timer
timer = timer_start
last_count = pygame.time.get_ticks()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 12
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, blue, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(400, 300))

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_w]: self.rect.move_ip(0, -5)
        if pressed_keys[pygame.K_s]: self.rect.move_ip(0, 5)
        if pressed_keys[pygame.K_a]: self.rect.move_ip(-5, 0)
        if pressed_keys[pygame.K_d]: self.rect.move_ip(5, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((25, 25))
        self.surf.fill(red)
        self.rect = self.surf.get_rect(center=(200, 300))

def main():
    player = Player()
    enemy = Enemy()

    players = pygame.sprite.Group()
    players.add(player)

    enemies = pygame.sprite.Group()
    enemies.add(enemy)

    clock = pygame.time.Clock()

    global timer, last_count

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        screen.fill(white)

        # Draw the scaled obstacles
        for obstacle in obstacles:
            scaled_obstacle = scale_points(obstacle.points, scale_x, scale_y, offset_x, offset_y)
            pygame.draw.polygon(screen, gray, scaled_obstacle)

        # Update and render the timer
        current_time = pygame.time.get_ticks()
        if current_time - last_count >= 1000:  # One second passed
            timer -= 1
            last_count = current_time
        
        # Render the timer text
        timer_text = font.render(str(timer), True, black)
        text_rect = timer_text.get_rect(center=(screen_width // 2, 50))
        screen.blit(timer_text, text_rect)

        # Draw the player and the enemy
        screen.blit(player.image, player.rect)
        screen.blit(enemy.surf, enemy.rect)

        pygame.display.flip()
        clock.tick(30)

        # Check for game exit condition
        if timer <= 0:
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()