import pygame
import sys
from utils import *
from obstacles import load_obstacles
from player import Player
from enemy import Enemy

white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
gray = (128, 128, 128)
black = (0, 0, 0)
green = (0, 255, 0) 
gold = (255, 215, 0)

pygame.init()
font = pygame.font.Font(None, 74)
screen_width, screen_height = 1000, 1000
screen = pygame.display.set_mode((screen_width, screen_height))
obstacles = load_obstacles('maze.csv')

#map and scaling parameters
map_x_min = min(obstacle.x_min for obstacle in obstacles)
map_x_max = max(obstacle.x_max for obstacle in obstacles)
map_y_min = min(obstacle.y_min for obstacle in obstacles)
map_y_max = max(obstacle.y_max for obstacle in obstacles)

scale_x = screen_width / (map_x_max - map_x_min)
scale_y = screen_height / (map_y_max - map_y_min)
offset_x = -map_x_min * scale_x
offset_y = -map_y_min * scale_y


timer_start = 55
timer = timer_start
last_count = pygame.time.get_ticks()

#menu helper fns
def quit_or_reset():
    input_wait = True
    while input_wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    input_wait = False

def pause_or_reset():
    reset = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return reset
                elif event.key == pygame.K_r:
                    reset = True
                    return reset

def restart_screen():
    screen.fill(black) 
    restart_text = font.render('Game Over! Press R to Restart', True, white)
    text_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(restart_text, text_rect)
    pygame.display.flip()
    quit_or_reset()

def win_screen():
    screen.fill(gold) 
    win_text = font.render('You Win! Press R to Restart', True, white)
    text_rect = win_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(win_text, text_rect)
    pygame.display.flip()
    quit_or_reset()

def pause_screen():
    screen.fill(green) 
    pause_text = font.render('Game Paused', True, white)
    text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(pause_text, text_rect)

    small_font = pygame.font.Font(None, 35) 
    continue_text = small_font.render('Press P to Continue', True, white)
    continue_rect = continue_text.get_rect(center=(screen_width // 2, screen_height // 2 + 10))
    screen.blit(continue_text, continue_rect)

    restart_text = small_font.render('Press R to Restart', True, white)
    restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2 + 45))
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()
    return pause_or_reset()


def main():
    #player char
    player = Player()

    #slow enemy agent (prm)
    enemy_slow = Enemy(start_pos=[250,500])
    enemy_slow.set_params(1, False, None)
    
    #fast enemy agent (prm)
    enemy_fast = Enemy(start_pos=[750,400])
    enemy_fast.set_params(3, True, None)

    last_update_time = 0
    path_update_interval = 1000

    players = pygame.sprite.Group()
    players.add(player)
    enemies = pygame.sprite.Group()
    enemies.add(enemy_slow)
    enemies.add(enemy_fast)
    clock = pygame.time.Clock()
    global timer, last_count
    
    num_points = 200
    connection_radius = 200
    game_area = (screen_width, screen_height) 
    roadmap, points = build_roadmap(num_points, connection_radius, game_area, obstacles, scale_x, scale_y, offset_x, offset_y)
    
    enemy_slow.set_roadmap(roadmap, points)
    enemy_fast.set_roadmap(roadmap, points)

    show_roadmap = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                show_roadmap = not show_roadmap
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    choice = pause_screen()
                    if choice:
                        enemy_slow.reset([250,500])
                        enemy_fast.reset([750,400])
                        timer = timer_start
                elif event.key == pygame.K_r:
                    enemy_slow.reset([250,500])
                    enemy_fast.reset([750,400])
                    roadmap, points = build_roadmap(num_points, connection_radius, game_area, obstacles, scale_x, scale_y, offset_x, offset_y)

                    timer = timer_start

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


        player_pos = player.position
        update_enemy_path(enemy_slow, player_pos, roadmap, points)
        update_enemy_path(enemy_fast, player_pos, roadmap, points)
        
        #NOTE:uncommment debug line for enemy pathfinding
        #for i in range(len(enemy_slow.path) - 1):
            #pygame.draw.line(screen, pygame.Color('red'), enemy_slow.path[i], enemy_slow.path[i + 1], 5)

        #for i in range(len(enemy_fast.path) - 1):
            #pygame.draw.line(screen, pygame.Color('green'), enemy_fast.path[i], enemy_fast.path[i + 1], 5)
        
        #speedup at 30 secs
        if timer == 30:
            enemy_slow.set_params(3, True, None)

        player_pos = player.position
        # Update each enemy with the new logic
        for enemy in enemies:
            enemy.update(player_pos)
            
        for enemy in enemies:
            other_enemies_positions = lambda e=enemy: [e.position for e in enemies if e != enemy]
            enemy.update_position(obstacles, scale_x, scale_y, offset_x, offset_y, other_enemies_positions, current_time)
        
        #timer updates
        timer_text = font.render(str(timer), True, black)
        text_rect = timer_text.get_rect(center=(screen_width // 2, 50))

        #player updates
        screen.blit(timer_text, text_rect)
        screen.blit(player.image, player.rect)

        #enemy display updates
        scaled_enemy_pos = scale_points([enemy_slow.position], scale_x, scale_y, offset_x, offset_y)[0]
        enemy_slow.rect.x, enemy_slow.rect.y = scaled_enemy_pos
        enemy_slow.rect.x, enemy_slow.rect.y = enemy_slow.position  
        screen.blit(enemy_slow.surf, enemy_slow.rect)

        scaled_enemy_pos = scale_points([enemy_fast.position], scale_x, scale_y, offset_x, offset_y)[0]
        enemy_fast.rect.x, enemy_fast.rect.y = scaled_enemy_pos
        enemy_fast.rect.x, enemy_fast.rect.y = enemy_fast.position  
        screen.blit(enemy_fast.surf, enemy_fast.rect)

        if show_roadmap:
            draw_prm_roadmap(screen, roadmap, points)

        if pygame.sprite.collide_rect(player, enemy_slow):
            restart_screen()
            player.reset()
            enemy_slow.reset([250,500])
            enemy_fast.reset([750,400])
            timer = timer_start 
        
        if pygame.sprite.collide_rect(player, enemy_fast):
            restart_screen()
            player.reset()
            enemy_slow.reset([250,500])
            enemy_fast.reset([750,400])
            timer = timer_start 

        pygame.display.flip()
        clock.tick(30) 

        if timer <= 0:
            win_screen()
            player.reset()
            enemy_slow.reset([250,500])
            enemy_fast.reset([750,400])
            timer = timer_start

if __name__ == "__main__":
    main()