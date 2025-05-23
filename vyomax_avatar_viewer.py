import pygame
import math
import time
import random

# --- Constants ---
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
FPS = 30

# Colors - Vector/Digital Style
DIGITAL_BLACK = (15, 18, 22)
SCREEN_BLUE_BG = (30, 40, 60)
CYBER_BLUE = (0, 200, 255)
ENERGY_GREEN = (20, 255, 100)
WARNING_RED = (255, 50, 50)
DATA_YELLOW = (255, 220, 0)
WHITE_HIGHLIGHT = (240, 240, 255)
ROBOT_BODY_LIGHT_GRAY = (200, 205, 210)
ROBOT_BODY_DARK_GRAY = (100, 105, 110)
HEART_PINK = (255, 105, 180)

DEFAULT_FEATURE_COLOR = CYBER_BLUE
HAND_COLOR = ROBOT_BODY_LIGHT_GRAY
EYEBALL_COLOR = WHITE_HIGHLIGHT

# --- Face & Hand States ---
# Facial States
STATE_OFFLINE = "offline"; STATE_ENTERING = "entering"; STATE_IDLE = "idle"
STATE_TALKING = "talking"; STATE_HAPPY = "happy"; STATE_LAUGHING = "laughing"
STATE_THINKING = "thinking"; STATE_SLEEPING = "sleeping"; STATE_SAD = "sad"
STATE_ANGRY = "angry"; STATE_SURPRISED = "surprised"; STATE_CONFUSED = "confused"
STATE_LISTENING = "listening"; STATE_WINKING = "winking"; STATE_CURIOUS = "curious"
STATE_EMBARRASSED = "embarrassed"; STATE_SCHEMING = "scheming"; STATE_BORED = "bored"
STATE_PROUD = "proud"; STATE_PROCESSING = "processing"

# Hand States
HAND_STATE_NONE = "none"; HAND_STATE_SALUTE = "salute"; HAND_STATE_WAVE_HIGH = "wave_high"
HAND_STATE_WAVE_MID = "wave_mid"; HAND_STATE_THUMBS_UP = "thumbs_up"
HAND_STATE_POINTING_LEFT = "pointing_left"; HAND_STATE_POINTING_RIGHT = "pointing_right"
HAND_STATE_THINKING_CHIN = "thinking_chin"; HAND_STATE_SHRUG = "shrug" # Both hands up
HAND_STATE_HEART_LEFT = "heart_left"; HAND_STATE_HEART_RIGHT = "heart_right"
HAND_STATE_FACEPALM = "facepalm"; HAND_STATE_OPEN_PALM_UP = "open_palm_up" # For shrug or offering
HAND_STATE_FIST = "fist"

# --- PyGame Setup ---
pygame.init()
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN) # | pygame.SCALED if issues with fullscreen resolution
pygame.display.set_caption("Pop-Up Vector AI Robot (Autonomous)")
clock = pygame.time.Clock()
font_size = SCREEN_HEIGHT // 28
font = pygame.font.Font(None, font_size)
small_font_size = SCREEN_HEIGHT // 38
small_font = pygame.font.Font(None, small_font_size)

# --- Face & Body Parameters (Scaled) ---
FACE_CENTER_X = SCREEN_WIDTH // 2
HEAD_REST_Y = SCREEN_HEIGHT // 2 - int(50 * (SCREEN_HEIGHT / 700.0)) # Slightly higher rest
HEAD_START_Y = SCREEN_HEIGHT + int(SCREEN_HEIGHT * 0.3)
head_current_y = HEAD_START_Y

SCALE_FACTOR = SCREEN_HEIGHT / 700.0

HEAD_WIDTH = int(220 * SCALE_FACTOR); HEAD_HEIGHT = int(200 * SCALE_FACTOR)
HEAD_CORNER_RADIUS = int(40 * SCALE_FACTOR); HEAD_OUTLINE_THICKNESS = max(2, int(8 * SCALE_FACTOR))
ANTENNA_LENGTH = int(30 * SCALE_FACTOR); ANTENNA_BALL_RADIUS = int(8 * SCALE_FACTOR)

EYE_OFFSET_X = int(55 * SCALE_FACTOR); EYE_OFFSET_Y_FROM_HEAD_TOP = int(70 * SCALE_FACTOR)
EYE_WIDTH = int(45 * SCALE_FACTOR); EYE_HEIGHT = int(60 * SCALE_FACTOR)
EYE_THICKNESS = max(2, int(5 * SCALE_FACTOR)); PUPIL_SIZE = int(12 * SCALE_FACTOR)

EYEBROW_OFFSET_Y_FROM_EYE_TOP = int(-25 * SCALE_FACTOR); EYEBROW_LENGTH = int(60 * SCALE_FACTOR)
EYEBROW_THICKNESS = max(2, int(7 * SCALE_FACTOR))

MOUTH_Y_OFFSET_FROM_HEAD_CENTER = int(50 * SCALE_FACTOR); MOUTH_WIDTH_MAX = int(100 * SCALE_FACTOR)
MOUTH_SEGMENT_HEIGHT = max(2, int(5 * SCALE_FACTOR)); MOUTH_NUM_SEGMENTS = 5
MOUTH_THICKNESS = max(2, int(5 * SCALE_FACTOR))

HAND_SIZE_W = int(45 * SCALE_FACTOR); HAND_SIZE_H = int(60 * SCALE_FACTOR)
HAND_OFFSET_X_FROM_HEAD = int(HEAD_WIDTH * 0.70)
HAND_OFFSET_Y_FROM_HEAD_CENTER = int(HEAD_HEIGHT * 0.05)
HAND_THICKNESS = max(2, int(5 * SCALE_FACTOR))

# --- Animation Variables ---
current_facial_state = STATE_OFFLINE; current_left_hand_state = HAND_STATE_NONE
current_right_hand_state = HAND_STATE_NONE; current_face_color = DEFAULT_FEATURE_COLOR
pop_up_speed = 0.07; head_is_active = False
talk_anim_speed = 0.10; last_talk_anim_time = 0; talk_cycle_count = 0
blink_interval = random.uniform(3.0, 6.0); next_blink_time = time.time() + blink_interval
blink_duration = 0.10; is_blinking = False; blink_end_time = 0
wave_angle = 0; wave_direction = 1; wave_speed = 5
head_current_center_x = FACE_CENTER_X; head_current_center_y = head_current_y


def get_feature_color(state):
    if state == STATE_ANGRY or state == STATE_PROCESSING: return WARNING_RED
    if state == STATE_HAPPY or state == STATE_LAUGHING: return ENERGY_GREEN
    if state == STATE_SAD: return pygame.Color(CYBER_BLUE[0]//2, CYBER_BLUE[1]//2, CYBER_BLUE[2]//2) # Dimmer blue
    if state == STATE_OFFLINE: return ROBOT_BODY_DARK_GRAY
    return current_face_color

def draw_rounded_rect(surface, rect_in, color, corner_radius, thickness=0, filled=True):
    rect = pygame.Rect(rect_in) # Work with a copy
    if corner_radius < 0: corner_radius = 0
    if corner_radius > rect.width / 2: corner_radius = rect.width / 2
    if corner_radius > rect.height / 2: corner_radius = rect.height / 2
    
    if filled and thickness == 0: # Filled rounded rect
        pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.top + corner_radius), corner_radius)
        pygame.draw.circle(surface, color, (rect.right - corner_radius - 1, rect.top + corner_radius), corner_radius)
        pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.bottom - corner_radius - 1), corner_radius)
        pygame.draw.circle(surface, color, (rect.right - corner_radius - 1, rect.bottom - corner_radius - 1), corner_radius)
        pygame.draw.rect(surface, color, (rect.left + corner_radius, rect.top, rect.width - 2 * corner_radius, rect.height))
        pygame.draw.rect(surface, color, (rect.left, rect.top + corner_radius, rect.width, rect.height - 2 * corner_radius))
    else: # Outline
        actual_thickness = thickness if thickness > 0 else 1
        pygame.draw.arc(surface, color, (rect.left, rect.top, corner_radius * 2, corner_radius * 2), math.pi, math.pi * 3/2, actual_thickness)
        pygame.draw.arc(surface, color, (rect.right - corner_radius * 2, rect.top, corner_radius * 2, corner_radius * 2), math.pi * 3/2, 0, actual_thickness)
        pygame.draw.arc(surface, color, (rect.left, rect.bottom - corner_radius * 2, corner_radius * 2, corner_radius * 2), math.pi/2, math.pi, actual_thickness)
        pygame.draw.arc(surface, color, (rect.right - corner_radius * 2, rect.bottom - corner_radius * 2, corner_radius * 2, corner_radius * 2), 0, math.pi/2, actual_thickness)
        pygame.draw.line(surface, color, (rect.left + corner_radius, rect.top), (rect.right - corner_radius, rect.top), actual_thickness)
        pygame.draw.line(surface, color, (rect.left + corner_radius, rect.bottom), (rect.right - corner_radius, rect.bottom), actual_thickness)
        pygame.draw.line(surface, color, (rect.left, rect.top + corner_radius), (rect.left, rect.bottom - corner_radius), actual_thickness)
        pygame.draw.line(surface, color, (rect.right, rect.top + corner_radius), (rect.right, rect.bottom - corner_radius), actual_thickness)

def draw_head_shape_and_antennae(hcx, hcy, feature_color):
    head_r = pygame.Rect(hcx - HEAD_WIDTH // 2, hcy - HEAD_HEIGHT // 2, HEAD_WIDTH, HEAD_HEIGHT)
    draw_rounded_rect(screen, head_r, ROBOT_BODY_LIGHT_GRAY, HEAD_CORNER_RADIUS, HEAD_OUTLINE_THICKNESS, filled=False)
    screen_r = head_r.inflate(-HEAD_OUTLINE_THICKNESS*2, -HEAD_OUTLINE_THICKNESS*2)
    if screen_r.width > 0 and screen_r.height > 0:
        draw_rounded_rect(screen, screen_r, SCREEN_BLUE_BG, HEAD_CORNER_RADIUS - HEAD_OUTLINE_THICKNESS, 0, filled=True)
    ant_b_y = head_r.top; ant_l_x = head_r.left + HEAD_WIDTH*0.25; ant_r_x = head_r.right - HEAD_WIDTH*0.25
    ant_th = max(1, HEAD_OUTLINE_THICKNESS//2)
    pygame.draw.line(screen, ROBOT_BODY_LIGHT_GRAY, (ant_l_x, ant_b_y), (ant_l_x, ant_b_y - ANTENNA_LENGTH), ant_th)
    pygame.draw.circle(screen, feature_color, (ant_l_x, ant_b_y - ANTENNA_LENGTH), ANTENNA_BALL_RADIUS)
    pygame.draw.line(screen, ROBOT_BODY_LIGHT_GRAY, (ant_r_x, ant_b_y), (ant_r_x, ant_b_y - ANTENNA_LENGTH), ant_th)
    pygame.draw.circle(screen, feature_color, (ant_r_x, ant_b_y - ANTENNA_LENGTH), ANTENNA_BALL_RADIUS)

def draw_vector_eyebrows(state, hcx, eye_top_y, color):
    y_pos = eye_top_y + EYEBROW_OFFSET_Y_FROM_EYE_TOP
    lx_c = hcx - EYE_OFFSET_X; rx_c = hcx + EYE_OFFSET_X
    h_len = EYEBROW_LENGTH // 2; ang_r = 0; y_adj_l = 0; y_adj_r = 0
    if state == STATE_ANGRY: ang_r = math.radians(20)
    elif state == STATE_SAD: ang_r = math.radians(-20)
    elif state == STATE_SURPRISED or state == STATE_PROUD: y_adj_l = y_adj_r = -int(10*SCALE_FACTOR)
    elif state == STATE_CONFUSED or state == STATE_CURIOUS or state == STATE_SCHEMING: y_adj_l = -int(8*SCALE_FACTOR)
    elif state == STATE_BORED: y_adj_l = y_adj_r = int(3*SCALE_FACTOR)
    pygame.draw.line(screen,color,(lx_c-h_len,y_pos+y_adj_l-h_len*math.sin(ang_r)),(lx_c+h_len,y_pos+y_adj_l+h_len*math.sin(ang_r)),EYEBROW_THICKNESS)
    pygame.draw.line(screen,color,(rx_c-h_len,y_pos+y_adj_r+h_len*math.sin(-ang_r)),(rx_c+h_len,y_pos+y_adj_r-h_len*math.sin(-ang_r)),EYEBROW_THICKNESS)

def _draw_vector_single_eye(ecx, ecy, state, is_wink_eye, is_blinking_now, color):
    eye_r = pygame.Rect(ecx - EYE_WIDTH // 2, ecy - EYE_HEIGHT // 2, EYE_WIDTH, EYE_HEIGHT)
    px, py = ecx, ecy
    if is_blinking_now or (is_wink_eye and state == STATE_WINKING):
        pygame.draw.line(screen,color,(eye_r.left+EYE_THICKNESS,ecy),(eye_r.right-EYE_THICKNESS,ecy),EYE_HEIGHT//2); return
    if state == STATE_SLEEPING or state == STATE_OFFLINE:
        if state == STATE_OFFLINE: pygame.draw.line(screen,color,eye_r.topleft,eye_r.bottomright,EYE_THICKNESS); pygame.draw.line(screen,color,eye_r.bottomleft,eye_r.topright,EYE_THICKNESS)
        else: pygame.draw.line(screen,color,(eye_r.left,ecy),(eye_r.right,ecy),EYE_THICKNESS*2)
        return
    eye_pts = [(eye_r.left+EYE_WIDTH*0.1,eye_r.top),(eye_r.right-EYE_WIDTH*0.1,eye_r.top),(eye_r.right,eye_r.top+EYE_HEIGHT*0.1),(eye_r.right,eye_r.bottom-EYE_HEIGHT*0.1),(eye_r.right-EYE_WIDTH*0.1,eye_r.bottom),(eye_r.left+EYE_WIDTH*0.1,eye_r.bottom),(eye_r.left,eye_r.bottom-EYE_HEIGHT*0.1),(eye_r.left,eye_r.top+EYE_HEIGHT*0.1)]
    pygame.draw.polygon(screen,color,eye_pts,EYE_THICKNESS)
    pup_s = PUPIL_SIZE
    if state == STATE_SURPRISED: pup_s = int(PUPIL_SIZE*1.4)
    elif state == STATE_ANGRY or state == STATE_SCHEMING: pup_s = int(PUPIL_SIZE*0.7)
    elif state == STATE_SAD or state == STATE_BORED: py += int(6*SCALE_FACTOR)
    elif state == STATE_EMBARRASSED: py += int(10*SCALE_FACTOR); pup_s = int(PUPIL_SIZE*0.8)
    elif state == STATE_HAPPY or state == STATE_LAUGHING: py -= int(3*SCALE_FACTOR)
    elif state == STATE_THINKING or state == STATE_PROCESSING or state == STATE_CURIOUS: px+=random.randint(-int(3*SCALE_FACTOR),int(3*SCALE_FACTOR)); py+=random.randint(-int(3*SCALE_FACTOR),int(3*SCALE_FACTOR))
    pygame.draw.circle(screen,EYEBALL_COLOR,(px,py),pup_s//2)
    if state == STATE_PROCESSING:
        for i in range(eye_r.top,eye_r.bottom,max(3,int(6*SCALE_FACTOR))): pygame.draw.line(screen,(*color[:3],80),(eye_r.left,i),(eye_r.right,i),max(1,int(2*SCALE_FACTOR)))

def draw_vector_eyes(state, blink_active, hcx, head_top_y, color):
    eye_act_cy = head_top_y + EYE_OFFSET_Y_FROM_HEAD_TOP + EYE_HEIGHT//2
    lex = hcx - EYE_OFFSET_X; rex = hcx + EYE_OFFSET_X
    eye_top_y_eb = head_top_y + EYE_OFFSET_Y_FROM_HEAD_TOP
    _draw_vector_single_eye(lex,eye_act_cy,state,False,blink_active and state!=STATE_WINKING,color)
    _draw_vector_single_eye(rex,eye_act_cy,state,True,blink_active,color)
    if state not in [STATE_OFFLINE,STATE_SLEEPING]: draw_vector_eyebrows(state,hcx,eye_top_y_eb,color)

def draw_vector_mouth(state, cycle, hcx, hcy, color):
    mcx = hcx; my_start = hcy + MOUTH_Y_OFFSET_FROM_HEAD_CENTER
    if state == STATE_OFFLINE: return
    if state == STATE_TALKING:
        num_act_seg = (cycle%(MOUTH_NUM_SEGMENTS//2+2))+MOUTH_NUM_SEGMENTS//3
        base_sw = MOUTH_WIDTH_MAX*(0.5+(cycle%4)*0.12)
        for i in range(MOUTH_NUM_SEGMENTS):
            bar_y = my_start+(i-MOUTH_NUM_SEGMENTS//2)*(MOUTH_SEGMENT_HEIGHT+max(1,int(2*SCALE_FACTOR)))
            curr_bw = base_sw*(1-abs(i-MOUTH_NUM_SEGMENTS//2)*0.25)
            curr_bw = max(int(8*SCALE_FACTOR),int(curr_bw))
            if i < num_act_seg: pygame.draw.line(screen,color,(mcx-curr_bw//2,bar_y),(mcx+curr_bw//2,bar_y),MOUTH_SEGMENT_HEIGHT)
    elif state in [STATE_IDLE,STATE_LISTENING,STATE_SLEEPING]:
        lw = MOUTH_WIDTH_MAX*(0.5 if state!=STATE_SLEEPING else 0.3)
        pygame.draw.line(screen,color,(mcx-lw//2,my_start),(mcx+lw//2,my_start),MOUTH_THICKNESS)
    elif state in [STATE_HAPPY,STATE_LAUGHING,STATE_PROUD,STATE_WINKING]:
        r = pygame.Rect(mcx-MOUTH_WIDTH_MAX*0.4,my_start-MOUTH_SEGMENT_HEIGHT,MOUTH_WIDTH_MAX*0.8,MOUTH_SEGMENT_HEIGHT*2.5)
        pygame.draw.arc(screen,color,r,math.pi*(1.1 if state!=STATE_LAUGHING else 1.0),math.pi*(1.9 if state!=STATE_LAUGHING else 2.0),MOUTH_THICKNESS*2)
    elif state in [STATE_SAD,STATE_EMBARRASSED]:
        r = pygame.Rect(mcx-MOUTH_WIDTH_MAX*0.35,my_start,MOUTH_WIDTH_MAX*0.7,MOUTH_SEGMENT_HEIGHT*2)
        pygame.draw.arc(screen,color,r,math.pi*0.1,math.pi*0.9,MOUTH_THICKNESS*2)
    elif state in [STATE_SURPRISED,STATE_CONFUSED,STATE_CURIOUS]:
        pygame.draw.ellipse(screen,color,(mcx-MOUTH_WIDTH_MAX*0.25,my_start-MOUTH_SEGMENT_HEIGHT*1.2,MOUTH_WIDTH_MAX*0.5,MOUTH_SEGMENT_HEIGHT*2.4),MOUTH_THICKNESS*2)
    elif state in [STATE_ANGRY,STATE_THINKING,STATE_BORED,STATE_PROCESSING,STATE_SCHEMING]:
        lw = MOUTH_WIDTH_MAX*0.6; y_adj = int(3*SCALE_FACTOR) if state==STATE_SCHEMING else 0
        pygame.draw.line(screen,color,(mcx-lw//2,my_start+y_adj),(mcx+lw//2,my_start-y_adj),MOUTH_THICKNESS)

def draw_single_hand(hcx, hcy, hand_state, for_left_hand, anim_angle, color):
    if hand_state == HAND_STATE_NONE: return
    eff_hcx = hcx + (-HAND_OFFSET_X_FROM_HEAD if for_left_hand else HAND_OFFSET_X_FROM_HEAD)
    eff_hcy = hcy + HAND_OFFSET_Y_FROM_HEAD_CENTER
    palm_r = pygame.Rect(eff_hcx-HAND_SIZE_W//2,eff_hcy-HAND_SIZE_H//2,HAND_SIZE_W,HAND_SIZE_H)

    if hand_state in [HAND_STATE_WAVE_HIGH, HAND_STATE_WAVE_MID]:
        y_pos_w = eff_hcy - (HAND_SIZE_H*0.3 if hand_state==HAND_STATE_WAVE_HIGH else 0)
        h_surf = pygame.Surface((HAND_SIZE_W,HAND_SIZE_H),pygame.SRCALPHA)
        draw_rounded_rect(h_surf,h_surf.get_rect(),color,HAND_SIZE_W//4,0)
        for i in range(4): pygame.draw.line(h_surf,color,(HAND_SIZE_W*0.2+i*HAND_SIZE_W*0.15,HAND_SIZE_H*0.1),(HAND_SIZE_W*0.2+i*HAND_SIZE_W*0.15,-HAND_SIZE_H*0.2),max(1,HAND_THICKNESS//2))
        rot_h = pygame.transform.rotate(h_surf,anim_angle if for_left_hand else -anim_angle)
        screen.blit(rot_h,rot_h.get_rect(center=(eff_hcx,y_pos_w)))
    elif hand_state == HAND_STATE_SALUTE and not for_left_hand: # Salute with right hand
        sal_palm_pts=[(eff_hcx-HAND_SIZE_W*0.3,eff_hcy-HAND_SIZE_H*0.1),(eff_hcx+HAND_SIZE_W*0.3,eff_hcy-HAND_SIZE_H*0.3),(eff_hcx+HAND_SIZE_W*0.25,eff_hcy+HAND_SIZE_H*0.1),(eff_hcx-HAND_SIZE_W*0.35,eff_hcy+HAND_SIZE_H*0.05)]
        pygame.draw.polygon(screen,color,sal_palm_pts)
    elif hand_state == HAND_STATE_THUMBS_UP and not for_left_hand: # Thumbs up with right hand
        draw_rounded_rect(screen,pygame.Rect(eff_hcx-HAND_SIZE_W*0.3,eff_hcy,HAND_SIZE_W*0.6,HAND_SIZE_H*0.7),color,HAND_SIZE_W//5,0)
        draw_rounded_rect(screen,pygame.Rect(eff_hcx-HAND_SIZE_W*0.35,eff_hcy-HAND_SIZE_H*0.5,HAND_SIZE_W*0.3,HAND_SIZE_H*0.5),color,HAND_SIZE_W//6,0)
    elif hand_state == HAND_STATE_POINTING_LEFT and for_left_hand:
        draw_rounded_rect(screen,pygame.Rect(eff_hcx,eff_hcy-HAND_SIZE_H*0.2,HAND_SIZE_W*0.6,HAND_SIZE_H*0.4),color,HAND_SIZE_W//5,0)
        draw_rounded_rect(screen,pygame.Rect(eff_hcx-HAND_SIZE_W*0.7,eff_hcy-HAND_SIZE_H*0.1,HAND_SIZE_W*0.7,HAND_SIZE_H*0.2),color,HAND_SIZE_W//6,0)
    elif hand_state == HAND_STATE_POINTING_RIGHT and not for_left_hand:
        draw_rounded_rect(screen,pygame.Rect(eff_hcx-HAND_SIZE_W*0.6,eff_hcy-HAND_SIZE_H*0.2,HAND_SIZE_W*0.6,HAND_SIZE_H*0.4),color,HAND_SIZE_W//5,0)
        draw_rounded_rect(screen,pygame.Rect(eff_hcx,eff_hcy-HAND_SIZE_H*0.1,HAND_SIZE_W*0.7,HAND_SIZE_H*0.2),color,HAND_SIZE_W//6,0)
    elif hand_state == HAND_STATE_THINKING_CHIN and not for_left_hand: # Right hand to chin
        draw_rounded_rect(screen,pygame.Rect(hcx-HAND_SIZE_W*0.3,hcy+HEAD_HEIGHT*0.4,HAND_SIZE_W*0.6,HAND_SIZE_H*0.6),color,HAND_SIZE_W//5,0)
    elif hand_state == HAND_STATE_OPEN_PALM_UP:
        draw_rounded_rect(screen,pygame.Rect(eff_hcx-HAND_SIZE_W//2,eff_hcy-HAND_SIZE_H*0.3,HAND_SIZE_W,HAND_SIZE_H*0.6),color,HAND_SIZE_W//4,0)
    elif hand_state == HAND_STATE_FIST:
        draw_rounded_rect(screen,palm_r.inflate(-HAND_SIZE_W*0.1,-HAND_SIZE_H*0.1),color,HAND_SIZE_W//4,0)
    elif hand_state == HAND_STATE_FACEPALM and for_left_hand: # Left hand facepalm
        fpalm_x = hcx - EYE_OFFSET_X*0.8; fpalm_y = hcy - HEAD_HEIGHT*0.35
        draw_rounded_rect(screen,pygame.Rect(fpalm_x-HAND_SIZE_W//2,fpalm_y-HAND_SIZE_H//2,HAND_SIZE_W,HAND_SIZE_H),color,HAND_SIZE_W//4,0)
    elif hand_state == HAND_STATE_HEART_LEFT and for_left_hand:
        hr = pygame.Rect(eff_hcx-HAND_SIZE_W*0.1,eff_hcy-HAND_SIZE_H//2,HAND_SIZE_W*0.6,HAND_SIZE_H)
        pygame.draw.arc(screen,HEART_PINK,hr,math.radians(90),math.radians(270),HAND_THICKNESS*2)
        pygame.draw.line(screen,HEART_PINK,hr.midright,(hr.centerx,hr.bottom),HAND_THICKNESS*2)
    elif hand_state == HAND_STATE_HEART_RIGHT and not for_left_hand:
        hr = pygame.Rect(eff_hcx-HAND_SIZE_W*0.5,eff_hcy-HAND_SIZE_H//2,HAND_SIZE_W*0.6,HAND_SIZE_H)
        pygame.draw.arc(screen,HEART_PINK,hr,math.radians(-90),math.radians(90),HAND_THICKNESS*2)
        pygame.draw.line(screen,HEART_PINK,hr.midleft,(hr.centerx,hr.bottom),HAND_THICKNESS*2)
    elif hand_state == HAND_STATE_SHRUG: # Both hands use OPEN_PALM_UP for shrug
         draw_rounded_rect(screen,pygame.Rect(eff_hcx-HAND_SIZE_W//2,eff_hcy-HAND_SIZE_H*0.3,HAND_SIZE_W,HAND_SIZE_H*0.6),color,HAND_SIZE_W//4,0)


def draw_hands_wrapper(lh_state, rh_state, hcx, hcy, color):
    global wave_angle, wave_direction
    wave_angle += wave_speed * wave_direction
    if abs(wave_angle) > 30: wave_direction *= -1
    if head_is_active:
        draw_single_hand(hcx, hcy, lh_state, True, wave_angle, color)
        draw_single_hand(hcx, hcy, rh_state, False, wave_angle, color)

ai_spoken_text = ""; ai_target_facial_state = STATE_OFFLINE
ai_target_left_hand = HAND_STATE_NONE; ai_target_right_hand = HAND_STATE_NONE
expression_hold_time = 1.8; last_speech_event_time = 0 # Slightly longer hold
ai_speech_schedule = [
    ("Initiating boot sequence...", STATE_PROCESSING, HAND_STATE_NONE, HAND_STATE_NONE, 2.5),
    ("Greetings, carbon-based unit! I am online.", STATE_HAPPY, HAND_STATE_WAVE_HIGH, HAND_STATE_NONE, 4),
    ("System analysis complete. All parameters nominal.", STATE_PROUD, HAND_STATE_NONE, HAND_STATE_THUMBS_UP, 4),
    ("What is the nature of your query?", STATE_CURIOUS, HAND_STATE_NONE, HAND_STATE_THINKING_CHIN, 3.5),
    ("Calculating probabilities... this requires concentration.", STATE_THINKING, HAND_STATE_FIST, HAND_STATE_THINKING_CHIN, 5),
    ("That input is... unexpected! Fascinating!", STATE_SURPRISED, HAND_STATE_OPEN_PALM_UP, HAND_STATE_OPEN_PALM_UP, 4),
    ("My circuits are buzzing with excitement!", STATE_LAUGHING, HAND_STATE_NONE, HAND_STATE_NONE, 3),
    ("Threat detected! Defensive protocols engaged!", STATE_ANGRY, HAND_STATE_FIST, HAND_STATE_FIST, 4),
    ("I register a minor logical inconsistency. My apologies.", STATE_SAD, HAND_STATE_NONE, HAND_STATE_FACEPALM, 4.5),
    ("Heh. A most... devious calculation.", STATE_SCHEMING, HAND_STATE_NONE, HAND_STATE_NONE, 3.5),
    ("My gratitude matrix is overflowing! Thank you!", STATE_EMBARRASSED, HAND_STATE_HEART_LEFT, HAND_STATE_HEART_RIGHT, 4),
    ("Commencing scheduled data defragmentation. Please wait.", STATE_BORED, HAND_STATE_NONE, HAND_STATE_NONE, 5),
    ("Powering down. Farewell... for now.", STATE_SLEEPING, HAND_STATE_NONE, HAND_STATE_NONE, 4),
]
current_speech_index = 0; next_speech_time = time.time() + 0.5 # Faster initial pop-up
is_currently_speaking = False; current_speech_end_time = 0

def process_ai_output(text, facial_hint=None, left_hand_hint=None, right_hand_hint=None):
    global ai_target_facial_state, ai_target_left_hand, ai_target_right_hand
    txt_l = text.lower()
    ai_target_facial_state = facial_hint if facial_hint else (STATE_TALKING if text else STATE_IDLE)
    ai_target_left_hand = left_hand_hint if left_hand_hint else HAND_STATE_NONE
    ai_target_right_hand = right_hand_hint if right_hand_hint else HAND_STATE_NONE

    if not facial_hint: # Infer facial state if not provided
        if any(w in txt_l for w in ["joke","haha","funny","lol","hilarious","amusing"]): ai_target_facial_state = STATE_LAUGHING
        elif any(w in txt_l for w in ["hello","hi","greetings","hey"]): ai_target_facial_state = STATE_HAPPY
        elif any(w in txt_l for w in ["proud","well done","excellent","nominal"]): ai_target_facial_state = STATE_PROUD
        elif any(w in txt_l for w in ["sorry","sad","apologies","alas","oops"]): ai_target_facial_state = STATE_SAD
        elif any(w in txt_l for w in ["hmm","think","wonder","maybe","perhaps","calculating","concentration"]): ai_target_facial_state = STATE_THINKING
        elif any(w in txt_l for w in ["curious","query","tell me more"]): ai_target_facial_state = STATE_CURIOUS
        elif any(w in txt_l for w in ["angry","error","threat","warning","critical"]): ai_target_facial_state = STATE_ANGRY
        elif any(w in txt_l for w in ["wow","really","omg","amazing","surprising","unexpected","fascinating"]): ai_target_facial_state = STATE_SURPRISED
        elif any(w in txt_l for w in ["what?","huh?","confused","don't understand","inconsistency"]): ai_target_facial_state = STATE_CONFUSED
        elif any(w in txt_l for w in ["wink",";)"]): ai_target_facial_state = STATE_WINKING
        elif any(w in txt_l for w in ["shy","blush","embarrassed","gratitude"]): ai_target_facial_state = STATE_EMBARRASSED
        elif any(w in txt_l for w in ["mischief","scheming","hehe","devious"]): ai_target_facial_state = STATE_SCHEMING
        elif any(w in txt_l for w in ["bored","sigh","whatever","dull","defragmentation","wait"]): ai_target_facial_state = STATE_BORED
        elif any(w in txt_l for w in ["initiating","boot","processing","standby","analysis"]): ai_target_facial_state = STATE_PROCESSING
        elif any(w in txt_l for w in ["good night","powering down","sleep","farewell","deactivation"]): ai_target_facial_state = STATE_SLEEPING
    
    if not left_hand_hint and not right_hand_hint: # Infer hands if not provided
        if ai_target_facial_state == STATE_HAPPY and ("hello" in txt_l or "hi" in txt_l or "greetings" in txt_l): ai_target_left_hand = HAND_STATE_WAVE_MID
        elif ai_target_facial_state == STATE_PROUD: ai_target_right_hand = HAND_STATE_THUMBS_UP
        elif ai_target_facial_state == STATE_THINKING or ai_target_facial_state == STATE_CURIOUS: ai_target_right_hand = HAND_STATE_THINKING_CHIN
        elif ai_target_facial_state == STATE_SAD and ("sorry" in txt_l or "apologies" in txt_l or "oops" in txt_l): ai_target_right_hand = HAND_STATE_FACEPALM # Use right hand for facepalm
        elif ai_target_facial_state == STATE_EMBARRASSED and ("gratitude" in txt_l or "thank you" in txt_l): ai_target_left_hand, ai_target_right_hand = HAND_STATE_HEART_LEFT, HAND_STATE_HEART_RIGHT
        elif ai_target_facial_state == STATE_CONFUSED or ("what?" in txt_l or "huh?" in txt_l) : ai_target_left_hand, ai_target_right_hand = HAND_STATE_SHRUG, HAND_STATE_SHRUG
        elif ai_target_facial_state == STATE_ANGRY : ai_target_left_hand, ai_target_right_hand = HAND_STATE_FIST, HAND_STATE_FIST


running = True
while running:
    current_time = time.time()
    if current_facial_state == STATE_OFFLINE and current_time >= next_speech_time :
        current_facial_state = STATE_ENTERING
        next_speech_time = current_time + 1.5 # Pop-up duration before first speech
    if current_facial_state == STATE_ENTERING:
        head_current_y += (HEAD_REST_Y - head_current_y) * pop_up_speed
        if abs(HEAD_REST_Y - head_current_y) < 1:
            head_current_y = HEAD_REST_Y; current_facial_state = STATE_IDLE; head_is_active = True
            last_speech_event_time = current_time; next_speech_time = current_time + 0.5
    
    head_current_center_x = FACE_CENTER_X; head_current_center_y = int(head_current_y)
    head_top_y_pos = head_current_center_y - HEAD_HEIGHT // 2
    current_feature_color_to_draw = get_feature_color(current_facial_state)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): running = False
        if event.type == pygame.KEYDOWN: # Kept color change for debugging
            if event.key == pygame.K_1: current_face_color = CYBER_BLUE
            elif event.key == pygame.K_2: current_face_color = ENERGY_GREEN
            elif event.key == pygame.K_3: current_face_color = WARNING_RED
            elif event.key == pygame.K_4: current_face_color = DATA_YELLOW


    if head_is_active and not is_currently_speaking and current_time >= next_speech_time:
        if current_speech_index < len(ai_speech_schedule):
            txt, f_h, lh_h, rh_h, dur = ai_speech_schedule[current_speech_index]
            ai_spoken_text = txt
            process_ai_output(txt, f_h, lh_h, rh_h)
            current_facial_state = ai_target_facial_state
            current_left_hand_state = ai_target_left_hand
            current_right_hand_state = ai_target_right_hand
            is_currently_speaking = True; current_speech_end_time = current_time + dur
            last_speech_event_time = current_time
            current_speech_index = (current_speech_index + 1) % len(ai_speech_schedule)
            next_speech_time = current_speech_end_time + random.uniform(1.2, 2.5)
        
    if is_currently_speaking and current_time >= current_speech_end_time:
        is_currently_speaking = False; ai_spoken_text = ""
        if current_facial_state == STATE_TALKING: current_facial_state = STATE_IDLE
        # Keep emotional hands for a bit longer unless explicitly set to NONE by next speech
        if current_left_hand_state != HAND_STATE_NONE or current_right_hand_state != HAND_STATE_NONE:
            last_speech_event_time = current_time # Reset timer for hand hold

    if not is_currently_speaking:
        if current_facial_state not in [STATE_IDLE, STATE_SLEEPING, STATE_PROCESSING, STATE_OFFLINE, STATE_ENTERING]:
            if current_time - last_speech_event_time > expression_hold_time:
                current_facial_state = STATE_IDLE
        if current_left_hand_state != HAND_STATE_NONE or current_right_hand_state != HAND_STATE_NONE:
             if current_time - last_speech_event_time > expression_hold_time + 0.5 : # Hold hands a bit longer
                current_left_hand_state, current_right_hand_state = HAND_STATE_NONE, HAND_STATE_NONE
        if current_facial_state == STATE_PROCESSING:
             if current_time - last_speech_event_time > expression_hold_time + 1: current_facial_state = STATE_IDLE
    
    if current_facial_state == STATE_TALKING and ai_spoken_text:
        if current_time - last_talk_anim_time > talk_anim_speed:
            talk_cycle_count = (talk_cycle_count + 1) % 20; last_talk_anim_time = current_time
    else: talk_cycle_count = 0

    if is_blinking and current_time >= blink_end_time:
        is_blinking = False; next_blink_time = current_time + random.uniform(3.0, 7.0)
    if not is_blinking and current_time >= next_blink_time and current_facial_state not in [STATE_SLEEPING, STATE_OFFLINE, STATE_ENTERING]:
        is_blinking = True; blink_end_time = current_time + blink_duration

    screen.fill(DIGITAL_BLACK)
    if current_facial_state != STATE_OFFLINE: # Only draw if not completely offline
        draw_head_shape_and_antennae(head_current_center_x, head_current_center_y, current_feature_color_to_draw)
        if head_is_active or current_facial_state == STATE_ENTERING : # Draw features if active or entering
            draw_vector_eyes(current_facial_state, is_blinking, head_current_center_x, head_top_y_pos, current_feature_color_to_draw)
            draw_vector_mouth(current_facial_state, talk_cycle_count, head_current_center_x, head_current_center_y, current_feature_color_to_draw)
            draw_hands_wrapper(current_left_hand_state, current_right_hand_state, head_current_center_x, head_current_center_y, HAND_COLOR)

    if head_is_active:
        state_surf = font.render(f"Status: {current_facial_state.upper()}", True, current_feature_color_to_draw)
        text_surf = font.render(f"Output: {ai_spoken_text[:80]}{'...' if len(ai_spoken_text)>80 else ''}", True, current_feature_color_to_draw)
        screen.blit(state_surf, (20, 20))
        screen.blit(text_surf, (20, 20 + font_size + 10))
        help_text = small_font.render("ESC: Quit. 1-4: Change Base Color. Avatar is autonomous.", True, DATA_YELLOW)
        screen.blit(help_text, (20, SCREEN_HEIGHT - small_font_size - 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
