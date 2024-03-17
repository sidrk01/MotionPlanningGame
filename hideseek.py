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
enemy_slow_start_pos = [250, 500]
enemy_fast_start_pos = [300, 400]
enemy_faster_start_pos = [700, 400]
enemy_qlearning_start_pos = [700, 400]

pygame.init()
font = pygame.font.Font(None, 74)
screen_width, screen_height = 1000, 1000
screen = pygame.display.set_mode((screen_width, screen_height))
obstacles = load_obstacles("maze.csv")

# map and scaling parameters
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


# menu helper fns
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
    restart_text = font.render("Game Over! Press R to Restart", True, white)
    text_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(restart_text, text_rect)
    pygame.display.flip()
    quit_or_reset()


def win_screen():
    screen.fill(gold)
    win_text = font.render("You Win! Press R to Restart", True, white)
    text_rect = win_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(win_text, text_rect)
    pygame.display.flip()
    quit_or_reset()


def pause_screen():
    screen.fill(green)
    pause_text = font.render("Game Paused", True, white)
    text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(pause_text, text_rect)

    small_font = pygame.font.Font(None, 35)
    continue_text = small_font.render("Press P to Continue", True, white)
    continue_rect = continue_text.get_rect(
        center=(screen_width // 2, screen_height // 2 + 10)
    )
    screen.blit(continue_text, continue_rect)

    restart_text = small_font.render("Press R to Restart", True, white)
    restart_rect = restart_text.get_rect(
        center=(screen_width // 2, screen_height // 2 + 45)
    )
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()
    return pause_or_reset()


def main():
    # player char
    player = Player()

    # slow enemy agent (prm)
    enemy_slow = Enemy(start_pos=enemy_slow_start_pos)
    enemy_slow.set_params(1, True, None)

    # fast enemy agent (prm)
    enemy_fast = Enemy(start_pos=enemy_fast_start_pos)
    enemy_fast.set_params(2, True, None)

    # faster enemy agent (prm)
    # enemy_faster = Enemy(start_pos=enemy_faster_start_pos)
    # enemy_faster.set_params(3, True, None)

    # faster enemy agent (prm)
    enemy_qlearning = Enemy(start_pos=enemy_qlearning_start_pos)
    enemy_qlearning.set_params(3, True, None)
    enemy_qlearning.is_qlearning = True
    enemy_qlearning.surf.fill(green)

    last_update_time = 0
    path_update_interval = 1000

    players = pygame.sprite.Group()
    players.add(player)
    enemies = pygame.sprite.Group()
    enemies.add(enemy_slow)
    enemies.add(enemy_fast)
    # enemies.add(enemy_faster)
    enemies.add(enemy_qlearning)
    clock = pygame.time.Clock()
    global timer, last_count

    num_points = 200
    connection_radius = 200
    game_area = (screen_width, screen_height)
    roadmap, points = build_roadmap(
        num_points,
        connection_radius,
        game_area,
        obstacles,
        scale_x,
        scale_y,
        offset_x,
        offset_y,
    )

    for enemy in enemies:
        enemy.set_roadmap(roadmap, points)

    show_roadmap = False

    def enemies_reset():
        enemy_slow.reset(enemy_slow_start_pos)
        enemy_fast.reset(enemy_fast_start_pos)
        # enemy_faster.reset(enemy_faster_start_pos)
        enemy_qlearning.reset(enemy_qlearning_start_pos)

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
                        enemies_reset()
                        timer = timer_start
                elif event.key == pygame.K_r:
                    enemies_reset()
                    roadmap, points = build_roadmap(
                        num_points,
                        connection_radius,
                        game_area,
                        obstacles,
                        scale_x,
                        scale_y,
                        offset_x,
                        offset_y,
                    )

                    timer = timer_start

        pressed_keys = pygame.key.get_pressed()

        hiding_spots = pygame.sprite.Group(
            HidingSpot(300, 300, 50, 50), HidingSpot(200, 400, 50, 50)
        )

        player.update(
            pressed_keys, obstacles, hiding_spots, scale_x, scale_y, offset_x, offset_y
        )

        screen.fill(white)
        for obstacle in obstacles:
            scaled_obstacle = scale_points(
                obstacle.points, scale_x, scale_y, offset_x, offset_y
            )
            pygame.draw.polygon(screen, gray, scaled_obstacle)

        for spot in hiding_spots:
            screen.blit(spot.image, spot.rect)

        current_time = pygame.time.get_ticks()
        if current_time - last_count >= 1000:
            timer -= 1
            last_count = current_time

        player_pos = player.position
        for enemy in enemies:
            update_enemy_path(enemy, player_pos, roadmap, points)

        # # NOTE:uncommment debug line for enemy pathfinding
        # for i in range(len(enemy_slow.path) - 1):
        #     pygame.draw.line(screen, pygame.Color('red'), enemy_slow.path[i], enemy_slow.path[i + 1], 5)

        # for i in range(len(enemy_fast.path) - 1):
        #     pygame.draw.line(screen, pygame.Color('green'), enemy_fast.path[i], enemy_fast.path[i + 1], 5)

        # for i in range(len(enemy_fast.path) - 1):
        #     pygame.draw.line(screen, pygame.Color('bkye'), enemy_faster.path[i], enemy_faster.path[i + 1], 5)

        # speedup at 30 secs
        if timer == 30:
            enemy_slow.set_params(3, True, None)

        player_pos = player.position
        # Update each enemy with the new logic
        for enemy in enemies:
            enemy.update(player_pos)

        for enemy in enemies:
            other_enemies_positions = lambda e=enemy: [
                e.position for e in enemies if e != enemy
            ]
            enemy.update_position(
                obstacles,
                scale_x,
                scale_y,
                offset_x,
                offset_y,
                other_enemies_positions,
                current_time,
                player.position,
                lambda: player.is_hiding
            )

        # timer updates
        timer_text = font.render(str(timer), True, black)
        text_rect = timer_text.get_rect(center=(screen_width // 2, 50))

        # player updates
        screen.blit(timer_text, text_rect)
        screen.blit(player.image, player.rect)

        # enemy display updates
        for enemy in enemies:
            scaled_enemy_pos = scale_points(
                [enemy.position], scale_x, scale_y, offset_x, offset_y
            )[0]
            enemy.rect.x, enemy.rect.y = scaled_enemy_pos
            enemy.rect.x, enemy.rect.y = enemy.position
            screen.blit(enemy.surf, enemy.rect)

        if show_roadmap:
            draw_prm_roadmap(screen, roadmap, points)

        if (
            pygame.sprite.collide_rect(player, enemy_slow)
            or pygame.sprite.collide_rect(player, enemy_fast)
            # or pygame.sprite.collide_rect(player, enemy_faster)
            or pygame.sprite.collide_rect(player, enemy_qlearning)
        ):
            restart_screen()
            player.reset()
            enemies_reset()
            timer = timer_start

        pygame.display.flip()
        clock.tick(30)

        if timer <= 0:
            win_screen()
            player.reset()
            enemies_reset()
            timer = timer_start


if __name__ == "__main__":
    main()
