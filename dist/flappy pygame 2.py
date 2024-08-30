import pygame
import random
import os
from enum import Enum
from datetime import datetime, timedelta

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
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game states
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    SHOP = 3
    ACHIEVEMENTS = 4

# Power-up types
class PowerUp(Enum):
    NONE = 0
    IMMUNITY = 1
    SLOW_MOTION = 2

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

# Boss properties
boss_width = 100
boss_height = 100
boss_x = WIDTH
boss_y = HEIGHT // 2
boss_health = 100
boss_velocity = 2

# Score and currency
score = 0
high_score = 0
coins = 0
level = 1

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
boss_hit_sound = pygame.mixer.Sound("boss_hit.mp3")

# Load images
bg_img = pygame.image.load("background.png")
bird_img = pygame.image.load("bird.png")
pipe_img = pygame.image.load("pipe.png")
boss_img = pygame.image.load("boss.png")

# Scale images
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
bird_img = pygame.transform.scale(bird_img, (bird_radius * 2, bird_radius * 2))
pipe_img = pygame.transform.scale(pipe_img, (pipe_width, HEIGHT))
boss_img = pygame.transform.scale(boss_img, (boss_width, boss_height))

# Particle system
particles = []

# Achievements
achievements = {
    "Beginner": {"description": "Score 10 points", "achieved": False},
    "Intermediate": {"description": "Score 50 points", "achieved": False},
    "Expert": {"description": "Score 100 points", "achieved": False},
    "Boss Slayer": {"description": "Defeat a boss", "achieved": False},
    "Shopaholic": {"description": "Buy all items from the shop", "achieved": False}
}

# Daily challenge
daily_challenge = {
    "description": "Score 20 points without using power-ups",
    "target": 20,
    "completed": False,
    "date": None
}

def reset_game():
    global bird_y, bird_velocity, pipe_x, pipe_height, score, game_state, level, boss_health, boss_x, boss_y
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipe_x = WIDTH
    pipe_height = random.randint(100, 400)
    score = 0
    game_state = GameState.PLAYING
    level = 1
    boss_health = 100
    boss_x = WIDTH
    boss_y = HEIGHT // 2

def save_game_data():
    global high_score, coins, achievements, daily_challenge
    with open("game_data.txt", "w") as f:
        f.write(f"{high_score},{coins}\n")
        for achievement, data in achievements.items():
            f.write(f"{achievement},{data['achieved']}\n")
        f.write(f"{daily_challenge['completed']},{daily_challenge['date']}\n")

def load_game_data():
    global high_score, coins, achievements, daily_challenge
    if os.path.exists("game_data.txt"):
        try:
            with open("game_data.txt", "r") as f:
                data = f.readlines()
                if len(data) >= 1:
                    high_score, coins = map(int, data[0].strip().split(','))
                for i, (achievement, _) in enumerate(achievements.items()):
                    if i + 1 < len(data):
                        achievement_data = data[i+1].strip().split(',')
                        if len(achievement_data) > 1:
                            achievements[achievement]['achieved'] = achievement_data[1] == 'True'
                if len(data) > len(achievements) + 1:
                    daily_challenge_data = data[-1].strip().split(',')
                    if len(daily_challenge_data) > 1:
                        daily_challenge['completed'] = daily_challenge_data[0] == 'True'
                        daily_challenge['date'] = datetime.strptime(daily_challenge_data[1], "%Y-%m-%d").date() if daily_challenge_data[1] != 'None' else None
        except Exception as e:
            print(f"Error loading game data: {e}")
            print("Starting with default values.")
            high_score = 0
            coins = 0
            for achievement in achievements:
                achievements[achievement]['achieved'] = False
            daily_challenge['completed'] = False
            daily_challenge['date'] = None
    else:
        print("No save file found. Starting with default values.")
        high_score = 0
        coins = 0
        for achievement in achievements:
            achievements[achievement]['achieved'] = False
        daily_challenge['completed'] = False
        daily_challenge['date'] = None

        
def update_achievements():
    global achievements
    if score >= 10:
        achievements["Beginner"]["achieved"] = True
    if score >= 50:
        achievements["Intermediate"]["achieved"] = True
    if score >= 100:
        achievements["Expert"]["achieved"] = True

def check_daily_challenge():
    global daily_challenge
    today = datetime.now().date()
    if daily_challenge['date'] != today:
        daily_challenge['description'] = f"Score {random.randint(10, 50)} points without using power-ups"
        daily_challenge['target'] = int(daily_challenge['description'].split()[1])
        daily_challenge['completed'] = False
        daily_challenge['date'] = today

def draw_menu():
    screen.blit(bg_img, (0, 0))
    title = big_font.render("Flappy Bird", True, WHITE)
    start = font.render("Press SPACE to Start", True, WHITE)
    shop = font.render("Press S for Shop", True, WHITE)
    achievements = font.render("Press A for Achievements", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
    screen.blit(shop, (WIDTH // 2 - shop.get_width() // 2, HEIGHT * 3 // 4 - 30))
    screen.blit(achievements, (WIDTH // 2 - achievements.get_width() // 2, HEIGHT * 3 // 4 + 30))

def draw_game():
    screen.blit(bg_img, (0, 0))
    screen.blit(bird_img, (bird_x - bird_radius, bird_y - bird_radius))
    screen.blit(pipe_img, (pipe_x, 0), (0, 0, pipe_width, pipe_height))
    screen.blit(pipe_img, (pipe_x, pipe_height + pipe_gap), (0, 0, pipe_width, HEIGHT - pipe_height - pipe_gap))
    
    if level % 5 == 0:  # Boss level
        screen.blit(boss_img, (boss_x, boss_y))
        pygame.draw.rect(screen, RED, (boss_x, boss_y - 20, boss_width * (boss_health / 100), 10))

    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    coins_text = font.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(coins_text, (10, 90))

    # Draw particles
    for particle in particles:
        pygame.draw.circle(screen, particle[3], (int(particle[0]), int(particle[1])), int(particle[2]))

def draw_game_over():
    screen.blit(bg_img, (0, 0))
    game_over_text = big_font.render("Game Over", True, WHITE)
    final_score = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    menu_text = font.render("Press M for Menu", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
    screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 + 30))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT * 3 // 4 - 30))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT * 3 // 4 + 30))

def draw_achievements():
    screen.blit(bg_img, (0, 0))
    title = big_font.render("Achievements", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    for i, (achievement, data) in enumerate(achievements.items()):
        color = GREEN if data['achieved'] else RED
        text = font.render(f"{achievement}: {data['description']}", True, color)
        screen.blit(text, (20, 100 + i * 40))

    back_text = font.render("Press B to go back", True, WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

def create_particle(x, y, color):
    particles.append([x, y, 5, color, 0.5])  # x, y, size, color, shrink_rate

def update_particles():
    for particle in particles:
        particle[0] += random.uniform(-1, 1)
        particle[1] += random.uniform(-1, 1)
        particle[2] -= particle[4]
        if particle[2] <= 0:
            particles.remove(particle)

# Game loop
clock = pygame.time.Clock()
running = True

load_game_data()
check_daily_challenge()

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
                    create_particle(bird_x, bird_y, BLUE)
                elif game_state == GameState.GAME_OVER:
                    game_state = GameState.MENU
            elif event.key == pygame.K_s and game_state == GameState.MENU:
                game_state = GameState.SHOP
            elif event.key == pygame.K_a and game_state == GameState.MENU:
                game_state = GameState.ACHIEVEMENTS
            elif event.key == pygame.K_b and (game_state == GameState.SHOP or game_state == GameState.ACHIEVEMENTS):
                game_state = GameState.MENU
            elif event.key == pygame.K_m and game_state == GameState.GAME_OVER:
                game_state = GameState.MENU

    if game_state == GameState.PLAYING:
        # Update bird position
        bird_velocity += gravity
        bird_y += bird_velocity

        # Move pipe
        pipe_x -= 3 + level * 0.5  # Increase speed with level

        if pipe_x < -pipe_width:
            pipe_x = WIDTH
            pipe_height = random.randint(100, 400)
            score += 1
            coins += 1
            level += 1
            score_sound.play()

        # Boss logic
        if level % 5 == 0:  # Boss level
            boss_x -= boss_velocity
            if boss_x < -boss_width:
                boss_x = WIDTH
                boss_health = 100

            # Boss collision
            if (bird_x + bird_radius > boss_x and bird_x - bird_radius < boss_x + boss_width and
                bird_y + bird_radius > boss_y and bird_y - bird_radius < boss_y + boss_height):
                boss_health -= 10
                boss_hit_sound.play()
                create_particle(bird_x, bird_y, RED)
                if boss_health <= 0:
                    coins += 50
                    achievements["Boss Slayer"]["achieved"] = True

        # Check for collisions
        if (bird_y < 0 or bird_y > HEIGHT or
            (pipe_x < bird_x + bird_radius < pipe_x + pipe_width and
             (bird_y < pipe_height or bird_y > pipe_height + pipe_gap))):
            game_state = GameState.GAME_OVER
            game_over_sound.play()
            if score > high_score:
                high_score = score
            save_game_data()

        update_achievements()
        update_particles()

        # Check daily challenge
        if not daily_challenge['completed'] and score >= daily_challenge['target']:
            daily_challenge['completed'] = True
            coins += 100  # Reward for completing daily challenge

    # Draw the appropriate screen based on game state
    if game_state == GameState.MENU:
        draw_menu()
    elif game_state == GameState.PLAYING:
        draw_game()
    elif game_state == GameState.GAME_OVER:
        draw_game_over()
    elif game_state == GameState.ACHIEVEMENTS:
        draw_achievements()

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

save_game_data()
pygame.quit()