import pygame
from pygame.locals import *
import random
import os
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
pygame.display.set_caption("Chorão")

# File to save high scores
SCORE_FILE = "high_scores.json"

# Load high scores from file
def load_high_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as file:
            return json.load(file)
    else:
        return {song: 0 for song in songs}

# Save high scores to file
def save_high_scores():
    with open(SCORE_FILE, "w") as file:
        json.dump(high_scores, file)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
GREY = (100, 100, 100)
YELLOW = (255, 255, 0)  # Highlight color

MUSIC_MAX_TIME = 30000  # For example, 30 seconds

# Load custom font
custom_font_path = "RockSalt-Regular.ttf"  
font_large = pygame.font.Font(custom_font_path, 64)
font_medium = pygame.font.Font(custom_font_path, 32)

# Font
font = pygame.font.Font(custom_font_path, 22)

# Lanes and positions
lanes = [150, 250, 350, 450]  # Corresponding to a, s, k, l
keys = [0, 1, 2, 3]
note_speed = 5
striking_zone_height = 100  # Height of the striking zone
striking_zone_y = HEIGHT - striking_zone_height

# Scoring and combo variables
score = 0
combo = 0
combo_streak = 0  # Tracks correct hits in a row

# Music list and high scores dictionary
songs = ["musica1.mp3", "musica2.mp3", "musica3.mp3"]
high_scores = load_high_scores()
current_song = songs[0]

# Function to find the next note in the lane
def find_next_note_in_lane(lane_key, notes):
    for note in notes:
        if note.key == lane_key and not note.hit:
            return note
    return None

# Draw the fixed blocks
def draw_fixed_arrows():
    original_arrow = pygame.transform.scale(pygame.image.load("Sprites/setas/seta_padrao.png"), (50, 50))
    arrows = [ 
        pygame.transform.rotate(original_arrow, 90),    # Left
        pygame.transform.rotate(original_arrow, 180),   # Down
        original_arrow,                                 # Up  
        pygame.transform.rotate(original_arrow, -90)    # Right
    ]
    for i, lane in enumerate(lanes):
        arrow_rect = arrows[i].get_rect(center=(lane + 25, HEIGHT - striking_zone_height + 25))
        screen.blit(arrows[i], arrow_rect)

# Modify the score calculation logic
def calculate_score(note, accuracy):
    global score, combo, combo_streak

    # Adjust base score increments and decrements for fairness
    if accuracy == "early":
        score_increase = -2  # Small penalty for early hits
        note.dissipate_color = WHITE
    elif accuracy == "good":
        score_increase = 4  # Lower score for good hits
        note.dissipate_color = GREEN
    elif accuracy == "half":
        score_increase = 2  # Lower score for half-good hits
        note.dissipate_color = ORANGE
    else:
        score_increase = -3  # Higher penalty for a complete miss
        note.dissipate_color = RED

    if score_increase > 0:
        # Positive combo for correct hits, capped at 5x multiplier
        combo_streak += 1
        combo = min(combo_streak, 5)  # Cap the positive combo at 5
    else:
        # Negative combo for misses; increases penalty with more misses
        combo_streak = max(combo_streak - 1, -5)  # Cap the negative combo at -5
        combo = combo_streak

    # Update score based on combo
    score += score_increase * abs(combo)  # Use absolute value of combo for consistency

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

        # Load arrow sprites for each lane
        self.arrow_sprites = [
            pygame.transform.scale(pygame.image.load("Sprites/setas/seta_esquerda.png"), (50, 50)),
            pygame.transform.scale(pygame.image.load("Sprites/setas/seta_baixo.png"), (50, 50)),
            pygame.transform.scale(pygame.image.load("Sprites/setas/seta_cima.png"), (50, 50)),
            pygame.transform.scale(pygame.image.load("Sprites/setas/seta_direita.png"), (50, 50))
        ]
        self.current_arrow = self.arrow_sprites[key]

    def fall(self):
        if not self.hit:
            self.rect.y += note_speed

    def dissipate(self):
        if self.dissipating:
            self.radius += self.size_decrease_rate
            self.alpha = max(0, self.alpha - 15)
            if self.alpha <= 0:
                return True
        return False

    def draw(self, screen):
        if not self.dissipating:
            # Draw the note with the arrow sprite
            screen.blit(self.current_arrow, (self.rect.x, self.rect.y))
        else:
            # Create a temporary surface for the dissipating note
            dissipate_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color = self.dissipate_color + (self.alpha,)
            pygame.draw.circle(dissipate_surface, color, (self.radius, self.radius), self.radius)
            # Position and draw the dissipating circle
            dissipate_x = self.rect.x + self.rect.width // 2 - self.radius
            dissipate_y = self.rect.y + self.rect.height // 2 - self.radius
            screen.blit(dissipate_surface, (dissipate_x, dissipate_y))

        if self.hit and not self.dissipating:
            self.dissipating = True


class BigCryer:
    def __init__(self):
        self.x = 300
        self.y = 400
        self.hit = False
        self.jump_height = 5
        self.animations = {
            "start_walk": self.load_animation("Sprites/cryer/Comeco_andar.png", 616, 192, 11),
            "walk": self.load_animation("Sprites/cryer/Andando.png", 616, 192, 12),
            "jump": self.load_animation("Sprites/cryer/Pulando.png", 616, 192, 11),
            "crouch": self.load_animation("Sprites/cryer/Abaixa.png", 616, 192, 6),
            "trick1": self.load_animation("Sprites/cryer/Manobra_baixo.png", 616, 192, 8),
        }
        self.current_animation = "start_walk"
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_delay = 5

    def load_animation(self, file_path, frame_width, frame_height, num_frames):
        animation = []
        sprite_sheet = pygame.image.load(file_path).convert_alpha()
        for i in range(num_frames):
            frame = sprite_sheet.subsurface((0, i*frame_height, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (frame_width * 1.3, frame_height * 1.3))
            animation.append(frame)
        return animation

    def set_animation(self, action):
        if action != self.current_animation:
            self.current_animation = action
            self.current_frame = 0

    def update(self, screen):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame += 1
            
            # Se a animação for apenas uma vez e estiver no último quadro
            if self.current_animation != "walk" and self.current_frame >= len(self.animations[self.current_animation]):
                self.set_animation("walk")  # Volta para a animação "walk"
            else:
                # Garante que a animação continua a se repetir caso não seja "once"
                self.current_frame %= len(self.animations[self.current_animation])
        
        current_frame_image = self.animations[self.current_animation][self.current_frame]
        screen.blit(current_frame_image, (self.x, self.y))

class BackgroundLayer:
    def __init__(self, image_path, speed):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.x1 = 0
        self.x2 = self.image.get_width()
        self.speed = speed

    def update(self, screen):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 + self.image.get_width() < 0:
            self.x1 = self.x2 + self.image.get_width()
        if self.x2 + self.image.get_width() < 0:
            self.x2 = self.x1 + self.image.get_width()

        screen.blit(self.image, (self.x1, 0))
        screen.blit(self.image, (self.x2, 0))

# Game Class to Handle Menu, Play, and Pause
class Game:
    def __init__(self):
        self.state = "menu"
        self.notes = []
        self.paused = False
        self.selected_option = 0
        self.song_selected = 0
        self.music_start_time = 0  # Track when the music started

    def start_game(self):
        global current_song
        current_song = songs[self.song_selected]
        current_phase = self.song_selected 
        self.background_layers = background_selection(current_phase)
        self.state = "playing"
        self.notes.clear()
        global score, combo, combo_streak
        score = 0
        combo = 0
        combo_streak = 0
        pygame.mixer.music.load(current_song)
        pygame.mixer.music.play(-1)
        self.music_start_time = pygame.time.get_ticks()  # Record the start time of the music

    def handle_menu(self):
        screen.fill(BLACK)
        
        # Title
        title_text = font_large.render("Skater Pro: Chorão", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)
        
        # Menu Options
        play_text_color = YELLOW if self.selected_option == 0 else WHITE
        quit_text_color = YELLOW if self.selected_option == 1 else WHITE
        play_text = font_medium.render("Play", True, play_text_color)
        quit_text = font_medium.render("Quit", True, quit_text_color)
        
        # Center menu options
        play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(play_text, play_rect)
        screen.blit(quit_text, quit_rect)
        
        # Song List
        for i, song in enumerate(songs):
            song_text_color = YELLOW if self.song_selected == i else GREY
            song_text = font_medium.render(f"{song} (High Score: {high_scores[song]})", True, song_text_color)
            song_rect = song_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 140 + (i * 50)))
            screen.blit(song_text, song_rect)
            
    def pause_game(self):
        self.paused = True
        pygame.mixer.music.pause()

    def resume_game(self):
        self.paused = False
        pygame.mixer.music.unpause()

    def back_to_menu(self):
        self.state = "menu"
        pygame.mixer.music.stop()

    def handle_game_over(self):
        screen.fill(BLACK)
        game_over_text = font_large.render("Game Over", True, WHITE)
        score_text = font_medium.render(f"Score: {score}", True, WHITE)
        high_score_text = font_medium.render(f"High Score: {high_scores[current_song]}", True, WHITE)
        return_text = font_medium.render("Press Enter to return to Menu", True, GREY)
        
        # Center the game over text
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(high_score_text, high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
        screen.blit(return_text, return_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100)))
        
    def handle_pause(self):
        screen.fill(BLACK)
        pause_text = font.render("Paused", True, WHITE)
        resume_text = font.render("Press ESC to Resume", True, WHITE)
        return_text = font.render("Press M to Return to Menu", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - 100, HEIGHT // 4))
        screen.blit(resume_text, (WIDTH // 2 - 200, HEIGHT // 2))
        screen.blit(return_text, (WIDTH // 2 - 200, HEIGHT // 2 + 50))

    def handle_play(self):
        # Check if the music has reached the max time
        elapsed_time = pygame.time.get_ticks() - self.music_start_time
        if elapsed_time >= MUSIC_MAX_TIME:
            pygame.mixer.music.stop()
            if score > high_scores[current_song]:  # Update high score if beaten
                high_scores[current_song] = score
                save_high_scores()  # Save high scores to file
            self.state = "game_over"  # Switch to game over state
            
        # Regular gameplay handling
        if random.randint(1, 50) == 1:
            lane = random.choice(lanes)
            key = lanes.index(lane)
            self.notes.append(Note(lane, key))
        
        # Draw backgrounds
        for layer in self.background_layers:
            layer.update(screen)

        # Draw the striking zone
        for i, lane in enumerate(lanes):
            pygame.draw.line(screen, WHITE, (lane + 25, 0), (lane + 25, HEIGHT), 2)

        # Draw the notes and handle dissipation
        for note in self.notes[:]:
            if note.dissipating:
                if note.dissipate():
                    self.notes.remove(note)
            else:
                note.fall()
            note.draw(screen)

        # Check for notes that are missed
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
        elif self.state == "game_over":
            self.handle_game_over()

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
                    self.selected_option = (self.selected_option - 1) % 2
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % 2
                elif event.key == pygame.K_LEFT:
                    self.song_selected = (self.song_selected - 1) % len(songs)
                elif event.key == pygame.K_RIGHT:
                    self.song_selected = (self.song_selected + 1) % len(songs)

        elif self.state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.paused:
                        self.pause_game()
                    else:
                        self.resume_game()
                if self.paused and event.key == pygame.K_m:
                    if score > high_scores[current_song]:  # Save the high score if beaten
                        high_scores[current_song] = score
                    self.back_to_menu()

                # Process key presses when they occur during gameplay
                if not self.paused:
                    for lane_index, lane_key in enumerate([pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT]):
                        if event.key == lane_key:
                            current_note = find_next_note_in_lane(lane_index, self.notes)
                            if current_note and current_note.rect.y < striking_zone_y - 50 and not current_note.hit:
                                current_note.hit = True
                                calculate_score(current_note, accuracy="early")
                            elif current_note and HEIGHT - striking_zone_height - 50 < current_note.rect.y < HEIGHT - striking_zone_height + 50 and not current_note.hit:
                                current_note.hit = True
                                calculate_score(current_note, accuracy="good")

        elif self.state == "game_over" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.back_to_menu()

# Initialize game instance
game = Game()

# Initialize Character BigCryer
cryer = BigCryer()


def background_selection(background_selected):
    if background_selected == 0:
        background_layers = [
            BackgroundLayer("Sprites/bg/fase1/Sky.png", 1),
            BackgroundLayer("Sprites/bg/fase1/back.png", 2),
            BackgroundLayer("Sprites/bg/fase1/houses3.png", 3),
            BackgroundLayer("Sprites/bg/fase1/houses1.png", 4),
            BackgroundLayer("Sprites/bg/fase1/minishop&callbox.png", 5),
            BackgroundLayer("Sprites/bg/fase1/road&lamps.png", 6)
        ]
    elif background_selected == 1:
        background_layers = [
            BackgroundLayer("Sprites/bg/fase2/1.png", 1),
            BackgroundLayer("Sprites/bg/fase2/2.png", 2),
            BackgroundLayer("Sprites/bg/fase2/3.png", 3),
            BackgroundLayer("Sprites/bg/fase2/4.png", 4),
            BackgroundLayer("Sprites/bg/fase2/5.png", 5),
            BackgroundLayer("Sprites/bg/fase2/7.png", 6),
            BackgroundLayer("Sprites/bg/fase2/road2.png", 7)
        ]
    elif background_selected == 2:
        background_layers = [
            BackgroundLayer("Sprites/bg/fase3/Sky.png", 1),
            BackgroundLayer("Sprites/bg/fase3/houses.png", 2),
            BackgroundLayer("Sprites/bg/fase3/houses2.png", 3),
            BackgroundLayer("Sprites/bg/fase3/fountain&bush.png", 4),
            BackgroundLayer("Sprites/bg/fase3/houses1.png", 5),
            BackgroundLayer("Sprites/bg/fase3/umbrella&policebox.png", 6),
            BackgroundLayer("Sprites/bg/fase3/road.png", 7)
        ]
    return background_layers

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                cryer.set_animation("crouch")
            elif event.key == pygame.K_UP:
                cryer.set_animation("jump")
            elif event.key == pygame.K_RIGHT:
                cryer.set_animation("trick1")
            elif event.key == pygame.K_LEFT:
                cryer.set_animation("trick1")

        # Handle input in the game
        game.handle_input(event)
    
    
    # Update the game based on state
    game.update()
    if game.state == "playing":
        cryer.update(screen)
    

    # Draw the score and combo on the screen if the game is playing
    if game.state == "playing" and not game.paused:
        score_label = font.render(f"Score: {score}", True, WHITE)
        combo_label = font.render(f"Combo: {combo}", True, WHITE)
        screen.blit(score_label, (10, 10))
        screen.blit(combo_label, (10, 60))
        draw_fixed_arrows()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()