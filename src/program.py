import pygame
from pygame.locals import *

import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
pygame.display.set_caption("Chorão")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
GREY = (100, 100, 100)
YELLOW = (255, 255, 0)  # Highlight color

# Font
font = pygame.font.SysFont(None, 48)

# Lanes and positions
lanes = [150, 250, 350, 450]  # Corresponding to a, s, k, l
keys = ['a', 's', 'k', 'l']
note_speed = 5
striking_zone_height = 100  # Height of the striking zone
striking_zone_y = HEIGHT - striking_zone_height

# Scoring and combo variables
score = 0
combo = 0
combo_streak = 0  # Tracks correct hits in a row

# Load background image
background_image = pygame.image.load("background.jpeg")  # Ensure the image exists in your project folder
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Scale it to the screen size

# Load and configure background music
pygame.mixer.music.load("musica.mp3")  # Replace with the path to your music file
pygame.mixer.music.set_volume(0.5)  # Set the volume (0.0 to 1.0)

# Function to find the next note in the lane
def find_next_note_in_lane(lane_key, notes):
    """Finds the next note in the same lane that hasn't been hit yet."""
    for note in notes:
        if note.key == lane_key and not note.hit:
            return note
    return None

# Draw the fixed blocks
def draw_fixed_blocks():
    for i, lane in enumerate(lanes):
        block_rect = pygame.Rect(lane, striking_zone_y, 50, 50)
        pygame.draw.rect(screen, GREY, block_rect)
        key_label = font.render(keys[i], True, WHITE)
        screen.blit(key_label, (lane + 10, striking_zone_y + 10))

# Function to calculate the score and set dissipation color
def calculate_score(note, accuracy):
    global score, combo, combo_streak

    if accuracy == "early":
        score_increase = -25
        note.dissipate_color = WHITE  # Early hit, set dissipation to white
    elif accuracy == "good":
        score_increase = 100
        note.dissipate_color = GREEN  # Good hit, set dissipation to green
    elif accuracy == "half":
        score_increase = 50
        note.dissipate_color = ORANGE  # Half hit, set dissipation to orange
    else:
        score_increase = -25
        note.dissipate_color = RED  # Miss, set dissipation to red

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


# Note class
class Note:
    def __init__(self, lane, key):
        self.radius = 25  # Radius of the circle note
        self.rect = pygame.Rect(lane, -50, self.radius * 2, self.radius * 2)  # Define bounding rect for the circle
        self.hit = False
        self.key = key
        self.dissipating = False  # Flag to start dissipation
        self.alpha = 255  # Full opacity at the start
        self.size_decrease_rate = 2  # How fast the note shrinks
        self.dissipate_color = RED  # Default color (will be changed based on hit)

    def fall(self):
        if not self.hit:
            self.rect.y += note_speed

    def dissipate(self):
        """Handles the dissipating animation after the note is hit."""
        if self.dissipating:
            # Increase size first, then shrink it for larger dissipation effect
            self.radius += self.size_decrease_rate
            self.alpha = max(0, self.alpha - 15)  # Gradually reduce alpha (transparency)

            if self.radius > 75:  # Start shrinking after a certain size
                self.size_decrease_rate = -2

            if self.radius <= 0 or self.alpha <= 0:
                return True  # Signal that dissipation is complete
        return False

    def draw(self, screen):
        """Draw the note, either normal or during dissipation."""
        if not self.dissipating:
            color = RED if not self.hit else self.dissipate_color
        else:
            color = (*self.dissipate_color[:3], self.alpha)  # Adjust alpha (transparency) for dissipating

        # Create a surface with transparency for the dissipating effect
        note_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(note_surface, color, (self.radius, self.radius), self.radius)
        screen.blit(note_surface, (self.rect.x, self.rect.y))

        # If hit, start dissipation
        if self.hit and not self.dissipating:
            self.dissipating = True


# Game Class to Handle Menu, Play, and Pause
class Game:
    def __init__(self):
        self.state = "menu"  # Game starts in the menu
        self.notes = []
        self.paused = False
        self.selected_option = 0  # 0: Play, 1: Quit

    def start_game(self):
        self.state = "playing"
        self.notes.clear()  # Clear notes when the game starts
        global score, combo, combo_streak
        score = 0
        combo = 0
        combo_streak = 0
        pygame.mixer.music.play(-1)  # Start playing music in loop when the game starts

    def pause_game(self):
        self.paused = True
        pygame.mixer.music.pause()  # Pause the music when game is paused

    def resume_game(self):
        self.paused = False
        pygame.mixer.music.unpause()  # Unpause the music when game resumes

    def back_to_menu(self):
        self.state = "menu"
        pygame.mixer.music.stop()  # Stop the music when returning to the menu

    def handle_menu(self):
        # Draw the menu
        screen.fill(BLACK)
        title = font.render("Guitar Hero Clone", True, WHITE)
        play_text_color = YELLOW if self.selected_option == 0 else WHITE
        quit_text_color = YELLOW if self.selected_option == 1 else WHITE
        play_text = font.render("Play", True, play_text_color)
        quit_text = font.render("Quit", True, quit_text_color)
        screen.blit(title, (WIDTH // 2 - 200, HEIGHT // 4))
        screen.blit(play_text, (WIDTH // 2 - 50, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - 50, HEIGHT // 2 + 50))

    def handle_pause(self):
        # Draw the pause screen
        screen.fill(BLACK)
        pause_text = font.render("Paused", True, WHITE)
        resume_text = font.render("Press ESC to Resume", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - 100, HEIGHT // 4))
        screen.blit(resume_text, (WIDTH // 2 - 200, HEIGHT // 2))

    def handle_play(self):
        # Draw the game background
        screen.blit(background_image, (0, 0))

        # Create new notes at random intervals
        if random.randint(1, 50) == 1:
            lane = random.choice(lanes)
            key = lanes.index(lane)
            self.notes.append(Note(lane, key))

        # Draw vertical lines in each lane
        for i, lane in enumerate(lanes):
            pygame.draw.line(screen, WHITE, (lane + 25, 0), (lane + 25, HEIGHT), 2)  # Thin vertical line in center of lane

        # Process falling notes
        for note in self.notes[:]:
            if note.dissipating:
                if note.dissipate():
                    self.notes.remove(note)  # Remove the note once it has fully dissipated
            else:
                note.fall()
            note.draw(screen)

        # Penalize if the note passes the striking zone without being hit
        for note in self.notes[:]:
            if note.rect.y > striking_zone_y + 50 and not note.hit:
                note.hit = True  # Mark the note as missed
                calculate_score(note, accuracy="miss")

    def update(self):
        if self.state == "menu":
            self.handle_menu()
        elif self.state == "playing":
            if not self.paused:
                self.handle_play()
            else:
                self.handle_pause()

    def handle_input(self, event):
        if self.state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Select option
                    if self.selected_option == 0:
                        self.start_game()
                    elif self.selected_option == 1:
                        pygame.quit()
                        exit()
                elif event.key == pygame.K_UP:
                    # Move selection up
                    self.selected_option = (self.selected_option - 1) % 2
                elif event.key == pygame.K_DOWN:
                    # Move selection down
                    self.selected_option = (self.selected_option + 1) % 2
        elif self.state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.paused:
                        self.pause_game()
                    else:
                        self.resume_game()

                # Handle back to menu logic
                if self.paused and event.key == pygame.K_m:
                    self.back_to_menu()

            # Process key presses when they occur
            if not self.paused:
                for lane_index, lane_key in enumerate(['a', 's', 'k', 'l']):
                    if event.type == pygame.KEYDOWN and event.key == ord(lane_key):
                        current_note = find_next_note_in_lane(lane_index, self.notes)

                        # Early hit logic: note is too far from the striking zone
                        if current_note and current_note.rect.y < striking_zone_y - 50 and not current_note.hit:
                            current_note.hit = True
                            calculate_score(current_note, accuracy="early")

                        # Normal hit logic: note is in the striking zone
                        elif current_note and HEIGHT - striking_zone_height - 50 < current_note.rect.y < HEIGHT - striking_zone_height + 50 and not current_note.hit:
                            current_note.hit = True
                            calculate_score(current_note, accuracy="good")


# Initialize game instance
game = Game()

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle input in the game
        game.handle_input(event)

    # Update the game based on state
    game.update()

    # Draw the score and combo on the screen if the game is playing
    if game.state == "playing" and not game.paused:
        score_label = font.render(f"Score: {score}", True, WHITE)
        combo_label = font.render(f"Combo: {combo}", True, WHITE)
        screen.blit(score_label, (10, 10))
        screen.blit(combo_label, (10, 60))
        draw_fixed_blocks()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()