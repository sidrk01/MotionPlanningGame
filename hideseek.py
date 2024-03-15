import pygame
import sys
from utils import scale_points, draw_prm_roadmap, build_roadmap
from obstacles import load_obstacles
from player import Player
from enemy import Enemy

white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
gray = (128, 128, 128)
black = (0, 0, 0)

pygame.init()
font = pygame.font.Font(None, 74)
screen_width, screen_height = 1000, 1000
screen = pygame.display.set_mode((screen_width, screen_height))
obstacles = load_obstacles('maze.csv')

map_x_min = min(obstacle.x_min for obstacle in obstacles)
map_x_max = max(obstacle.x_max for obstacle in obstacles)
map_y_min = min(obstacle.y_min for obstacle in obstacles)
map_y_max = max(obstacle.y_max for obstacle in obstacles)

scale_x = screen_width / (map_x_max - map_x_min)
scale_y = screen_height / (map_y_max - map_y_min)
offset_x = -map_x_min * scale_x
offset_y = -map_y_min * scale_y

timer_start = 100
timer = timer_start
last_count = pygame.time.get_ticks()

def main():
    player = Player()
    enemy = Enemy()
    players = pygame.sprite.Group()
    players.add(player)
    enemies = pygame.sprite.Group()
    enemies.add(enemy)
    clock = pygame.time.Clock()
    global timer, last_count
    
    num_points = 300
    connection_radius = 100
    game_area = (screen_width, screen_height)  # Example game area, adjust as necessary
    roadmap, points = build_roadmap(num_points, connection_radius, game_area, obstacles)

    
    show_roadmap = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                show_roadmap = not show_roadmap

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys, obstacles, scale_x, scale_y, offset_x, offset_y)

        screen.fill(white)
        for obstacle in obstacles:
            scaled_obstacle = scale_points(obstacle.points, scale_x, scale_y, offset_x, offset_y)
            pygame.draw.polygon(screen, gray, scaled_obstacle)

        current_time = pygame.time.get_ticks()
        if current_time - last_count >= 1000:
            timer -= 1
            last_count = current_time

        timer_text = font.render(str(timer), True, black)
        text_rect = timer_text.get_rect(center=(screen_width // 2, 50))
        screen.blit(timer_text, text_rect)
        screen.blit(player.image, player.rect)
        screen.blit(enemy.surf, enemy.rect)

        if show_roadmap:
            draw_prm_roadmap(screen, roadmap, points)

        pygame.display.flip()
        clock.tick(30)

        if timer <= 0:
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
