import pygame
import math
import time
import random # For blink randomness

# --- Constants (Mostly same as before) ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
FPS = 30
ALMOST_BLACK = (20, 20, 30)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 221, 255)
NEON_PINK = (255, 0, 191)
NEON_RED = (255, 20, 50)
NEON_YELLOW = (255, 255, 0)
FEATURE_COLOR = NEON_GREEN

# --- Face States ---
STATE_IDLE = "idle"
STATE_TALKING = "talking"
STATE_HAPPY = "happy"
STATE_LAUGHING = "laughing"
STATE_THINKING = "thinking"
STATE_SLEEPING = "sleeping"
STATE_SAD = "sad"
STATE_ANGRY = "angry"
STATE_SURPRISED = "surprised"
STATE_CONFUSED = "confused"
STATE_LISTENING = "listening" # New

# --- PyGame Setup (Same as before) ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Reactive AI Avatar Face")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 26) # Slightly smaller for more text

# --- Face Parameters (Can be adjusted) ---
FACE_CENTER_X = SCREEN_WIDTH // 2
FACE_CENTER_Y = SCREEN_HEIGHT // 2
EYE_OFFSET_X = 50
EYE_OFFSET_Y = -30
EYE_RADIUS_X = 35
EYE_RADIUS_Y = 45
EYE_THICKNESS = 8
EYEBROW_OFFSET_Y = -65 # Above eyes
EYEBROW_LENGTH = 40
EYEBROW_THICKNESS = 6

MOUTH_Y_OFFSET = 40
MOUTH_WIDTH = 100
MOUTH_HEIGHT_NORMAL = 20
MOUTH_THICKNESS = 8

# --- Animation Variables ---
current_state = STATE_IDLE
current_face_color = FEATURE_COLOR # Color can also be part of the state

# Talking animation
talk_anim_speed = 0.15  # Faster for more natural feel
last_talk_anim_time = 0
mouth_open_talk = False
talk_cycle_count = 0 # For varying mouth shapes during talk

# Blinking animation
blink_interval = random.uniform(2.5, 5.0)
next_blink_time = time.time() + blink_interval
blink_duration = 0.15
is_blinking = False
blink_end_time = 0

# Nodding/Shaking (subtle face offset)
vertical_offset = 0
horizontal_offset = 0
is_nodding = False
is_shaking = False
nod_shake_amplitude = 5
nod_shake_speed = 0.1
last_nod_shake_time = 0
nod_shake_phase = 0 # 0: center, 1: up/right, 2: center, 3: down/left

# --- Helper: Get current feature color (can be state-dependent) ---
def get_feature_color(state):
    if state == STATE_ANGRY:
        return NEON_RED
    # elif state == STATE_SAD: # Could make it slightly desaturated or blueish
    #     return NEON_BLUE
    return current_face_color


# --- Drawing Functions (Modified and New) ---
def draw_eyebrows(state, base_x, base_y, color):
    left_start_x = base_x - EYE_OFFSET_X - EYEBROW_LENGTH // 2
    left_end_x = base_x - EYE_OFFSET_X + EYEBROW_LENGTH // 2
    right_start_x = base_x + EYE_OFFSET_X - EYEBROW_LENGTH // 2
    right_end_x = base_x + EYE_OFFSET_X + EYEBROW_LENGTH // 2
    
    y_pos = base_y + EYEBROW_OFFSET_Y

    if state == STATE_ANGRY:
        # Angled down towards center
        pygame.draw.line(screen, color, (left_start_x, y_pos - 5), (left_end_x, y_pos + 5), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos + 5), (right_end_x, y_pos - 5), EYEBROW_THICKNESS)
    elif state == STATE_SAD:
        # Angled up towards center (opposite of angry)
        pygame.draw.line(screen, color, (left_start_x, y_pos + 5), (left_end_x, y_pos - 5), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos - 5), (right_end_x, y_pos + 5), EYEBROW_THICKNESS)
    elif state == STATE_SURPRISED:
        # Raised high
        pygame.draw.line(screen, color, (left_start_x, y_pos - 10), (left_end_x, y_pos - 10), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos - 10), (right_end_x, y_pos - 10), EYEBROW_THICKNESS)
    elif state == STATE_CONFUSED:
        # One raised, one normal/lowered
        pygame.draw.line(screen, color, (left_start_x, y_pos - 8), (left_end_x, y_pos - 8), EYEBROW_THICKNESS) # Raised
        pygame.draw.line(screen, color, (right_start_x, y_pos), (right_end_x, y_pos), EYEBROW_THICKNESS) # Normal
    elif state not in [STATE_SLEEPING]: # No eyebrows if sleeping or default
        # Default straight eyebrows
        pygame.draw.line(screen, color, (left_start_x, y_pos), (left_end_x, y_pos), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos), (right_end_x, y_pos), EYEBROW_THICKNESS)


def draw_eyes(state, blink_active, base_x, base_y, color):
    eye_left_pos_x = base_x - EYE_OFFSET_X
    eye_right_pos_x = base_x + EYE_OFFSET_X
    eye_pos_y = base_y + EYE_OFFSET_Y
    
    if blink_active: # Eyes closed for blink
        pygame.draw.line(screen, color, (eye_left_pos_x - EYE_RADIUS_X // 2, eye_pos_y), (eye_left_pos_x + EYE_RADIUS_X // 2, eye_pos_y), EYE_THICKNESS)
        pygame.draw.line(screen, color, (eye_right_pos_x - EYE_RADIUS_X // 2, eye_pos_y), (eye_right_pos_x + EYE_RADIUS_X // 2, eye_pos_y), EYE_THICKNESS)
        return

    if state in [STATE_IDLE, STATE_TALKING, STATE_THINKING, STATE_LISTENING]:
        pygame.draw.ellipse(screen, color, (eye_left_pos_x - EYE_RADIUS_X//2, eye_pos_y - EYE_RADIUS_Y//2, EYE_RADIUS_X, EYE_RADIUS_Y), EYE_THICKNESS)
        pygame.draw.ellipse(screen, color, (eye_right_pos_x - EYE_RADIUS_X//2, eye_pos_y - EYE_RADIUS_Y//2, EYE_RADIUS_X, EYE_RADIUS_Y), EYE_THICKNESS)
        if state == STATE_THINKING: # Slightly narrowed one eye
             pygame.draw.ellipse(screen, color, (eye_right_pos_x - EYE_RADIUS_X//2, eye_pos_y - EYE_RADIUS_Y//3, EYE_RADIUS_X, EYE_RADIUS_Y * 0.7), EYE_THICKNESS)


    elif state == STATE_HAPPY or state == STATE_LAUGHING:
        arc_rect_left = pygame.Rect(eye_left_pos_x - EYE_RADIUS_X // 2, eye_pos_y - EYE_RADIUS_Y // 2, EYE_RADIUS_X, EYE_RADIUS_Y)
        arc_rect_right = pygame.Rect(eye_right_pos_x - EYE_RADIUS_X // 2, eye_right_pos_y - EYE_RADIUS_Y // 2, EYE_RADIUS_X, EYE_RADIUS_Y)
        start_angle = math.radians(200)
        end_angle = math.radians(340)
        if state == STATE_LAUGHING: # More squinted for laughing
            start_angle = math.radians(220)
            end_angle = math.radians(320)
        pygame.draw.arc(screen, color, arc_rect_left, start_angle, end_angle, EYE_THICKNESS + (2 if state == STATE_LAUGHING else 0))
        pygame.draw.arc(screen, color, arc_rect_right, start_angle, end_angle, EYE_THICKNESS + (2 if state == STATE_LAUGHING else 0))

    elif state == STATE_SAD:
        # Downward tilted lines or droopy ellipses
        pygame.draw.line(screen, color, (eye_left_pos_x - EYE_RADIUS_X // 2, eye_pos_y - 5), (eye_left_pos_x + EYE_RADIUS_X // 2, eye_pos_y + 5), EYE_THICKNESS)
        pygame.draw.line(screen, color, (eye_right_pos_x - EYE_RADIUS_X // 2, eye_pos_y + 5), (eye_right_pos_x + EYE_RADIUS_X // 2, eye_pos_y - 5), EYE_THICKNESS)
        # Optional: small tear drop
        # pygame.draw.ellipse(screen, NEON_BLUE, (eye_left_pos_x + 5, eye_pos_y + EYE_RADIUS_Y//2, 5, 10),0)


    elif state == STATE_ANGRY:
        # Narrowed, perhaps slightly angular
        rect_left = (eye_left_pos_x - EYE_RADIUS_X//2, eye_pos_y - EYE_RADIUS_Y//3, EYE_RADIUS_X, EYE_RADIUS_Y * 0.6)
        rect_right = (eye_right_pos_x - EYE_RADIUS_X//2, eye_pos_y - EYE_RADIUS_Y//3, EYE_RADIUS_X, EYE_RADIUS_Y * 0.6)
        pygame.draw.ellipse(screen, color, rect_left, EYE_THICKNESS)
        pygame.draw.ellipse(screen, color, rect_right, EYE_THICKNESS)

    elif state == STATE_SURPRISED:
        # Wide open circles
        radius_mult = 1.3
        pygame.draw.ellipse(screen, color, (eye_left_pos_x - (EYE_RADIUS_X*radius_mult)//2, eye_pos_y - (EYE_RADIUS_Y*radius_mult)//2, EYE_RADIUS_X*radius_mult, EYE_RADIUS_Y*radius_mult), EYE_THICKNESS)
        pygame.draw.ellipse(screen, color, (eye_right_pos_x - (EYE_RADIUS_X*radius_mult)//2, eye_pos_y - (EYE_RADIUS_Y*radius_mult)//2, EYE_RADIUS_X*radius_mult, EYE_RADIUS_Y*radius_mult), EYE_THICKNESS)
    
    elif state == STATE_SLEEPING:
        pygame.draw.line(screen, color, (eye_left_pos_x - EYE_RADIUS_X // 2, eye_pos_y), (eye_left_pos_x + EYE_RADIUS_X // 2, eye_pos_y), EYE_THICKNESS)
        pygame.draw.line(screen, color, (eye_right_pos_x - EYE_RADIUS_X // 2, eye_pos_y), (eye_right_pos_x + EYE_RADIUS_X // 2, eye_pos_y), EYE_THICKNESS)
    
    elif state == STATE_CONFUSED: # Similar to thinking but maybe one eye wider
        pygame.draw.ellipse(screen, color, (eye_left_pos_x - EYE_RADIUS_X//1.5, eye_pos_y - EYE_RADIUS_Y//1.5, EYE_RADIUS_X*1.2, EYE_RADIUS_Y*1.2), EYE_THICKNESS) # Wider
        pygame.draw.ellipse(screen, color, (eye_right_pos_x - EYE_RADIUS_X//2, eye_pos_y - EYE_RADIUS_Y//3, EYE_RADIUS_X, EYE_RADIUS_Y * 0.7), EYE_THICKNESS) # Narrowed


def draw_mouth(state, mouth_is_open_for_talk, cycle, base_x, base_y, color):
    mouth_center_x = base_x
    mouth_center_y = base_y + MOUTH_Y_OFFSET

    if state == STATE_IDLE or state == STATE_LISTENING:
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y - MOUTH_HEIGHT_NORMAL // 4, MOUTH_WIDTH, MOUTH_HEIGHT_NORMAL)
        pygame.draw.arc(screen, color, rect, math.radians(200), math.radians(340), MOUTH_THICKNESS)

    elif state == STATE_TALKING:
        # Vary mouth shape during talk cycle for more dynamism
        h_mult = 1.0
        w_mult = 1.0
        y_offset_mult = 1.0
        shape_type = "ellipse" # "ellipse", "rect_arc_open", "line"

        if cycle % 4 == 0: # Open wide "O"
            h_mult = 1.3
            w_mult = 0.8
            y_offset_mult = 1.6
        elif cycle % 4 == 1: # Medium open "oo"
            h_mult = 0.8
            w_mult = 1.0
            y_offset_mult = 1.0
        elif cycle % 4 == 2: # Wider, flatter "ee"
            h_mult = 0.5
            w_mult = 1.2
            y_offset_mult = 0.8
            shape_type = "ellipse"
        else: # Almost closed "mm"
            h_mult = 0.2
            w_mult = 1.1
            y_offset_mult = 0.5
            shape_type = "line"
        
        current_mouth_height = MOUTH_HEIGHT_NORMAL * h_mult
        current_mouth_width = MOUTH_WIDTH * w_mult
        
        if shape_type == "ellipse":
            pygame.draw.ellipse(screen, color, 
                                (mouth_center_x - current_mouth_width // 2, mouth_center_y - current_mouth_height / y_offset_mult, current_mouth_width, current_mouth_height), MOUTH_THICKNESS)
        elif shape_type == "line":
            pygame.draw.line(screen, color,
                             (mouth_center_x - current_mouth_width // 2, mouth_center_y),
                             (mouth_center_x + current_mouth_width // 2, mouth_center_y), MOUTH_THICKNESS)


    elif state == STATE_HAPPY:
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y - MOUTH_HEIGHT_NORMAL // 2, MOUTH_WIDTH, MOUTH_HEIGHT_NORMAL * 1.5)
        pygame.draw.arc(screen, color, rect, math.radians(190), math.radians(350), MOUTH_THICKNESS)
    
    elif state == STATE_LAUGHING:
        # Wider, more open happy mouth
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 1.5, mouth_center_y - MOUTH_HEIGHT_NORMAL, MOUTH_WIDTH * 1.3, MOUTH_HEIGHT_NORMAL * 2)
        pygame.draw.arc(screen, color, rect, math.radians(180), math.radians(360), MOUTH_THICKNESS) # Almost full half circle

    elif state == STATE_THINKING or state == STATE_CONFUSED:
        pygame.draw.line(screen, color, (mouth_center_x - MOUTH_WIDTH // 2.5, mouth_center_y), (mouth_center_x + MOUTH_WIDTH // 2.5, mouth_center_y), MOUTH_THICKNESS)
        if state == STATE_CONFUSED: # slight smirk/skew
            pygame.draw.line(screen, color, (mouth_center_x - MOUTH_WIDTH // 2.5, mouth_center_y), (mouth_center_x + MOUTH_WIDTH // 2.5 -10, mouth_center_y+5), MOUTH_THICKNESS)


    elif state == STATE_SLEEPING:
        pygame.draw.ellipse(screen, color, (mouth_center_x - MOUTH_WIDTH // 4, mouth_center_y, MOUTH_WIDTH // 2, MOUTH_HEIGHT_NORMAL // 2), MOUTH_THICKNESS)

    elif state == STATE_SAD:
        # Downward arc
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y + MOUTH_HEIGHT_NORMAL // 3, MOUTH_WIDTH, MOUTH_HEIGHT_NORMAL)
        pygame.draw.arc(screen, color, rect, math.radians(20), math.radians(160), MOUTH_THICKNESS) # Top part of circle, flipped

    elif state == STATE_ANGRY:
        # Tight, straight line, maybe slightly downturned corners
        pygame.draw.line(screen, color, (mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y + 5), (mouth_center_x + MOUTH_WIDTH // 2, mouth_center_y + 5), MOUTH_THICKNESS + 2)

    elif state == STATE_SURPRISED:
        # "O" shaped mouth
        pygame.draw.ellipse(screen, color, (mouth_center_x - MOUTH_WIDTH // 2.5, mouth_center_y - MOUTH_HEIGHT_NORMAL // 1.5, MOUTH_WIDTH // 1.2, MOUTH_HEIGHT_NORMAL * 1.5), MOUTH_THICKNESS)

# --- Communication with AI Backend (Simplified Simulation) ---
# In a real app, this would come from another thread/process via a queue or WebSocket
# For now, we'll simulate it with key presses that also set a "spoken text"
# and then infer state from that text.

ai_spoken_text = ""
ai_target_state = STATE_IDLE # The state the AI wants the avatar to be in

def process_ai_output(text):
    """
    Simple logic to determine avatar state from text.
    This would be much more sophisticated in the real AI.
    """
    global ai_target_state
    text_lower = text.lower()

    if not text: # If no text, could be listening or idle
        if current_state == STATE_TALKING: # Transition from talking to idle
             ai_target_state = STATE_IDLE
        # Keep current state if it's listening, thinking, etc.
        return

    # Default to talking if there's text
    ai_target_state = STATE_TALKING

    # Keyword-based emotion (override talking if specific emotion detected)
    if any(word in text_lower for word in ["joke", "haha", "funny", "lol"]):
        ai_target_state = STATE_LAUGHING
    elif any(word in text_lower for word in ["great", "awesome", "happy", "wonderful", "congrats", "yay"]):
        ai_target_state = STATE_HAPPY
    elif any(word in text_lower for word in ["sorry", "sad", "unfortunately", "alas"]):
        ai_target_state = STATE_SAD
    elif any(word in text_lower for word in ["hmm", "think", "wonder", "maybe", "perhaps"]):
        ai_target_state = STATE_THINKING
    elif any(word in text_lower for word in ["angry", "stop", "don't", "problem", "error"]): # Risky
        ai_target_state = STATE_ANGRY
    elif any(word in text_lower for word in ["wow", "really", "omg", "amazing", "look"]):
        ai_target_state = STATE_SURPRISED
    elif any(word in text_lower for word in ["what?", "huh?", "confused", "don't understand"]):
        ai_target_state = STATE_CONFUSED
    
    # Special non-text driven states (would be set by other AI logic)
    # e.g., if AI detects user inactivity for a long time -> STATE_SLEEPING
    # e.g., if AI is actively processing a user voice command -> STATE_LISTENING
    # e.g., if AI is waiting for a long API call -> STATE_THINKING

# --- Main Loop ---
running = True
simulated_texts = {
    pygame.K_1: ("Hello there! I am your AI assistant.", STATE_IDLE), # Initial greeting
    pygame.K_2: ("That's a great joke! Hahaha!", STATE_LAUGHING),
    pygame.K_3: ("I'm so happy to help you today.", STATE_HAPPY),
    pygame.K_4: ("Hmm, let me think about that for a moment.", STATE_THINKING),
    pygame.K_5: ("I'm feeling a bit tired, going to sleep now.", STATE_SLEEPING),
    pygame.K_6: ("Oh, I'm so sorry to hear that.", STATE_SAD),
    pygame.K_7: ("That's not right! I'm a bit angry.", STATE_ANGRY),
    pygame.K_8: ("Wow! That's amazing news!", STATE_SURPRISED),
    pygame.K_9: ("Huh? I don't quite understand what you mean.", STATE_CONFUSED),
    pygame.K_0: ("I'm listening to your request.", STATE_LISTENING),
    pygame.K_SPACE: ("", STATE_IDLE) # Clear text, go to idle
}

# Duration for which a non-talking state (like happy, sad) persists after text
expression_hold_time = 1.5 # seconds
last_text_time = 0

while running:
    current_time = time.time()
    actual_center_x = FACE_CENTER_X + horizontal_offset
    actual_center_y = FACE_CENTER_Y + vertical_offset
    current_feature_color_to_draw = get_feature_color(current_state)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: running = False
            if event.key in simulated_texts:
                ai_spoken_text, forced_state = simulated_texts[event.key]
                process_ai_output(ai_spoken_text) # This sets ai_target_state
                # If the key press directly implies a state (like sleeping), override inference
                if ai_spoken_text == "" and forced_state != STATE_IDLE : # for listening, sleeping
                     ai_target_state = forced_state
                current_state = ai_target_state # Immediately update for responsiveness
                last_text_time = current_time
                
                # Reset nodding/shaking
                is_nodding = False
                is_shaking = False
                vertical_offset = 0
                horizontal_offset = 0

            # Manual overrides for nod/shake (for testing)
            elif event.key == pygame.K_UP: is_nodding = not is_nodding; is_shaking = False
            elif event.key == pygame.K_LEFT: is_shaking = not is_shaking; is_nodding = False


    # State transition logic
    if current_state == STATE_TALKING and not ai_spoken_text: # If text finished, transition
        if current_time - last_text_time > 0.2: # Brief pause after talking
            current_state = STATE_IDLE # Default to idle after talking
    elif current_state != STATE_TALKING and current_state != STATE_IDLE and current_state != STATE_SLEEPING and current_state != STATE_LISTENING and current_state != STATE_THINKING:
        # For expressions like happy, sad, angry, hold them for a bit then revert to idle
        if current_time - last_text_time > expression_hold_time:
            if not ai_spoken_text: # Only revert if no new text is making it talk
                current_state = STATE_IDLE


    # Update animation variables
    if current_state == STATE_TALKING and ai_spoken_text:
        if current_time - last_talk_anim_time > talk_anim_speed:
            mouth_open_talk = not mouth_open_talk # Basic open/close for this variable
            talk_cycle_count = (talk_cycle_count + 1) % 100 # Cycle for varied mouth shapes
            last_talk_anim_time = current_time
    else:
        mouth_open_talk = False
        talk_cycle_count = 0

    if is_blinking and current_time >= blink_end_time:
        is_blinking = False
        next_blink_time = current_time + random.uniform(2.0, 5.0)
    if not is_blinking and current_time >= next_blink_time and current_state != STATE_SLEEPING:
        is_blinking = True
        blink_end_time = current_time + blink_duration

    # Nodding/Shaking animation (simple version)
    if is_nodding or is_shaking:
        if current_time - last_nod_shake_time > nod_shake_speed:
            nod_shake_phase = (nod_shake_phase + 1) % 4
            last_nod_shake_time = current_time
            if is_nodding:
                if nod_shake_phase == 0: vertical_offset = 0
                elif nod_shake_phase == 1: vertical_offset = -nod_shake_amplitude
                elif nod_shake_phase == 2: vertical_offset = 0
                elif nod_shake_phase == 3: vertical_offset = nod_shake_amplitude
            elif is_shaking:
                if nod_shake_phase == 0: horizontal_offset = 0
                elif nod_shake_phase == 1: horizontal_offset = -nod_shake_amplitude
                elif nod_shake_phase == 2: horizontal_offset = 0
                elif nod_shake_phase == 3: horizontal_offset = nod_shake_amplitude
    else:
        vertical_offset = 0
        horizontal_offset = 0
        nod_shake_phase = 0


    # --- Drawing ---
    screen.fill(ALMOST_BLACK)
    draw_eyebrows(current_state, actual_center_x, actual_center_y, current_feature_color_to_draw)
    draw_eyes(current_state, is_blinking, actual_center_x, actual_center_y, current_feature_color_to_draw)
    draw_mouth(current_state, mouth_open_talk, talk_cycle_count, actual_center_x, actual_center_y, current_feature_color_to_draw)

    # Display current state and simulated text
    state_surf = font.render(f"State: {current_state.upper()}", True, NEON_GREEN)
    text_surf = font.render(f"AI Says: {ai_spoken_text[:35]}{'...' if len(ai_spoken_text)>35 else ''}", True, NEON_GREEN)
    screen.blit(state_surf, (10, 10))
    screen.blit(text_surf, (10, 35))
    help_text = font.render("Keys 1-0 simulate AI speech/state. Q=Quit. UP/LEFT=Nod/Shake", True, NEON_YELLOW)
    screen.blit(help_text, (10, SCREEN_HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
