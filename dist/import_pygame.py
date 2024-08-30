import pygame
import random
import os
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the game window
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game states
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    SHOP = 3

# Power-up types
class PowerUp(Enum):
    NONE = 0
    IMMUNITY = 1
    SLOW_MOTION = 2

# Game variables
high_score = 0
coins = 0

# Bird properties
bird_x = 50
bird_y = HEIGHT // 2
bird_radius = 20
bird_velocity = 0
gravity = 0.5
jump_strength = -10

# Pipe properties
pipe_width = 50
pipe_gap = 200
pipe_x = WIDTH
pipe_height = random.randint(100, 400)

# Cloud properties
cloud_width = 80
cloud_height = 40
clouds = []

# Score and currency
score = 0
high_score = 0
coins = 0
difficulty = 1
pipe_speed = 3

# Fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Game state
game_state = GameState.MENU

# Load sounds
jump_sound = pygame.mixer.Sound("jump.mp3")
score_sound = pygame.mixer.Sound("score.mp3")
game_over_sound = pygame.mixer.Sound("game_over.mp3")
power_up_sound = pygame.mixer.Sound("power_up.mp3")

# Load bird images
bird_images = {
    "blue": pygame.image.load("bird_blue.png"),
    
}

# Scale bird images if necessary
for color in bird_images:
    bird_images[color] = pygame.transform.scale(bird_images[color], (bird_radius * 2, bird_radius * 2))

# Load and scale background images
bg_day = pygame.image.load("bg_day.png")
bg_day = pygame.transform.scale(bg_day, (WIDTH, HEIGHT))
bg_night = pygame.image.load("bg_night.png")
bg_night = pygame.transform.scale(bg_night, (WIDTH, HEIGHT))

# Day/Night cycle
day_night_cycle = 0
is_day = True

# Bird colors and upgrades
bird_colors = [BLUE, RED, YELLOW, GREEN]
current_bird_color = 0
unlocked_colors = [True, False, False, False]

# Power-up properties
current_power_up = PowerUp.NONE
power_up_duration = 0
immunity_duration = 300  # 5 seconds at 60 FPS
slow_motion_duration = 300
slow_motion_factor = 0.5

# Shop items
shop_items = [
    {"name": "Red Bird", "cost": 50, "type": "color", "index": 1},
    {"name": "Yellow Bird", "cost": 100, "type": "color", "index": 2},
    {"name": "Green Bird", "cost": 150, "type": "color", "index": 3},
    {"name": "Immunity", "cost": 30, "type": "power_up", "power_up": PowerUp.IMMUNITY},
    {"name": "Slow Motion", "cost": 40, "type": "power_up", "power_up": PowerUp.SLOW_MOTION}
]



def reset_game():
    global bird_y, bird_velocity, pipe_x, pipe_height, score, game_state, difficulty, pipe_speed, current_power_up, power_up_duration, clouds
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipe_x = WIDTH
    pipe_height = random.randint(100, 400)
    score = 0
    game_state = GameState.PLAYING
    difficulty = 1
    pipe_speed = 3
    current_power_up = PowerUp.NONE
    power_up_duration = 0
    clouds = []

def update_high_score():
    global high_score
    if score > high_score:
        high_score = score
    save_game_data()

# Load high score


def save_game_data():
    global high_score, coins
    with open("game_data.txt", "w") as f:
        f.write(f"{high_score},{coins}")

def load_game_data():
    global high_score, coins
    if os.path.exists("game_data.txt"):
        with open("game_data.txt", "r") as f:
            data = f.read().split(',')
            high_score = int(data[0])
            coins = int(data[1])

load_game_data()

def draw_menu():
    screen.blit(bg_day if is_day else bg_night, (0, 0))
    title = big_font.render("Flappy Bird", True, WHITE)
    start = font.render("Press SPACE to Start", True, WHITE)
    shop = font.render("Press S for Shop", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
    screen.blit(shop, (WIDTH // 2 - shop.get_width() // 2, HEIGHT * 3 // 4))

def draw_game():
    screen.blit(bg_day if is_day else bg_night, (0, 0))

    # Draw clouds
    for cloud in clouds:
        pygame.draw.ellipse(screen, WHITE, cloud)

    # Draw bird
    bird_image = bird_images[list(bird_images.keys())[current_bird_color]]
    bird_rect = bird_image.get_rect(center=(int(bird_x), int(bird_y)))
    if current_power_up == PowerUp.IMMUNITY:
        pygame.draw.circle(screen, WHITE, (int(bird_x), int(bird_y)), bird_radius + 5)
    screen.blit(bird_image, bird_rect)

    # Draw pipes
    pygame.draw.rect(screen, GREEN, (pipe_x, 0, pipe_width, pipe_height))
    pygame.draw.rect(screen, GREEN, (pipe_x, pipe_height + pipe_gap, pipe_width, HEIGHT - pipe_height - pipe_gap))

    # Draw score and coins
    score_text = font.render(f"Score: {score}", True, WHITE)
    coins_text = font.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(score_text, (10, 10))
    screen.blit(coins_text, (10, 50))

    # Draw power-up indicator
    if current_power_up != PowerUp.NONE:
        power_up_text = font.render(f"{current_power_up.name}: {power_up_duration // 60}s", True, WHITE)
        screen.blit(power_up_text, (WIDTH - power_up_text.get_width() - 10, 10))

    # Draw high score
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 50))

    #draw bird velocity
    angle = -bird_velocity * 2  # Adjust multiplier for desired rotation speed
    rotated_bird = pygame.transform.rotate(bird_image, angle)
    bird_rect = rotated_bird.get_rect(center=(int(bird_x), int(bird_y)))
    screen.blit(rotated_bird, bird_rect)

def draw_game_over():
    screen.blit(bg_day if is_day else bg_night, (0, 0))
    game_over_text = big_font.render("Game Over", True, WHITE)
    final_score = font.render(f"Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    menu_text = font.render("Press M for Menu", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
    screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT * 3 // 4 - 30))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT * 3 // 4 + 30))

def draw_shop():
    screen.blit(bg_day if is_day else bg_night, (0, 0))
    shop_title = big_font.render("Shop", True, WHITE)
    screen.blit(shop_title, (WIDTH // 2 - shop_title.get_width() // 2, 20))

    coins_text = font.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(coins_text, (10, 10))

    for i, item in enumerate(shop_items):
        item_text = font.render(f"{item['name']}: {item['cost']} coins", True, WHITE)
        if (item['type'] == 'color' and unlocked_colors[item['index']]) or \
           (item['type'] == 'power_up' and coins >= item['cost']):
            pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 100, 100 + i * 50, 200, 40))
        else:
            pygame.draw.rect(screen, RED, (WIDTH // 2 - 100, 100 + i * 50, 200, 40))
        screen.blit(item_text, (WIDTH // 2 - item_text.get_width() // 2, 105 + i * 50))

    back_text = font.render("Press B to go back", True, WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

def handle_shop_purchase(mouse_pos):
    global coins, current_bird_color, unlocked_colors, current_power_up
    for i, item in enumerate(shop_items):
        if WIDTH // 2 - 100 <= mouse_pos[0] <= WIDTH // 2 + 100 and 100 + i * 50 <= mouse_pos[1] <= 140 + i * 50:
            if item['type'] == 'color' and not unlocked_colors[item['index']] and coins >= item['cost']:
                coins -= item['cost']
                unlocked_colors[item['index']] = True
            elif item['type'] == 'power_up' and coins >= item['cost']:
                coins -= item['cost']
                current_power_up = item['power_up']
                power_up_sound.play()

def spawn_cloud():
    cloud_x = WIDTH
    cloud_y = random.randint(0, HEIGHT // 2)
    clouds.append(pygame.Rect(cloud_x, cloud_y, cloud_width, cloud_height))

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == GameState.MENU:
                    reset_game()
                elif game_state == GameState.PLAYING:
                    bird_velocity = jump_strength
                    jump_sound.play()
                elif game_state == GameState.GAME_OVER:
                    game_state = GameState.MENU
            elif event.key == pygame.K_s and game_state == GameState.MENU:
                game_state = GameState.SHOP
            elif event.key == pygame.K_b and game_state == GameState.SHOP:
                game_state = GameState.MENU
            elif event.key == pygame.K_m and game_state == GameState.GAME_OVER:
                game_state = GameState.MENU
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == GameState.SHOP:
            handle_shop_purchase(event.pos)

    if game_state == GameState.PLAYING:
        # Update bird position
        bird_velocity += gravity
        bird_y += bird_velocity

        # Move pipe
        if current_power_up == PowerUp.SLOW_MOTION:
            pipe_x -= pipe_speed * slow_motion_factor
        else:
            pipe_x -= pipe_speed

        if pipe_x < -pipe_width:
            pipe_x = WIDTH
            pipe_height = random.randint(100, 400)
            score += 1
            coins += 1
            score_sound.play()

            # Increase difficulty
            if score % 5 == 0:
                difficulty += 1
                pipe_speed = min(3 + difficulty * 0.5, 10)  # Cap speed at 10

        # Move clouds
        for cloud in clouds:
            cloud.x -= 1
        clouds = [cloud for cloud in clouds if cloud.right > 0]

        # Spawn new cloud
        if random.random() < 0.01:
            spawn_cloud()

        # Check for collisions
        bird_rect = bird_images[list(bird_images.keys())[current_bird_color]].get_rect(center=(int(bird_x), int(bird_y)))
        collision = (bird_rect.top < 0 or bird_rect.bottom > HEIGHT or
                        (bird_rect.right > pipe_x and bird_rect.left < pipe_x + pipe_width and
                            (bird_rect.top < pipe_height or bird_rect.bottom > pipe_height + pipe_gap)))

        if collision and current_power_up != PowerUp.IMMUNITY:
            game_state = GameState.GAME_OVER
            game_over_sound.play()
            update_high_score()

        # Update power-up duration
        if current_power_up != PowerUp.NONE:
            power_up_duration -= 1
            if power_up_duration <= 0:
                current_power_up = PowerUp.NONE

        # Day/Night cycle
        day_night_cycle += 1
        if day_night_cycle >= 1800:  # Change every 30 seconds
            day_night_cycle = 0
            is_day = not is_day

    # Draw the appropriate screen based on game state
    if game_state == GameState.MENU:
        draw_menu()
    elif game_state == GameState.PLAYING:
        draw_game()
    elif game_state == GameState.GAME_OVER:
        draw_game_over()
    elif game_state == GameState.SHOP:
        draw_shop()

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

    save_game_data()

pygame.quit()