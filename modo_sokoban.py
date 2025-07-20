# modo_sokoban.py
import utime
import ujson
from machine import Pin, PWM
from config import * # Assuming config.py has BUZZER_PIN, etc.

# --- Game Configuration ---
SPRITE_SIZE = 7
LEVELS_FILE = "levels.json"
SCORES_FILE = "scores.json"

# --- Global Game State ---
current_level_index = 0
game_matrix = []
player_x, player_y = 0, 0
moves_count = 0
pushes_count = 0
start_time = 0
game_won = False
all_levels = [] # To store all levels loaded from JSON

# --- Buzzer (re-initialize based on main.py's approach) ---
# In main.py, buzzer is initialized, so we assume play_sound is passed.

# --- Sprites for drawing ---
def draw_sprite(oled, x, y, sprite_type):
    x0 = x * SPRITE_SIZE
    y0 = y * SPRITE_SIZE + 10 # Offset for game area below header
    if sprite_type == 0:
        return  # empty
    elif sprite_type == 1:  # player
        oled.rect(x0, y0, SPRITE_SIZE, SPRITE_SIZE, 1)
        oled.pixel(x0+2, y0+3, 1)
        oled.pixel(x0+3, y0+2, 1)
        oled.pixel(x0+3, y0+3, 1)
        oled.pixel(x0+3, y0+4, 1)
        oled.pixel(x0+4, y0+3, 1)
    elif sprite_type == 2:  # wall
        oled.fill_rect(x0, y0, SPRITE_SIZE, SPRITE_SIZE, 1)
    elif sprite_type == 3:  # box
        oled.rect(x0, y0, SPRITE_SIZE, SPRITE_SIZE, 1)
        oled.pixel(x0+3, y0+3, 1)
    elif sprite_type == 4:  # target
        oled.pixel(x0+3, y0, 1)
        oled.pixel(x0+2, y0+1, 1)
        oled.pixel(x0+4, y0+1, 1)
        oled.pixel(x0+1, y0+2, 1)
        oled.pixel(x0+5, y0+2, 1)
        oled.pixel(x0+2, y0+3, 1)
        oled.pixel(x0+4, y0+3, 1)
        oled.pixel(x0+3, y0+4, 1)
    elif sprite_type == 5: # Box on target
        oled.fill_rect(x0, y0, SPRITE_SIZE, SPRITE_SIZE, 1) # Filled box for solved
        oled.rect(x0+1, y0+1, SPRITE_SIZE-2, SPRITE_SIZE-2, 0) # Inner clear rect
        oled.pixel(x0+3, y0+3, 0) # Clear center pixel

def find_player():
    global player_x, player_y
    for y in range(len(game_matrix)):
        for x in range(len(game_matrix[0])):
            if game_matrix[y][x] == 1:
                player_x, player_y = x, y
                return

def load_levels():
    global all_levels
    try:
        with open(LEVELS_FILE, 'r') as f:
            all_levels = ujson.load(f)
        print(f"Loaded {len(all_levels)} levels.")
    except Exception as e:
        print(f"Error loading levels: {e}")
        all_levels = [] # Fallback to empty if loading fails

def load_level(level_idx):
    global game_matrix, moves_count, pushes_count, start_time, game_won
    if not all_levels:
        return False # No levels loaded

    if level_idx >= len(all_levels):
        return False # No more levels

    level_data = all_levels[level_idx]["level"]
    # Deep copy the matrix to allow modifications during play
    game_matrix = [list(row) for row in level_data]
    find_player()
    moves_count = 0
    pushes_count = 0
    start_time = utime.ticks_ms()
    game_won = False
    print(f"Loaded level {level_idx + 1}")
    return True

def save_score(level_name, time_taken, moves, pushes):
    try:
        scores = []
        try:
            with open(SCORES_FILE, 'r') as f:
                scores = ujson.load(f)
        except OSError:
            # File not found, create a new one
            pass

        scores.append({
            "level": level_name,
            "time_ms": time_taken,
            "moves": moves,
            "pushes": pushes,
            "timestamp": utime.time() # Unix timestamp
        })

        with open(SCORES_FILE, 'w') as f:
            ujson.dump(scores, f)
        print("Score saved.")
    except Exception as e:
        print(f"Error saving score: {e}")

def check_win():
    for y in range(len(game_matrix)):
        for x in range(len(game_matrix[0])):
            # If a target (4) exists and no box (3 or 5) is on it, not won
            if all_levels[current_level_index]["level"][y][x] == 4 and game_matrix[y][x] not in (3, 5):
                return False
    return True

def draw_game_screen(oled, current_time_ms):
    oled.fill(0)

    # Header: Clock, Moves, Pushes
    current_hour = (current_time_ms // (1000 * 60 * 60)) % 24 # Crude hour
    current_minute = (current_time_ms // (1000 * 60)) % 60
    current_second = (current_time_ms // 1000) % 60
    oled.text(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}", 0, 0) # Current real time (approx)

    game_elapsed_ms = utime.ticks_diff(utime.ticks_ms(), start_time)
    game_minute = (game_elapsed_ms // (1000 * 60)) % 60
    game_second = (game_elapsed_ms // 1000) % 60
    oled.text(f"T:{game_minute:02d}:{game_second:02d}", 73, 0) # Game Timer

    oled.text(f"M:{moves_count}", 95, 20)
    oled.text(f"P:{pushes_count}", 95, 40) # Display pushes below moves

    # Draw game matrix
    for y in range(len(game_matrix)):
        for x in range(len(game_matrix[0])):
            # Special handling for boxes on targets
            if all_levels[current_level_index]["level"][y][x] == 4 and game_matrix[y][x] == 3:
                draw_sprite(oled, x, y,5) # Draw as box on target
            else:
                draw_sprite(oled, x, y, game_matrix[y][x])

    oled.show()

def show_win_screen(oled, play_sound, time_taken_ms):
    oled.fill(0)
    oled.text("LEVEL CLEARED!", 0, 20)
    oled.text(f"Moves: {moves_count}", 0, 30)
    oled.text(f"Pushes: {pushes_count}", 0, 40)
    game_minute = (time_taken_ms // (1000 * 60)) % 60
    game_second = (time_taken_ms // 1000) % 60
    oled.text(f"Time: {game_minute:02d}:{game_second:02d}", 0, 50)
    oled.show()
    for _ in range(3):
        play_sound(1000, 100)
        play_sound(1200, 100)
        utime.sleep_ms(200)
    utime.sleep(2) # Display for a bit longer

def move_player(oled, dx, dy, play_sound):
    global player_x, player_y, moves_count, pushes_count, game_matrix, game_won

    new_px, new_py = player_x + dx, player_y + dy
    
    # Check boundaries
    if not (0 <= new_px < len(game_matrix[0]) and 0 <= new_py < len(game_matrix)):
        return

    target_cell = game_matrix[new_py][new_px]

    if target_cell == 0 or target_cell == 4: # Empty or target
        game_matrix[player_y][player_x] = 0 # Clear current player position
        game_matrix[new_py][new_px] = 1     # Move player
        player_x, player_y = new_px, new_py
        moves_count += 1
        play_sound(300, 50)
    elif target_cell == 3: # It's a box
        new_bx, new_by = new_px + dx, new_py + dy
        # Check if next cell for box is valid and empty/target
        if (0 <= new_bx < len(game_matrix[0]) and 0 <= new_by < len(game_matrix) and
            (game_matrix[new_by][new_bx] == 0 or game_matrix[new_by][new_bx] == 4)):
            
            game_matrix[player_y][player_x] = 0 # Clear player
            game_matrix[new_py][new_px] = 1     # Move player to box's old spot
            game_matrix[new_by][new_bx] = 3     # Move box
            player_x, player_y = new_px, new_py
            moves_count += 1
            pushes_count += 1
            play_sound(500, 70) # Sound for pushing box
    
    # After any potential move, check for win condition
    if check_win():
        game_won = True
        time_taken_ms = utime.ticks_diff(utime.ticks_ms(), start_time)
        save_score(all_levels[current_level_index]["name"], time_taken_ms, moves_count, pushes_count)
        show_win_screen(oled, play_sound, time_taken_ms)
        return # Exit the game loop for this level


def main(oled, get_direction, play_sound):
    global current_level_index, game_won

    load_levels()
    if not all_levels:
        oled.fill(0)
        oled.text("No levels found!", 0, 20)
        oled.show()
        utime.sleep(2)
        return

    current_level_index = 0
    
    while True:
        if not load_level(current_level_index):
            oled.fill(0)
            oled.text("ALL LEVELS", 0, 20)
            oled.text("COMPLETED!", 0, 30)
            oled.show()
            play_sound(800, 150)
            play_sound(1000, 150)
            utime.sleep(3)
            return # Exit Sokoban mode

        game_won = False
        while not game_won:
            # Get current real time for display
            current_local_time = utime.localtime()
            current_time_ms_for_display = (current_local_time[3] * 3600 + current_local_time[4] * 60 + current_local_time[5]) * 1000 # Convert to ms for formatting

            draw_game_screen(oled, current_time_ms_for_display)
            direction = get_direction()
            
            if direction == "double_click":
                play_sound(200, 100)
                play_sound(100, 100)
                return # Exit Sokoban mode
            elif direction == "up":
                move_player(oled, 0, -1, play_sound)
            elif direction == "down":
                move_player(oled, 0, 1, play_sound)
            elif direction == "left":
                move_player(oled, -1, 0, play_sound)
            elif direction == "right":
                move_player(oled, 1, 0, play_sound)
            
            utime.sleep_ms(100) # Small delay to prevent over-sensitive movement

        # If game_won is true, it means current level is completed, move to next
        current_level_index += 1