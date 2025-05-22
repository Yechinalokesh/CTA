import pygame
import math
import time
import random

# --- Constants ---
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
FPS = 30

# Colors
ALMOST_BLACK = (20, 20, 30)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 180, 255) # Adjusted blue for better visibility of white eyeballs
NEON_PINK = (255, 0, 191)
NEON_RED = (255, 20, 50)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 165, 0)
BLUSH_PINK = (255, 105, 180, 150)
WHITE = (240, 240, 240)
DARK_BLUE_EYEBALL = (0, 80, 150) # Or use WHITE

DEFAULT_FEATURE_COLOR = NEON_BLUE # Changed to blue
EYEBALL_COLOR = WHITE

# --- Face States (Same as before) ---
STATE_IDLE = "idle"; STATE_TALKING = "talking"; STATE_HAPPY = "happy"; STATE_LAUGHING = "laughing"
STATE_THINKING = "thinking"; STATE_SLEEPING = "sleeping"; STATE_SAD = "sad"; STATE_ANGRY = "angry"
STATE_SURPRISED = "surprised"; STATE_CONFUSED = "confused"; STATE_LISTENING = "listening"
STATE_WINKING = "winking"; STATE_CURIOUS = "curious"; STATE_EMBARRASSED = "embarrassed"
STATE_SCHEMING = "scheming"; STATE_BORED = "bored"; STATE_PROUD = "proud"

# --- PyGame Setup ---
pygame.init()
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Reactive AI Avatar Face (Fullscreen)")
clock = pygame.time.Clock()
font_size = SCREEN_HEIGHT // 25
font = pygame.font.Font(None, font_size)
small_font_size = SCREEN_HEIGHT // 35
small_font = pygame.font.Font(None, small_font_size)

# --- Face Parameters (Scaled) ---
FACE_CENTER_X = SCREEN_WIDTH // 2
FACE_CENTER_Y = SCREEN_HEIGHT // 2
SCALE_FACTOR = SCREEN_HEIGHT / 700.0 # Use float for precision

EYE_OFFSET_X = int(60 * SCALE_FACTOR) # Slightly wider apart
EYE_OFFSET_Y = int(-40 * SCALE_FACTOR)
EYE_RADIUS_X = int(40 * SCALE_FACTOR)
EYE_RADIUS_Y = int(50 * SCALE_FACTOR)
EYE_THICKNESS = max(1, int(8 * SCALE_FACTOR))
EYEBALL_RADIUS = max(1, int(12 * SCALE_FACTOR)) # Eyeball size

EYEBROW_OFFSET_Y = int(-90 * SCALE_FACTOR)
EYEBROW_LENGTH = int(50 * SCALE_FACTOR)
EYEBROW_THICKNESS = max(1, int(7 * SCALE_FACTOR))

MOUTH_Y_OFFSET = int(55 * SCALE_FACTOR)
MOUTH_WIDTH = int(110 * SCALE_FACTOR)
MOUTH_HEIGHT_NORMAL = int(25 * SCALE_FACTOR)
MOUTH_THICKNESS = max(1, int(8 * SCALE_FACTOR))

CHEEK_OFFSET_X = int(80 * SCALE_FACTOR)
CHEEK_OFFSET_Y = int(20 * SCALE_FACTOR)
CHEEK_RADIUS = int(30 * SCALE_FACTOR)

# --- Animation Variables (Same as before) ---
current_state = STATE_IDLE
current_face_color = DEFAULT_FEATURE_COLOR
talk_anim_speed = 0.15; last_talk_anim_time = 0; talk_cycle_count = 0
blink_interval = random.uniform(2.5, 5.0); next_blink_time = time.time() + blink_interval
blink_duration = 0.15; is_blinking = False; blink_end_time = 0
vertical_offset = 0; horizontal_offset = 0; is_nodding = False; is_shaking = False
nod_shake_amplitude = int(6 * SCALE_FACTOR); nod_shake_speed = 0.1
last_nod_shake_time = 0; nod_shake_phase = 0

# --- Helper: Get current feature color ---
def get_feature_color(state):
    if state == STATE_ANGRY: return NEON_RED
    if state == STATE_EMBARRASSED: return NEON_PINK
    return current_face_color

# --- Drawing Functions ---
def draw_eyebrows(state, base_x, base_y, color):
    # (Largely same, ensure scaling is applied if any direct numbers were missed)
    # ... (Previous eyebrow code was mostly fine with scaling)
    left_start_x = base_x - EYE_OFFSET_X - EYEBROW_LENGTH // 2
    left_end_x = base_x - EYE_OFFSET_X + EYEBROW_LENGTH // 2
    right_start_x = base_x + EYE_OFFSET_X - EYEBROW_LENGTH // 2
    right_end_x = base_x + EYE_OFFSET_X + EYEBROW_LENGTH // 2
    y_pos = base_y + EYEBROW_OFFSET_Y
    scaled_offset_5 = int(5 * SCALE_FACTOR)
    scaled_offset_8 = int(8 * SCALE_FACTOR)
    scaled_offset_10 = int(10 * SCALE_FACTOR)
    scaled_offset_3 = int(3 * SCALE_FACTOR)


    if state == STATE_ANGRY:
        pygame.draw.line(screen, color, (left_start_x, y_pos - scaled_offset_5), (left_end_x, y_pos + scaled_offset_5), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos + scaled_offset_5), (right_end_x, y_pos - scaled_offset_5), EYEBROW_THICKNESS)
    elif state == STATE_SAD:
        pygame.draw.line(screen, color, (left_start_x, y_pos + scaled_offset_5), (left_end_x, y_pos - scaled_offset_5), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos - scaled_offset_5), (right_end_x, y_pos + scaled_offset_5), EYEBROW_THICKNESS)
    elif state == STATE_SURPRISED or state == STATE_PROUD:
        pygame.draw.line(screen, color, (left_start_x, y_pos - scaled_offset_10), (left_end_x, y_pos - scaled_offset_10), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos - scaled_offset_10), (right_end_x, y_pos - scaled_offset_10), EYEBROW_THICKNESS)
    elif state == STATE_CONFUSED or state == STATE_CURIOUS or state == STATE_SCHEMING:
        pygame.draw.line(screen, color, (left_start_x, y_pos - scaled_offset_8), (left_end_x, y_pos - scaled_offset_8), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos), (right_end_x, y_pos), EYEBROW_THICKNESS)
    elif state == STATE_EMBARRASSED or state == STATE_BORED:
        pygame.draw.line(screen, color, (left_start_x, y_pos + scaled_offset_3), (left_end_x, y_pos + scaled_offset_3), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos + scaled_offset_3), (right_end_x, y_pos + scaled_offset_3), EYEBROW_THICKNESS)
    elif state not in [STATE_SLEEPING, STATE_WINKING]:
        pygame.draw.line(screen, color, (left_start_x, y_pos), (left_end_x, y_pos), EYEBROW_THICKNESS)
        pygame.draw.line(screen, color, (right_start_x, y_pos), (right_end_x, y_pos), EYEBROW_THICKNESS)


def _draw_single_eye(eye_x, eye_y, state, is_wink_eye, is_blinking_now, color):
    """Helper to draw one eye and its eyeball."""
    eye_rect_base = pygame.Rect(eye_x - EYE_RADIUS_X // 2, eye_y - EYE_RADIUS_Y // 2, EYE_RADIUS_X, EYE_RADIUS_Y)
    draw_eyeball_flag = True # Assume eyeball is drawn unless eye is closed

    if is_blinking_now:
        pygame.draw.line(screen, color, (eye_x - EYE_RADIUS_X // 2, eye_y), (eye_x + EYE_RADIUS_X // 2, eye_y), EYE_THICKNESS)
        draw_eyeball_flag = False
        return # Blinking overrides everything for this eye

    # Specific state drawing
    if is_wink_eye and state == STATE_WINKING:
        # Draw wink shape (downward arc)
        wink_rect = pygame.Rect(eye_x - EYE_RADIUS_X // 2, eye_y - EYE_RADIUS_Y // 3, EYE_RADIUS_X, EYE_RADIUS_Y // 1.5)
        pygame.draw.arc(screen, color, wink_rect, math.radians(10), math.radians(170), EYE_THICKNESS + max(1,int(1*SCALE_FACTOR)))
        draw_eyeball_flag = False
    elif state == STATE_SLEEPING:
        pygame.draw.line(screen, color, (eye_x - EYE_RADIUS_X // 2, eye_y), (eye_x + EYE_RADIUS_X // 2, eye_y), EYE_THICKNESS)
        draw_eyeball_flag = False
    elif state in [STATE_IDLE, STATE_TALKING, STATE_LISTENING, STATE_PROUD]:
        pygame.draw.ellipse(screen, color, eye_rect_base, EYE_THICKNESS)
    elif state == STATE_THINKING or state == STATE_SCHEMING or state == STATE_CONFUSED or state == STATE_CURIOUS:
        temp_y_r = EYE_RADIUS_Y * (0.7 if state != STATE_CURIOUS else 0.85) # Curious less narrowed
        current_eye_rect = pygame.Rect(eye_x - EYE_RADIUS_X // 2, eye_y - int(temp_y_r) // 2, EYE_RADIUS_X, int(temp_y_r))
        pygame.draw.ellipse(screen, color, current_eye_rect, EYE_THICKNESS)
    elif state == STATE_EMBARRASSED:
        temp_y_r = EYE_RADIUS_Y * 0.8
        current_eye_rect = pygame.Rect(eye_x - EYE_RADIUS_X // 2, eye_y - int(temp_y_r) // 2, EYE_RADIUS_X, int(temp_y_r))
        pygame.draw.ellipse(screen, color, current_eye_rect, EYE_THICKNESS) # Consider slight downward gaze for eyeball
    elif state == STATE_BORED:
        temp_y_r = EYE_RADIUS_Y * 0.5
        current_eye_rect = pygame.Rect(eye_x - EYE_RADIUS_X // 2, eye_y - int(temp_y_r) // 2, EYE_RADIUS_X, int(temp_y_r))
        pygame.draw.ellipse(screen, color, current_eye_rect, EYE_THICKNESS)
    elif state == STATE_HAPPY or state == STATE_LAUGHING or (state == STATE_WINKING and not is_wink_eye): # Non-winked eye is happy
        start_angle = math.radians(200) if state == STATE_HAPPY or state == STATE_WINKING else math.radians(220)
        end_angle = math.radians(340) if state == STATE_HAPPY or state == STATE_WINKING else math.radians(320)
        thick = EYE_THICKNESS + (max(1,int(2*SCALE_FACTOR)) if state == STATE_LAUGHING else 0)
        pygame.draw.arc(screen, color, eye_rect_base, start_angle, end_angle, thick)
    elif state == STATE_SAD:
        # Slanted lines for sad eyes
        pygame.draw.line(screen, color,
                         (eye_x - EYE_RADIUS_X // 2, eye_y - int(5*SCALE_FACTOR) if not is_wink_eye else eye_y + int(5*SCALE_FACTOR)), # Example: left eye normal slant, right eye inverted
                         (eye_x + EYE_RADIUS_X // 2, eye_y + int(5*SCALE_FACTOR) if not is_wink_eye else eye_y - int(5*SCALE_FACTOR)), EYE_THICKNESS)
        draw_eyeball_flag = False # Usually no distinct eyeball for this style of sad eye
    elif state == STATE_ANGRY:
        temp_y_r = EYE_RADIUS_Y * 0.6
        current_eye_rect = pygame.Rect(eye_x - EYE_RADIUS_X // 2, eye_y - int(temp_y_r) // 2, EYE_RADIUS_X, int(temp_y_r))
        pygame.draw.ellipse(screen, color, current_eye_rect, EYE_THICKNESS)
    elif state == STATE_SURPRISED:
        radius_mult = 1.2 # Slightly less extreme
        current_eye_rect = pygame.Rect(eye_x - int(EYE_RADIUS_X*radius_mult)//2, eye_y - int(EYE_RADIUS_Y*radius_mult)//2, int(EYE_RADIUS_X*radius_mult), int(EYE_RADIUS_Y*radius_mult))
        pygame.draw.ellipse(screen, color, current_eye_rect, EYE_THICKNESS)
    else: # Fallback to default idle eye
        pygame.draw.ellipse(screen, color, eye_rect_base, EYE_THICKNESS)


    # --- Draw Eyeball ---
    if draw_eyeball_flag:
        eyeball_x_pos = eye_x
        eyeball_y_pos = eye_y
        # TODO: Add gaze logic here to adjust eyeball_x_pos, eyeball_y_pos
        # For now, centered. Can be slightly shifted for emotions too.
        if state == STATE_EMBARRASSED: eyeball_y_pos += int(3 * SCALE_FACTOR) # Look slightly down
        if state == STATE_SURPRISED or state == STATE_CURIOUS : eyeball_y_pos -= int(2 * SCALE_FACTOR) # Look slightly up

        pygame.draw.circle(screen, EYEBALL_COLOR, (eyeball_x_pos, eyeball_y_pos), EYEBALL_RADIUS, 0) # 0 for filled


def draw_eyes(state, blink_active, base_x, base_y, color):
    left_eye_x = base_x - EYE_OFFSET_X
    right_eye_x = base_x + EYE_OFFSET_X
    eye_y = base_y + EYE_OFFSET_Y # Common y for both eyes' centers

    # Determine if the current blink cycle applies to these eyes
    # If winking, only the non-winked eye participates in general blinking
    left_blinking_now = blink_active and (state != STATE_WINKING)
    right_blinking_now = blink_active # Winked eye doesn't blink via general blink_active

    _draw_single_eye(left_eye_x, eye_y, state, False, left_blinking_now, color)
    _draw_single_eye(right_eye_x, eye_y, state, True, right_blinking_now, color) # True for is_wink_eye potential

    # Cheeks for embarrassed - drawn after eyes
    if state == STATE_EMBARRASSED:
        s = pygame.Surface((CHEEK_RADIUS*2, CHEEK_RADIUS*2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, BLUSH_PINK, s.get_rect(),0)
        screen.blit(s, (base_x - CHEEK_OFFSET_X - CHEEK_RADIUS, base_y + CHEEK_OFFSET_Y - CHEEK_RADIUS))
        screen.blit(s, (base_x + CHEEK_OFFSET_X - CHEEK_RADIUS, base_y + CHEEK_OFFSET_Y - CHEEK_RADIUS))


def draw_mouth(state, cycle, base_x, base_y, color): # Removed redundant mouth_is_open_for_talk
    mouth_center_x = base_x
    mouth_center_y = base_y + MOUTH_Y_OFFSET

    if state == STATE_IDLE or state == STATE_LISTENING or state == STATE_PROUD:
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y - MOUTH_HEIGHT_NORMAL // 4, MOUTH_WIDTH, MOUTH_HEIGHT_NORMAL)
        pygame.draw.arc(screen, color, rect, math.radians(200), math.radians(340), MOUTH_THICKNESS)
    elif state == STATE_TALKING:
        h_mult, w_mult, shape_type = 1.0, 1.0, "ellipse"
        # Define y_pos_adj for each phoneme shape to keep baseline more consistent or intentionally shift
        y_pos_adj = 0

        if cycle % 4 == 0:  h_mult, w_mult = 1.3, 0.8; y_pos_adj = int(2 * SCALE_FACTOR) # Open "O" slightly lower
        elif cycle % 4 == 1:h_mult, w_mult = 0.8, 1.0 # Medium "oo"
        elif cycle % 4 == 2:h_mult, w_mult, shape_type = 0.5, 1.2, "ellipse" # Wider "ee"
        else:               h_mult, w_mult, shape_type = 0.2, 1.1, "line" # Closed "mm"
        
        current_mouth_h = int(MOUTH_HEIGHT_NORMAL * h_mult)
        current_mouth_w = int(MOUTH_WIDTH * w_mult)
        
        if shape_type == "ellipse":
            pygame.draw.ellipse(screen, color, 
                                (mouth_center_x - current_mouth_w // 2, 
                                 mouth_center_y - current_mouth_h // 2 + y_pos_adj,
                                 current_mouth_w, current_mouth_h), MOUTH_THICKNESS)
        elif shape_type == "line":
            pygame.draw.line(screen, color, 
                             (mouth_center_x - current_mouth_w // 2, mouth_center_y + y_pos_adj), 
                             (mouth_center_x + current_mouth_w // 2, mouth_center_y + y_pos_adj), MOUTH_THICKNESS)
    # ... (rest of mouth states, ensure scaling for any direct numbers)
    elif state == STATE_HAPPY or state == STATE_WINKING:
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y - MOUTH_HEIGHT_NORMAL // 2, MOUTH_WIDTH, int(MOUTH_HEIGHT_NORMAL * 1.5))
        pygame.draw.arc(screen, color, rect, math.radians(190), math.radians(350), MOUTH_THICKNESS)
    elif state == STATE_LAUGHING:
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 1.5, mouth_center_y - MOUTH_HEIGHT_NORMAL, int(MOUTH_WIDTH * 1.3), int(MOUTH_HEIGHT_NORMAL * 2))
        pygame.draw.arc(screen, color, rect, math.radians(180), math.radians(360), MOUTH_THICKNESS)
    elif state == STATE_THINKING or state == STATE_BORED:
        pygame.draw.line(screen, color, (mouth_center_x - MOUTH_WIDTH // 2.5, mouth_center_y), (mouth_center_x + MOUTH_WIDTH // 2.5, mouth_center_y), MOUTH_THICKNESS)
    elif state == STATE_CURIOUS:
         pygame.draw.ellipse(screen, color, (mouth_center_x - MOUTH_WIDTH // 4, mouth_center_y - MOUTH_HEIGHT_NORMAL // 4, MOUTH_WIDTH // 2, MOUTH_HEIGHT_NORMAL // 1.5), MOUTH_THICKNESS)
    elif state == STATE_SCHEMING:
        s_5 = int(5*SCALE_FACTOR); s_2 = int(2*SCALE_FACTOR)
        points = [(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y + s_5), (mouth_center_x - MOUTH_WIDTH // 4, mouth_center_y - s_5), (mouth_center_x + MOUTH_WIDTH // 2, mouth_center_y + s_2)]
        pygame.draw.lines(screen, color, False, points, MOUTH_THICKNESS)
    elif state == STATE_EMBARRASSED:
        s_2 = int(2*SCALE_FACTOR); s_3 = int(3*SCALE_FACTOR)
        pygame.draw.line(screen, color, (mouth_center_x - MOUTH_WIDTH // 3, mouth_center_y + s_2), (mouth_center_x + MOUTH_WIDTH // 3, mouth_center_y + s_3), MOUTH_THICKNESS)
    elif state == STATE_SLEEPING:
        pygame.draw.ellipse(screen, color, (mouth_center_x - MOUTH_WIDTH // 4, mouth_center_y, MOUTH_WIDTH // 2, MOUTH_HEIGHT_NORMAL // 2), MOUTH_THICKNESS)
    elif state == STATE_SAD:
        rect = pygame.Rect(mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y + MOUTH_HEIGHT_NORMAL // 3, MOUTH_WIDTH, MOUTH_HEIGHT_NORMAL)
        pygame.draw.arc(screen, color, rect, math.radians(20), math.radians(160), MOUTH_THICKNESS)
    elif state == STATE_ANGRY:
        pygame.draw.line(screen, color, (mouth_center_x - MOUTH_WIDTH // 2, mouth_center_y + int(5*SCALE_FACTOR)), (mouth_center_x + MOUTH_WIDTH // 2, mouth_center_y + int(5*SCALE_FACTOR)), MOUTH_THICKNESS + max(1,int(2*SCALE_FACTOR)))
    elif state == STATE_SURPRISED:
        pygame.draw.ellipse(screen, color, (mouth_center_x - MOUTH_WIDTH // 2.5, mouth_center_y - MOUTH_HEIGHT_NORMAL // 1.5, int(MOUTH_WIDTH // 1.2), int(MOUTH_HEIGHT_NORMAL * 1.5)), MOUTH_THICKNESS)
    elif state == STATE_CONFUSED:
        s_5 = int(5*SCALE_FACTOR); s_2 = int(2*SCALE_FACTOR)
        points = [(mouth_center_x - MOUTH_WIDTH // 2.5, mouth_center_y), (mouth_center_x, mouth_center_y + s_5), (mouth_center_x + MOUTH_WIDTH // 2.5, mouth_center_y - s_2)]
        pygame.draw.lines(screen, color, False, points, MOUTH_THICKNESS)


# --- Communication & State Management (Simplified Simulation) ---
# (Same as before, just ensure process_ai_output covers new states if keywords added)
ai_spoken_text = ""
ai_target_state = STATE_IDLE
expression_hold_time = 1.5 # seconds
last_text_time = 0

def process_ai_output(text):
    global ai_target_state
    text_lower = text.lower()
    if not text:
        if current_state == STATE_TALKING: ai_target_state = STATE_IDLE
        return

    ai_target_state = STATE_TALKING # Default if there's text

    if any(word in text_lower for word in ["joke", "haha", "funny", "lol"]): ai_target_state = STATE_LAUGHING
    elif any(word in text_lower for word in ["great", "awesome", "happy", "wonderful", "congrats", "yay"]): ai_target_state = STATE_HAPPY
    elif any(word in text_lower for word in ["proud of", "well done"]): ai_target_state = STATE_PROUD
    elif any(word in text_lower for word in ["sorry", "sad", "unfortunately", "alas"]): ai_target_state = STATE_SAD
    elif any(word in text_lower for word in ["hmm", "think", "wonder", "maybe", "perhaps"]): ai_target_state = STATE_THINKING
    elif any(word in text_lower for word in ["curious", "tell me more"]): ai_target_state = STATE_CURIOUS
    elif any(word in text_lower for word in ["angry", "stop", "don't", "problem", "error"]): ai_target_state = STATE_ANGRY
    elif any(word in text_lower for word in ["wow", "really", "omg", "amazing", "look", "surprised"]): ai_target_state = STATE_SURPRISED
    elif any(word in text_lower for word in ["what?", "huh?", "confused", "don't understand"]): ai_target_state = STATE_CONFUSED
    elif any(word in text_lower for word in ["wink", ";)"]): ai_target_state = STATE_WINKING
    elif any(word in text_lower for word in ["oops", "shy", "blush", "embarrassed"]): ai_target_state = STATE_EMBARRASSED
    elif any(word in text_lower for word in ["mischief", "scheming", "hehe"]): ai_target_state = STATE_SCHEMING
    elif any(word in text_lower for word in ["bored", "sigh", "whatever", "dull"]): ai_target_state = STATE_BORED

# --- Main Loop ---
# (Largely same, key assignments might need review for new states)
running = True
simulated_texts = {
    pygame.K_F1: ("Hello there! I am your AI assistant.", STATE_IDLE),
    pygame.K_F2: ("That's a great joke! Hahaha!", STATE_LAUGHING),
    pygame.K_F3: ("I'm so happy to help you today.", STATE_HAPPY),
    pygame.K_F4: ("Hmm, let me think about that for a moment.", STATE_THINKING),
    pygame.K_F5: ("I'm feeling a bit tired, going to sleep now.", STATE_SLEEPING),
    pygame.K_F6: ("Oh, I'm so sorry to hear that.", STATE_SAD),
    pygame.K_F7: ("That's not right! I'm a bit angry.", STATE_ANGRY),
    pygame.K_F8: ("Wow! That's amazing news!", STATE_SURPRISED),
    pygame.K_F9: ("Huh? I don't quite understand what you mean.", STATE_CONFUSED),
    pygame.K_F10: ("I'm listening to your request.", STATE_LISTENING),
    pygame.K_F11: ("Just kidding! ;) Gotcha!", STATE_WINKING),
    pygame.K_F12: ("Oh, um, that's a bit embarrassing.", STATE_EMBARRASSED),
    pygame.K_PAGEUP: ("Hehe, I have a little plan...", STATE_SCHEMING),
    pygame.K_PAGEDOWN: ("This is rather dull, isn't it?", STATE_BORED),
    pygame.K_HOME: ("I'm quite proud of that achievement!", STATE_PROUD),
    pygame.K_END: ("I'm curious about what's next.", STATE_CURIOUS),
    pygame.K_SPACE: ("", STATE_IDLE) # Clear text, go to idle
}
key_to_color = { # Keys to change avatar color
    pygame.K_c: NEON_BLUE, pygame.K_v: NEON_GREEN, pygame.K_b: NEON_PINK, pygame.K_m: NEON_ORANGE
}

while running:
    current_time = time.time()
    actual_center_x = FACE_CENTER_X + horizontal_offset
    actual_center_y = FACE_CENTER_Y + vertical_offset
    current_feature_color_to_draw = get_feature_color(current_state)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            
            if event.key in simulated_texts:
                ai_spoken_text, forced_state = simulated_texts[event.key]
                process_ai_output(ai_spoken_text)
                if ai_spoken_text == "" and forced_state != STATE_IDLE : # For states like listening, sleeping
                     ai_target_state = forced_state
                current_state = ai_target_state # Immediately update for responsiveness
                last_text_time = current_time
                is_nodding = is_shaking = False # Reset movement on new speech/state
                vertical_offset = horizontal_offset = 0
            elif event.key in key_to_color:
                current_face_color = key_to_color[event.key]
                DEFAULT_FEATURE_COLOR = current_face_color # Update default if changed by user

            elif event.key == pygame.K_UP: is_nodding = not is_nodding; is_shaking = False
            elif event.key == pygame.K_LEFT: is_shaking = not is_shaking; is_nodding = False
    
    # State transition logic (remains largely the same)
    if current_state == STATE_TALKING and not ai_spoken_text: # If text finished, transition
        if current_time - last_text_time > 0.2: # Brief pause after talking
            current_state = STATE_IDLE # Default to idle after talking
    elif current_state not in [STATE_TALKING, STATE_IDLE, STATE_SLEEPING, STATE_LISTENING, STATE_THINKING]:
        # For expressions like happy, sad, angry, hold them for a bit then revert to idle
        if current_time - last_text_time > expression_hold_time:
            if not ai_spoken_text: # Only revert if no new text is making it talk
                current_state = STATE_IDLE

    # Animation updates (remains largely the same)
    if current_state == STATE_TALKING and ai_spoken_text:
        if current_time - last_talk_anim_time > talk_anim_speed:
            talk_cycle_count = (talk_cycle_count + 1) % 100 # Cycle for varied mouth shapes
            last_talk_anim_time = current_time
    else: talk_cycle_count = 0

    if is_blinking and current_time >= blink_end_time:
        is_blinking = False
        next_blink_time = current_time + random.uniform(2.0, 5.0) # Randomize next blink
    if not is_blinking and current_time >= next_blink_time and current_state != STATE_SLEEPING:
        is_blinking = True
        blink_end_time = current_time + blink_duration

    if is_nodding or is_shaking: # Nod/Shake Animation
        if current_time - last_nod_shake_time > nod_shake_speed:
            nod_shake_phase = (nod_shake_phase + 1) % 4
            last_nod_shake_time = current_time
            if is_nodding: vertical_offset = [0, -nod_shake_amplitude, 0, nod_shake_amplitude][nod_shake_phase]
            elif is_shaking: horizontal_offset = [0, -nod_shake_amplitude, 0, nod_shake_amplitude][nod_shake_phase]
    else: vertical_offset = horizontal_offset = nod_shake_phase = 0


    # --- Drawing ---
    screen.fill(ALMOST_BLACK)
    draw_eyebrows(current_state, actual_center_x, actual_center_y, current_feature_color_to_draw)
    draw_eyes(current_state, is_blinking, actual_center_x, actual_center_y, current_feature_color_to_draw)
    draw_mouth(current_state, talk_cycle_count, actual_center_x, actual_center_y, current_feature_color_to_draw)

    # Display current state and simulated text
    state_surf = font.render(f"State: {current_state.upper()}", True, current_feature_color_to_draw) # Use current color for state text
    text_surf = font.render(f"AI: {ai_spoken_text[:70]}{'...' if len(ai_spoken_text)>70 else ''}", True, current_feature_color_to_draw) # And for AI text
    screen.blit(state_surf, (20, 20))
    screen.blit(text_surf, (20, 20 + font_size + 5))
    
    help_text1 = small_font.render("F1-F12, PgUp/PgDn, Home/End: States. ESC: Quit.", True, NEON_YELLOW)
    help_text2 = small_font.render("UP/LEFT: Nod/Shake. C,V,B,M: Change Face Color.", True, NEON_YELLOW)
    screen.blit(help_text1, (20, SCREEN_HEIGHT - (small_font_size + 5) * 2 - 10))
    screen.blit(help_text2, (20, SCREEN_HEIGHT - small_font_size - 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
