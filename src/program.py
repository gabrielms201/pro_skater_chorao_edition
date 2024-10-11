import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guitar Hero Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (100, 100, 100)

# Font
font = pygame.font.SysFont(None, 48)

# Lanes and positions
lanes = [150, 250, 350, 450]  # Corresponding to w, a, s, d
keys = ['a', 's', 'k', 'l']
note_speed = 5
striking_zone_height = 100  # Height of the striking zone
striking_zone_y = HEIGHT - striking_zone_height

# Scoring and combo variables
score = 0
combo = 0
combo_streak = 0  # Tracks correct hits in a row

# Note class
class Note:
    def __init__(self, lane, key):
        self.rect = pygame.Rect(lane, -50, 50, 50)
        self.hit = False
        self.key = key

    def fall(self):
        self.rect.y += note_speed

    def draw(self, screen):
        color = GREEN if self.hit else RED
        pygame.draw.rect(screen, color, self.rect)

# Draw the fixed blocks
def draw_fixed_blocks():
    for i, lane in enumerate(lanes):
        block_rect = pygame.Rect(lane, striking_zone_y, 50, 50)
        pygame.draw.rect(screen, GREY, block_rect)
        key_label = font.render(keys[i], True, WHITE)
        screen.blit(key_label, (lane + 10, striking_zone_y + 10))

# Function to calculate the score and combo
def calculate_score(note, too_early=False):
    global score, combo, combo_streak

    if too_early:
        # Penalize for clicking too early
        score_increase = -25
    elif striking_zone_y < note.rect.y < striking_zone_y + 50:
        # Full score for hitting in the lower half of the striking zone
        score_increase = 100
    elif striking_zone_y - 50 < note.rect.y < striking_zone_y:
        # Half score for hitting in the upper half of the striking zone
        score_increase = 50
    else:
        # Miss
        score_increase = -25

    if score_increase > 0:
        combo_streak += 1
        if combo_streak >= 3:
            combo = 2 ** (combo_streak - 2)  # Exponential combo multiplier
        else:
            combo = 1
    else:
        combo_streak = 0  # Reset combo streak on miss or early click
        combo = 1  # Reset combo multiplier

    score += score_increase * combo

# Initialize variables
notes = []
game_over = False

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)

    # Create new notes at random intervals
    if random.randint(1, 50) == 1:
        lane = random.choice(lanes)
        key = lanes.index(lane)
        notes.append(Note(lane, key))

    # Process falling notes
    for note in notes:
        note.fall()
        note.draw(screen)

        # Check if note is in the striking zone and process input
        if HEIGHT - striking_zone_height - 50 < note.rect.y < HEIGHT - striking_zone_height + 50 and not note.hit:
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_a] and note.key == 0:
                note.hit = True
                calculate_score(note)
            elif keys_pressed[pygame.K_s] and note.key == 1:
                note.hit = True
                calculate_score(note)
            elif keys_pressed[pygame.K_k] and note.key == 2:
                note.hit = True
                calculate_score(note)
            elif keys_pressed[pygame.K_l] and note.key == 3:
                note.hit = True
                calculate_score(note)
        # Penalize if the note passes the striking zone without being hit
        elif note.rect.y > striking_zone_y + 50 and not note.hit:
            note.hit = True  # Mark the note as missed
            calculate_score(note)

        # Penalize for clicking too early
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_w] and note.key == 0 and note.rect.y < striking_zone_y - 50:
            calculate_score(note, too_early=True)
        elif keys_pressed[pygame.K_a] and note.key == 1 and note.rect.y < striking_zone_y - 50:
            calculate_score(note, too_early=True)
        elif keys_pressed[pygame.K_s] and note.key == 2 and note.rect.y < striking_zone_y - 50:
            calculate_score(note, too_early=True)
        elif keys_pressed[pygame.K_d] and note.key == 3 and note.rect.y < striking_zone_y - 50:
            calculate_score(note, too_early=True)

    # Draw fixed blocks with key labels
    draw_fixed_blocks()

    # Draw the score and combo on the screen
    score_label = font.render(f"Score: {score}", True, WHITE)
    combo_label = font.render(f"Combo: {combo}", True, WHITE)
    screen.blit(score_label, (10, 10))
    screen.blit(combo_label, (10, 60))

    # Event handler to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()