import pygame
from pygame.locals import *
import random
import os

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

# Music list and high scores dictionary
songs = ["musica1.mp3", "musica2.mp3", "musica3.mp3"]
high_scores = {song: 0 for song in songs}
current_song = songs[0]

# Load background image
background_image = pygame.image.load("background.jpeg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Function to find the next note in the lane
def find_next_note_in_lane(lane_key, notes):
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
        note.dissipate_color = WHITE
    elif accuracy == "good":
        score_increase = 100
        note.dissipate_color = GREEN
    elif accuracy == "half":
        score_increase = 50
        note.dissipate_color = ORANGE
    else:
        score_increase = -25
        note.dissipate_color = RED

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

class Note:
    def __init__(self, lane, key):
        self.radius = 25  # Radius of the circle note
        self.rect = pygame.Rect(lane, -50, self.radius * 2, self.radius * 2)
        self.hit = False
        self.key = key
        self.dissipating = False
        self.alpha = 255
        self.size_decrease_rate = 2
        self.dissipate_color = RED

    def fall(self):
        if not self.hit:
            self.rect.y += note_speed

    def dissipate(self):
        if self.dissipating:
            self.radius += self.size_decrease_rate
            self.alpha = max(0, self.alpha - 15)
            if self.radius > 75:
                self.size_decrease_rate = -2
            if self.radius <= 0 or self.alpha <= 0:
                return True
        return False

    def draw(self, screen):
        if not self.dissipating:
            color = RED if not self.hit else self.dissipate_color
        else:
            color = (*self.dissipate_color[:3], self.alpha)

        note_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(note_surface, color, (self.radius, self.radius), self.radius)
        surface_x = self.rect.x + self.rect.width // 2 - self.radius
        surface_y = self.rect.y + self.rect.height // 2 - self.radius
        screen.blit(note_surface, (surface_x, surface_y))

        if self.hit and not self.dissipating:
            self.dissipating = True

# Game Class to Handle Menu, Play, and Pause
class Game:
    def __init__(self):
        self.state = "menu"
        self.notes = []
        self.paused = False
        self.selected_option = 0
        self.song_selected = 0

    def start_game(self):
        global current_song
        current_song = songs[self.song_selected]
        self.state = "playing"
        self.notes.clear()
        global score, combo, combo_streak
        score = 0
        combo = 0
        combo_streak = 0
        pygame.mixer.music.load(current_song)
        pygame.mixer.music.play(-1)

    def pause_game(self):
        self.paused = True
        pygame.mixer.music.pause()

    def resume_game(self):
        self.paused = False
        pygame.mixer.music.unpause()

    def back_to_menu(self):
        self.state = "menu"
        pygame.mixer.music.stop()

    def handle_menu(self):
        screen.fill(BLACK)
        title = font.render("Skater Pro: Chorão", True, WHITE)
        play_text_color = YELLOW if self.selected_option == 0 else WHITE
        quit_text_color = YELLOW if self.selected_option == 1 else WHITE
        play_text = font.render("Play", True, play_text_color)
        quit_text = font.render("Quit", True, quit_text_color)
        
        # Display the songs and high scores
        for i, song in enumerate(songs):
            song_text_color = YELLOW if self.song_selected == i else WHITE
            song_text = font.render(f"{song} (High Score: {high_scores[song]})", True, song_text_color)
            screen.blit(song_text, (WIDTH // 2 - 200, HEIGHT // 2 + 100 + (i * 50)))

        screen.blit(title, (WIDTH // 2 - 200, HEIGHT // 4))
        screen.blit(play_text, (WIDTH // 2 - 50, HEIGHT // 2))
        screen.blit(quit_text, (WIDTH // 2 - 50, HEIGHT // 2 + 50))

    def handle_pause(self):
        screen.fill(BLACK)
        pause_text = font.render("Paused", True, WHITE)
        resume_text = font.render("Press ESC to Resume", True, WHITE)
        return_text = font.render("Press M to Return to Menu", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - 100, HEIGHT // 4))
        screen.blit(resume_text, (WIDTH // 2 - 200, HEIGHT // 2))
        screen.blit(return_text, (WIDTH // 2 - 200, HEIGHT // 2 + 50))

    def handle_play(self):
        screen.blit(background_image, (0, 0))
        if random.randint(1, 50) == 1:
            lane = random.choice(lanes)
            key = lanes.index(lane)
            self.notes.append(Note(lane, key))

        for i, lane in enumerate(lanes):
            pygame.draw.line(screen, WHITE, (lane + 25, 0), (lane + 25, HEIGHT), 2)

        for note in self.notes[:]:
            if note.dissipating:
                if note.dissipate():
                    self.notes.remove(note)
            else:
                note.fall()
            note.draw(screen)

        for note in self.notes[:]:
            if note.rect.y > striking_zone_y + 50 and not note.hit:
                note.hit = True
                calculate_score(note, accuracy="miss")

    def update(self):
        if self.state == "menu":
            self.handle_menu()
        elif self.state == "playing":
            if not self.paused:
                self.handle_play()
            else:
                self.handle_pause()
        
        # Display high score for the current song
        if self.state == "playing" and not self.paused:
            high_score_label = font.render(f"High Score: {high_scores[current_song]}", True, WHITE)
            screen.blit(high_score_label, (10, 110))

    def handle_input(self, event):
        if self.state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Select option
                    if self.selected_option == 0:  # Start Game
                        self.start_game()
                    elif self.selected_option == 1:  # Quit Game
                        pygame.quit()
                        exit()
                elif event.key == pygame.K_UP:
                    # Move selection up (Play/Quit)
                    self.selected_option = (self.selected_option - 1) % 2
                elif event.key == pygame.K_DOWN:
                    # Move selection down (Play/Quit)
                    self.selected_option = (self.selected_option + 1) % 2
                elif event.key == pygame.K_LEFT:
                    # Move song selection left
                    self.song_selected = (self.song_selected - 1) % len(songs)
                elif event.key == pygame.K_RIGHT:
                    # Move song selection right
                    self.song_selected = (self.song_selected + 1) % len(songs)

        elif self.state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.paused:
                        self.pause_game()
                    else:
                        self.resume_game()

                # Handle back to menu logic
                if self.paused and event.key == pygame.K_m:
                    if score > high_scores[current_song]:  # Save the high score if beaten
                        high_scores[current_song] = score
                    self.back_to_menu()

                # Process key presses when they occur during gameplay
                if not self.paused:
                    for lane_index, lane_key in enumerate(['a', 's', 'k', 'l']):
                        if event.key == ord(lane_key):
                            current_note = find_next_note_in_lane(lane_index, self.notes)

                            # Early hit logic: note is too far from the striking zone
                            if current_note and current_note.rect.y < striking_zone_y - 50 and not current_note.hit:
                                current_note.hit = True
                                calculate_score(current_note, accuracy="early")

                            # Normal hit logic: note is in the striking zone
                            elif current_note and HEIGHT - striking_zone_height - 50 < current_note.rect.y < HEIGHT - striking_zone_height + 50 and not current_note.hit:
                                current_note.hit = True
                                calculate_score(current_note, accuracy="good")
                                
            # Save high score when the game ends
            if event.type == pygame.QUIT or (self.paused and event.key == pygame.K_m):
                if score > high_scores[current_song]:
                    high_scores[current_song] = score  # Update the high score
                self.back_to_menu()

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