import pygame
import random
import time
import math
import json
from pathlib import Path

# Initialize Pygame and window
pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Colors
green = (0, 230, 0)
bright_green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
black = (0, 0, 0)
white = (255, 255, 255)

# Game state variables
bullets = []
enemy_bullets = []
powerups = []
boost_end_time = 0
boost_level = 0
score = 0
level = 1
lives = 5
current_key = None

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "game_imgs"
SOUND_DIR = BASE_DIR / "game_sounds"

# Load crab image
crab_image = pygame.image.load(ASSET_DIR / "crab.png")
crab_scaled = pygame.transform.scale(crab_image, (50, 50))

crab_hit = pygame.image.load(ASSET_DIR / "crab_hit.png")
crab_hit_scaled = pygame.transform.scale(crab_hit, (50, 50))


# Load octopus image
octopus_image = pygame.image.load(ASSET_DIR / "octopus.png")
octopus_scaled = pygame.transform.scale(octopus_image, (50, 50))

octopus_hit = pygame.image.load(ASSET_DIR / "octopus_hit.png")
octopus_hit_scaled = pygame.transform.scale(octopus_hit, (50, 50))


# Load squid image
squid_image = pygame.image.load(ASSET_DIR / "squid.png")
squid_scaled = pygame.transform.scale(squid_image, (50, 50))

squid_hit = pygame.image.load(ASSET_DIR / "squid_hit.png")
squid_hit_scaled = pygame.transform.scale(squid_hit, (50, 50))

# Load spaceship image
spaceship_image = pygame.image.load(ASSET_DIR / "spaceship.png")
spaceship_scaled = pygame.transform.scale(spaceship_image, (50, 50))

spaceship_hit = pygame.image.load(ASSET_DIR / "spaceship_hit.png")
spaceship_hit_scaled = pygame.transform.scale(spaceship_hit, (50, 50))

# Super alien
super_spaceship_scaled = pygame.transform.scale(crab_image, (200, 200))
super_spaceship_hit_scaled = pygame.transform.scale(crab_hit, (200, 200))

# Load player image
player_image = pygame.image.load(ASSET_DIR / "player.png")
player_scaled = pygame.transform.scale(player_image, (121, 75))

# Load background image
bg_image = pygame.image.load(ASSET_DIR / "bg.png")
bg_scaled = pygame.transform.scale(bg_image, (1440, 960))

# Sound
shoot_sound = pygame.mixer.Sound(SOUND_DIR / "shoot.wav")
shoot_sound.set_volume(0.1)

pygame.mixer.music.load(SOUND_DIR / "bg_music.mp3")
pygame.mixer.music.set_volume(0.5)  # optional: 0.0 to 1.0
pygame.mixer.music.play(-1)  # -1 means loop forever


# Load Super Alien Bullet Animation (frames 0–3)
super_bullet_frames = []
for i in range(4):
    path = ASSET_DIR / "firebullet" / f"ball_{i}.png"
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (50, 28))  # width=50, height=28 to maintain aspect ratio
    super_bullet_frames.append(image)


# Utility function to render text on screen
def show_text(message, x, y, color, size=32, font_name="freesans"):
    font = pygame.font.SysFont(font_name, size)
    text_surface = font.render(message, False, color)
    screen.blit(text_surface, (x, y))

# Draw button with border and label
def draw_button(text, rect, button_color, text_color=black):
    pygame.draw.rect(screen, button_color, rect)
    pygame.draw.rect(screen, black, rect, 2)
    show_text(text, rect.x + 20, rect.y + 10, text_color)

# Start menu before gameplay begins
def start_menu():
    # Load font
    title_font = pygame.font.SysFont("comicsansms", 80)

    # For background animation
    stars = [[pygame.Vector2(random.randint(0, 1280), random.randint(0, 960)), random.randint(1, 3)] for _ in range(100)]

    waiting = True
    while waiting:
        screen.fill(black)

        # --- Animate background stars ---
        for star in stars:
            pos, speed = star
            pos.y += speed
            if pos.y > 960:
                pos.y = 0
                pos.x = random.randint(0, 1280)
            pygame.draw.circle(screen, white, (int(pos.x), int(pos.y)), speed)

        # --- Draw Title ---
        title_surface = title_font.render("Space Invaders", True, white)
        screen.blit(title_surface, (640 - title_surface.get_width() // 2, 150))

        # --- Create Button ---
        mouse_pos = pygame.mouse.get_pos()
        start_rect = pygame.Rect(540, 400, 200, 60)
        leaderboard_rect = pygame.Rect(540, 480, 200, 60)


        # Change color on hover
        if start_rect.collidepoint(mouse_pos):
            color = bright_green
        else:
            color = green

        pygame.draw.rect(screen, color, start_rect, border_radius=10)
        show_text("Start Game", start_rect.x + 20, start_rect.y + 15, black, 28)

        # View Leaderboard button
        lb_color = bright_green if leaderboard_rect.collidepoint(mouse_pos) else green
        pygame.draw.rect(screen, lb_color, leaderboard_rect, border_radius=10)
        show_text("Leaderboard", leaderboard_rect.x + 15, leaderboard_rect.y + 15, black, 28)



        # --- Handle Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    # Optional: Play sound here
                    waiting = False
                elif leaderboard_rect.collidepoint(event.pos):
                    show_leaderboard()


        pygame.display.update()
        clock.tick(60)

def gameover_menu(won):
    # Fonts
    title_font = "comicsansms"
    message_size = 72
    button_size = 36

    # Create animated stars
    stars = [[pygame.Vector2(random.randint(0, 1280), random.randint(0, 960)), random.randint(1, 3)] for _ in range(100)]

    waiting = True
    while waiting:
        screen.fill(black)

        # --- Animate Background ---
        for star in stars:
            pos, speed = star
            pos.y += speed
            if pos.y > 960:
                pos.y = 0
                pos.x = random.randint(0, 1280)
            pygame.draw.circle(screen, white, (int(pos.x), int(pos.y)), speed)

        # --- Show Result Message ---
        if won:
            show_text("You Win!", 640 - 150, 250, yellow, size=message_size, font_name=title_font)
        else:
            show_text("Game Over!", 640 - 180, 250, red, size=message_size, font_name=title_font)

        # --- Button Positions ---
        retry_rect = pygame.Rect(390, 450, 220, 70)
        quit_rect = pygame.Rect(670, 450, 220, 70)
        leaderboard_rect = pygame.Rect(530, 550, 220, 70)


        # --- Mouse Hover Detection ---
        mouse_pos = pygame.mouse.get_pos()

        # Retry button
        retry_color = (0, 200, 0) if retry_rect.collidepoint(mouse_pos) else green
        pygame.draw.rect(screen, retry_color, retry_rect, border_radius=10)
        show_text("Play Again", retry_rect.x + 25, retry_rect.y + 18, black, size=button_size)

        # Quit button
        quit_color = (200, 0, 0) if quit_rect.collidepoint(mouse_pos) else red
        pygame.draw.rect(screen, quit_color, quit_rect, border_radius=10)
        show_text("Quit", quit_rect.x + 75, quit_rect.y + 18, black, size=button_size)

        lb_color = (0, 200, 200) if leaderboard_rect.collidepoint(mouse_pos) else (0, 150, 150)
        pygame.draw.rect(screen, lb_color, leaderboard_rect, border_radius=10)
        show_text("Leaderboard", leaderboard_rect.x + 15, leaderboard_rect.y + 20, black, size=button_size)


        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    return True
                if quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()
                elif leaderboard_rect.collidepoint(event.pos):
                    show_leaderboard()

        pygame.display.update()
        clock.tick(60)
# --- High Score System ---

HIGHSCORE_FILE = BASE_DIR / "highscores.json"

def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_highscores(highscores):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(highscores, f)

def update_highscores(name, new_score):
    highscores = load_highscores()
    highscores.append({"name": name, "score": new_score})
    highscores = sorted(highscores, key=lambda x: x["score"], reverse=True)[:10]
    save_highscores(highscores)
    return highscores

def ask_username():
    name = ""
    font = pygame.font.SysFont("freesans", 40)
    input_box = pygame.Rect(440, 400, 400, 60)
    active = True

    while active:
        screen.fill(black)
        show_text("New High Score!", 480, 300, yellow, 48)
        show_text("Enter your name:", 500, 350, white, 32)

        pygame.draw.rect(screen, white, input_box, 2)
        txt_surface = font.render(name, True, white)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name[:12]  # limit name length
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12:
                        name += event.unicode

def show_leaderboard():
    highscores = load_highscores()
    screen.fill(black)
    show_text("Leaderboard - Top 10", 460, 100, yellow, 48)

    y = 180
    for i, entry in enumerate(highscores):
        show_text(f"{i+1}. {entry['name']} - {entry['score']}", 460, y, white, 32)
        y += 40

    show_text("Press any key to continue...", 440, 650, white, 28)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

def draw_hud(level, score, lives):
    hud_height = 60
    hud_y = 0
    hud_color = (0, 0, 0)  # black background
    text_color = white
    font_size = 32
    font_name = "freesans"

    # Draw black rectangle across the top
    pygame.draw.rect(screen, hud_color, (0, hud_y, 1280, hud_height))

    # Horizontal spacing
    section_width = 1280 // 3

    # Text positions (centered in each third)
    level_x = section_width // 2
    score_x = section_width + section_width // 2
    lives_x = 2 * section_width + section_width // 2
    text_y = hud_y + 15

    show_text(f"Level: {level}", level_x, text_y, text_color, size=font_size, font_name=font_name)
    show_text(f"Score: {score}", score_x, text_y, text_color, size=font_size, font_name=font_name)
    show_text(f"Lives: {lives}", lives_x, text_y, text_color, size=font_size, font_name=font_name)


# Base Alien class and subclasses using inheritance
class Alien:
    def __init__(self, x, y, image, hit_image, hp, score_value):
        self.x = x
        self.y = y
        self.image = image
        self.hit_image = hit_image
        self.visual = self.image
        self.hp = hp
        self.score_value = score_value
        self.length = 50
        self.speed = 2 + (level//3)
        self.direction = 1
        self.rect = pygame.Rect(x, y, 50, 50)
        self.attacked = False

    def move(self):
        self.x += self.speed * self.direction

    def move_down(self):
        self.y += 50

    def wall(self):
        return self.x < 0 or self.x + self.length > 1280

    def draw(self):
        if self.attacked:
            if time.time() - self.start_time > 0.1:
                self.visual = self.image
                self.attacked = False
        screen.blit(self.visual, (self.x, self.y))
        self.rect.topleft = (self.x, self.y)

    def hit(self):
        global score
        self.hp -= 1
        self.start_time = time.time()
        self.visual = self.hit_image
        self.attacked = True

        if self.hp <= 0:
            score += self.score_value
            return True
        return False

class Squid(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, squid_scaled, squid_hit_scaled, hp=1, score_value=10)

class Crab(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, crab_scaled, crab_hit_scaled, hp=1, score_value=20)

class Octopus(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, octopus_scaled, octopus_hit_scaled, hp=2, score_value=50)

class Spaceship(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, spaceship_scaled, spaceship_hit_scaled, hp=3, score_value=100)

class SuperAlien(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, super_spaceship_scaled, super_spaceship_hit_scaled, hp=50, score_value=500)
        self.length = 200
        self.firing_direction = 1
        self.fire_start_time = None
        self.firing_bullets = False
        self.bullet_index = 0
        self.last_shot_time = 0
        self.dx_sequence = []
        self.spawn_time = time.time()
        self.start_delay = 5  # seconds
        self.fire_start_time = None


    def update(self):
        current_time = time.time()

        # Fire once every 10 seconds
        if current_time - self.spawn_time >= self.start_delay:
            if self.fire_start_time is None or current_time - self.fire_start_time >= 10:
                self.fire_start_time = current_time
                self.rapid_fire()

            
    def rapid_fire(self):
        dx_max = 6
        dx_values = list(range(-dx_max, dx_max+1,dx_max//2))

        if self.firing_direction == -1:
            dx_values.reverse()

        for dx in dx_values:
            dy = math.sqrt(100 - dx**2)  # ensures speed = 12 (Pythagoras)
            eb = SuperBullet(self.x + self.length // 2, self.y + self.length // 2, dx, dy)
            eb.dx = dx
            eb.dy = dy
            enemy_bullets.append(eb)

        # Flip direction for the next burst
        self.firing_direction *= -1




# Bullet class
class BaseBullet:
    def __init__(self, x, y, dx, dy, color, length=25):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.length = length
        self.color = color
        self.despawn = False

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def delete(self, screen_height):
        if self.y < 0 or self.y > screen_height:
            self.despawn = True

    def draw(self):
        pygame.draw.rect(screen, self.color, (round(self.x), round(self.y), self.length, self.length))


class Bullet(BaseBullet):
    def __init__(self, x, y, dx):
        dy = -math.sqrt(144 - dx**2)  # moves upward
        super().__init__(x, y, dx, dy, color=green)
    
    def check_collision(self, aliens):
        for alien in aliens[:]:
            if (self.x < alien.x + alien.length and
                self.x + self.length > alien.x and
                self.y < alien.y + alien.length and
                self.y + self.length > alien.y):
                dead = alien.hit()
                if dead:
                    aliens.remove(alien)
                bullets.remove(self)
                break

class EnemyBullet(BaseBullet):
    def __init__(self, x, y):
        super().__init__(x, y, dx=0, dy=6, color=green, length=15)
        
class SuperBullet(EnemyBullet):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y)
        self.dx = dx
        self.dy = dy
        self.frames = super_bullet_frames
        self.frame_index = 0
        self.animation_timer = time.time()
        self.frame_duration = 0.1

        # Calculate angle based on movement direction
        # math.atan2 gives radians, convert to degrees
        # Since fireball faces LEFT (180°), we offset angle by 180°
        angle_rad = math.atan2(self.dy, self.dx)
        self.angle = math.degrees(angle_rad)

        # For trail effect
        self.trail = []

    def move(self):
        super().move()

        # Save trail positions (limit length)
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

    def draw(self):
        # Animate frame
        now = time.time()
        if now - self.animation_timer > self.frame_duration:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.animation_timer = now

        current_frame = self.frames[self.frame_index]

        # --- Rotate to match direction ---
        rotated_img = pygame.transform.rotate(current_frame, self.angle)
        rect = rotated_img.get_rect(center=(round(self.x), round(self.y)))

        # --- Draw glow trail ---
        for i, (tx, ty) in enumerate(self.trail[:-1]):
            alpha = int(100 * (i / len(self.trail)))
            trail_frame = pygame.transform.rotate(self.frames[0], self.angle)
            trail_frame.set_alpha(alpha)
            trail_rect = trail_frame.get_rect(center=(round(tx), round(ty)))
            screen.blit(trail_frame, trail_rect.topleft)

        # --- Draw bullet ---
        screen.blit(rotated_img, rect.topleft)


# Player class with movement and firing logic
class Player:
    def __init__(self):
        self.width = 121
        self.height = 75
        self.x = (1280 - self.width) // 2
        self.y = 600
        self.direction = 0
        self.speed = 0
        self.shoot = False

    def move(self):
        self.x += self.speed

    def acceleration(self):
        if self.direction == -1:
            self.speed = max(self.speed - 1, -10)
        elif self.direction == 1:
            self.speed = min(self.speed + 1, 10)
        else:
            self.speed *= 0.96
            if abs(self.speed) < 0.5:
                self.speed = 0

    def walls(self):
        if self.x < 0:
            self.x = 0
            self.speed = 0
        if self.x > 1280 - self.width:
            self.x = 1280 - self.width
            self.speed = 0

    def draw(self):
        screen.blit(player_scaled, (round(self.x), round(self.y)))

    def fire(self):
        global boost_end_time, boost_level
        
        if self.shoot:
            now = time.time()
            if now < boost_end_time:
                if boost_level >= 5:
                    spread = [-4, -2, 0, 2, 4]
                else:
                    spread = [-2, 0, 2]
            else:
                spread = [0]

            # Sound
            shoot_sound.play()
                
            for dx in spread:
                bullets.append(Bullet(self.x + 48, self.y + 25, dx))
            self.shoot = False

# PowerUp class for speed boosts
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = 4
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius*2, self.radius*2)

    def move(self):
        self.y += self.speed
        self.rect.y = self.y - self.radius

    def draw(self):
        pygame.draw.circle(screen, yellow, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, player):
        if player.x < self.x < player.x + player.width and player.y < self.y < player.y + player.height:
            return True
        return False

# Define level configurations
levels = [
    [1, 0, 0, 0],    # 1 → 1 row
    [2, 0, 0, 0],    # 2 → 2 rows
    [1, 1, 0, 0],    # 3 → 2 rows
    [2, 1, 0, 0],    # 4 → 3 rows
    [],              # 5 → Boss only

    [2, 2, 0, 0],    # 6 → 4 rows
    [2, 2, 1, 0],    # 7 → 5 rows
    [2, 2, 2, 0],    # 8 → 6 rows
    [1, 2, 2, 1],    # 9 → 6 rows
    [1, 1, 2, 1],    # 10 → 5 rows + Boss

    [1, 2, 2, 1],    # 11 → 6 rows
    [1, 2, 3, 0],    # 12 → 6 rows
    [0, 3, 2, 1],    # 13 → 6 rows
    [1, 2, 2, 1],    # 14 → 6 rows
    [2, 2, 1, 1],    # 15 → 6 rows + Boss
]

current_level = levels[level - 1].copy()
aliens = []

# Generate alien instances based on current_level
def generate():
    aliens.clear()
    if level > 0 and level % 5 == 0:
        aliens.append(SuperAlien(540, 50))
    total_rows = sum(current_level)
    cols = 10
    spacing_x = 10
    spacing_y = 10
    alien_width = 50
    start_x = (1280 - (cols * alien_width + (cols - 1) * spacing_x)) // 2

    # Build rows by type
    alien_classes = [Squid, Crab, Octopus, Spaceship]
    for row in range(total_rows):
        idx = next(
            idx
            for idx in range(len(current_level) - 1, -1, -1)
            if current_level[idx] > 0
        )
        alien_class = alien_classes[idx]
        current_level[idx] -= 1

        y = 75 + row * (alien_width + spacing_y)
        for col in range(cols):
            x = start_x + col * (alien_width + spacing_x)
            aliens.append(alien_class(x, y))

    bullets.clear()
    enemy_bullets.clear()

def reset_game():
    global lives, score, level, current_level, bullets, enemy_bullets, current_key
    lives = 5
    score = 0
    level = 1
    current_level = levels[0].copy()
    generate()
    bullets.clear()
    enemy_bullets.clear()
    player.x = (1280 - player.width) // 2
    player.speed = 0
    player.direction = 0
    current_key = None


# Entry point: start menu, then main game loop
start_menu()
player = Player()
generate()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_key = pygame.K_LEFT
                player.direction = -1
            elif event.key == pygame.K_RIGHT:
                current_key = pygame.K_RIGHT
                player.direction = 1
            if event.key == pygame.K_SPACE:
                player.shoot = True
        if event.type == pygame.KEYUP:
            if event.key == current_key:
                player.direction = 0
                current_key = None
            if event.key == pygame.K_SPACE:
                player.shoot = False

    # Update game state
    screen.fill(black)
    screen.blit(bg_scaled, (-80, -120))
    
    
    player.acceleration()
    player.move()
    player.walls()
    player.fire()
    player.draw()

    # Random power-up spawn
    if random.randint(1, 300) == 1:
        powerups.append(PowerUp(random.randint(20, 1260), 0))

    # Update power-ups and handle collisions
    for pu in powerups[:]:
        pu.move()
        if pu.check_collision(player):
            if time.time() < boost_end_time:
                boost_level = 5
                boost_end_time += 5
            else:
                boost_level = 3
                boost_end_time = time.time() + 5
            powerups.remove(pu)
        pu.draw()

    # Alien movement and wall collision
    hit_wall = False
    for alien in aliens:
        alien.move()
        if isinstance(alien, SuperAlien):
            alien.update()
        if alien.wall():
            hit_wall = True
        alien.draw()
        # Game over if any alien reaches too low
        if alien.y + alien.length >= 600:
            highscores = load_highscores()
            if len(highscores) < 10 or score > highscores[-1]["score"]:
                name = ask_username()
                update_highscores(name, score)
                show_leaderboard()
            replay = gameover_menu(won=False)
            if replay:
                pygame.event.clear()
                reset_game()
            else:
                running = False
            break


        # Enemy Bullets
        if isinstance(alien, (Crab, Spaceship)):
            if random.randint(1, 700) == 1:  # Adjust probability as needed
                bullet_x = alien.x + 20
                bullet_y = alien.y + 50
                enemy_bullets.append(EnemyBullet(bullet_x, bullet_y))

    if hit_wall:
        for alien in aliens:
            alien.direction *= -1
            alien.move_down()
        
    # Bullet movement and collision
    for bullet in bullets[:]:
        bullet.move()
        bullet.delete(720)
        bullet.check_collision(aliens)
        bullet.draw()

    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    
    for eb in enemy_bullets[:]:
        eb.move()
        if player_rect.colliderect(pygame.Rect(eb.x, eb.y, eb.length, eb.length)):
            enemy_bullets.remove(eb)
            lives -= 1
            if lives <= 0:
                # Game over logic here, e.g., show gameover menu or quit
                highscores = load_highscores()
                if len(highscores) < 10 or score > highscores[-1]["score"]:
                    name = ask_username()
                    update_highscores(name, score)
                    show_leaderboard()
                replay = gameover_menu(won=False)
                if replay:
                    pygame.event.clear()
                    reset_game()
                else:
                    running = False
            break  # Prevent multiple hits in one frame
        eb.delete(720)
        eb.draw()
        if eb.despawn:
            enemy_bullets.remove(eb)
            
    draw_hud(level, score, lives)
    
    pygame.display.update()
    clock.tick(60)

    # Check for end of level or game
    if not aliens:
        if level < len(levels):
            level += 1
            current_level = levels[level - 1].copy()
            generate()
        else:
            highscores = load_highscores()
            if len(highscores) < 10 or score > highscores[-1]["score"]:
                name = ask_username()
                update_highscores(name, score)
                show_leaderboard()
            replay = gameover_menu(won=True)

            if replay:
                pygame.event.clear()
                reset_game()
            else:
                running = False

pygame.quit()
