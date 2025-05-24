Updated codes………..
# src/gui_face.py
import pygame
import threading
import math
import time
import random
from src.config import IS_FULLSCREEN, SCREEN_WIDTH_WINDOWED, SCREEN_HEIGHT_WINDOWED

class RobotFaceGUI:
    def __init__(self):
        pygame.init()
        if IS_FULLSCREEN:
            info = pygame.display.Info()
            self.WIDTH, self.HEIGHT = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        else:
            self.WIDTH, self.HEIGHT = SCREEN_WIDTH_WINDOWED, SCREEN_HEIGHT_WINDOWED
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        pygame.display.set_caption("Loki – Your Expressive Assistant")
        
        try:
            self.font = pygame.font.SysFont("SF Pro Display", 36, bold=True)
        except:
            self.font = pygame.font.SysFont("Arial", 32, bold=True)

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREY = (40, 40, 40)
        self.ROBO_ACCENT_COLOR = (70, 150, 255)
        self.LOVELY_PUPIL_COLOR = (255, 105, 180)
        self.ANGRY_PUPIL_COLOR = (255, 50, 50)
        self.BLUSH_COLOR_BASE = (255, 182, 193)

        self.FACE_CENTER_X = self.WIDTH // 2
        self.FACE_CENTER_Y = self.HEIGHT // 2
        self.EYE_Y_OFFSET = 90
        self.EYE_SPACING = 130
        self.EYE_WIDTH = 60
        self.EYE_HEIGHT = 100
        self.PUPIL_RADIUS_NORMAL = 12
        self.PUPIL_Y_IN_EYE_OFFSET = 15
        self.MOUTH_Y_OFFSET = 100
        self.MOUTH_BASE_WIDTH = 160
        self.MOUTH_BASE_HEIGHT = 70

        self.current_expression = "neutral"
        self.message = "Initializing..."
        self.expression_lock = threading.Lock()

        self.animation_state = {
            "last_blink_time": 0,
            "blink_interval": 3000,
            "blink_duration": 150,
            "is_blinking": False,
            "talking_mouth_frame_start_time": 0,
            "talking_mouth_frame_interval": 80,  # ms per frame (FASTER)
            "current_talking_mouth_frame": 0,
            "num_talking_mouth_frames": 5, # INCREASED number of frames
            "talking_eye_squeeze_factor": 1.0,
            "talking_eye_squeeze_phase": 0,
            "blush_alpha": 0,
            "blush_target_alpha": 0,
            "pupil_offset_x": 0,
            "pupil_offset_y_extra": 0,
        }
        self.animation_lock = threading.Lock()
        
        self.running = True
        self.clock = pygame.time.Clock()

    def _draw_stylized_eye(self, surface, center_x, center_y, width, height, pupil_radius, expression, is_blinking_now, pupil_offset_x_anim, pupil_offset_y_extra_anim, eye_squeeze_factor_anim):
        current_eye_height = int(height * eye_squeeze_factor_anim)
        eye_outer_rect = pygame.Rect(center_x - width // 2, center_y - current_eye_height // 2, width, current_eye_height)
        pygame.draw.rect(surface, self.WHITE, eye_outer_rect, border_radius=int(width*0.3))

        if is_blinking_now:
            lid_rect = pygame.Rect(eye_outer_rect.left, center_y - 10, eye_outer_rect.width, 20)
            pygame.draw.rect(surface, self.BLACK, lid_rect, border_radius=int(width*0.3))
            pygame.draw.line(surface, self.WHITE, (eye_outer_rect.left + 5, center_y), (eye_outer_rect.right - 5, center_y), 3)
            return

        pupil_base_x = center_x + pupil_offset_x_anim
        pupil_base_y = center_y + self.PUPIL_Y_IN_EYE_OFFSET * eye_squeeze_factor_anim + pupil_offset_y_extra_anim
        current_pupil_radius = pupil_radius

        if expression == "talking":
             current_pupil_radius *= (1.1 + 0.2 * math.sin(self.animation_state["talking_eye_squeeze_phase"]))

        if expression == "happy" or expression == "smiling":
            current_pupil_radius *= 1.3
            pygame.draw.circle(surface, self.ROBO_ACCENT_COLOR, (pupil_base_x, pupil_base_y - 5), current_pupil_radius)
        elif expression == "laughing":
            current_pupil_radius *= 1.2
            pygame.draw.arc(surface, self.BLACK, [pupil_base_x - current_pupil_radius, pupil_base_y - current_pupil_radius*1.5 - 5, current_pupil_radius*2, current_pupil_radius*2], math.pi * 1.2, math.pi * 1.8, 3)
            pygame.draw.circle(surface, self.ROBO_ACCENT_COLOR, (pupil_base_x, pupil_base_y + 5), current_pupil_radius)
        elif expression == "lovely":
            current_pupil_radius *= 1.6
            pygame.draw.circle(surface, self.LOVELY_PUPIL_COLOR, (pupil_base_x, pupil_base_y), current_pupil_radius)
            pygame.draw.circle(surface, self.WHITE, (pupil_base_x+5, pupil_base_y-5), current_pupil_radius*0.3)
        elif expression == "angry":
            pygame.draw.polygon(surface, self.BLACK, [
                (eye_outer_rect.left + 5, eye_outer_rect.top + 25 * eye_squeeze_factor_anim),
                (eye_outer_rect.right - 5, eye_outer_rect.top + 10 * eye_squeeze_factor_anim),
                (eye_outer_rect.right - 5, eye_outer_rect.top + 20 * eye_squeeze_factor_anim),
                (eye_outer_rect.left + 5, eye_outer_rect.top + 35 * eye_squeeze_factor_anim)
            ])
            pygame.draw.circle(surface, self.ANGRY_PUPIL_COLOR, (pupil_base_x, pupil_base_y + 5), current_pupil_radius * 0.8)
        elif expression == "sleepy":
            lid_rect = pygame.Rect(eye_outer_rect.left, eye_outer_rect.top, eye_outer_rect.width, eye_outer_rect.height * 0.6)
            pygame.draw.rect(surface, self.BLACK, lid_rect, border_top_left_radius=int(width*0.3), border_top_right_radius=int(width*0.3))
            pygame.draw.line(surface, self.WHITE, (eye_outer_rect.left+5, eye_outer_rect.top + eye_outer_rect.height*0.6 - 2), (eye_outer_rect.right-5, eye_outer_rect.top + eye_outer_rect.height*0.6 - 2), 3)
        elif expression == "shying":
            pygame.draw.circle(surface, self.ROBO_ACCENT_COLOR, (pupil_base_x, pupil_base_y + 10), current_pupil_radius * 0.9)
        elif expression == "thinking" or expression == "processing" or expression == "listening":
            pygame.draw.circle(surface, self.ROBO_ACCENT_COLOR, (pupil_base_x, pupil_base_y - 10), current_pupil_radius)
        else: 
            pygame.draw.circle(surface, self.ROBO_ACCENT_COLOR, (pupil_base_x, pupil_base_y), current_pupil_radius)

    def _draw_animated_mouth(self, surface, center_x, center_y, base_width, base_height, expression, talking_frame_idx):
        mouth_rect_center_y = center_y + base_height * 0.2

        if expression == "talking": # Laughing while talking
            frame = talking_frame_idx
            laugh_width_factor = 0.7 + 0.1 * math.sin(frame * math.pi / 2) # Dynamic width
            laugh_height_factor = 0.5 + 0.2 * math.sin(frame * math.pi)   # Dynamic height, more up/down

            current_mouth_width = base_width * laugh_width_factor
            current_mouth_height = base_height * laugh_height_factor

            # D-shape mouth, animated
            mouth_rect = pygame.Rect(
                center_x - current_mouth_width // 2,
                mouth_rect_center_y - current_mouth_height // 2,
                current_mouth_width,
                current_mouth_height
            )
            pygame.draw.ellipse(surface, self.WHITE, mouth_rect)
            # Cut off top to make D-shape (adjust if mouth_rect_center_y is true center)
            pygame.draw.rect(surface, self.BLACK, 
                             (mouth_rect.x, mouth_rect.y, 
                              mouth_rect.width, mouth_rect.height / 2 + 2)) # +2 to ensure full cutoff
            # Line across the D
            pygame.draw.line(surface, self.WHITE, 
                             (mouth_rect.left, mouth_rect.centery), 
                             (mouth_rect.right, mouth_rect.centery), 5)

        elif expression == "happy" or expression == "smiling":
            # ... (existing happy/smiling mouth) ...
            smile_rect = [center_x - base_width*0.35, mouth_rect_center_y - base_height*0.1, base_width*0.7, base_height*0.5]
            pygame.draw.arc(surface, self.WHITE, smile_rect, math.pi, 2 * math.pi, 7)
        elif expression == "laughing": # Standalone laughing
            laugh_width = base_width * 0.8; laugh_height = base_height * 0.6
            laugh_rect = pygame.Rect(center_x - laugh_width // 2, mouth_rect_center_y - laugh_height // 2, laugh_width, laugh_height)
            pygame.draw.ellipse(surface, self.WHITE, laugh_rect)
            pygame.draw.rect(surface, self.BLACK, (laugh_rect.x, laugh_rect.y, laugh_rect.width, laugh_rect.height / 2)) 
            pygame.draw.line(surface, self.WHITE, (laugh_rect.left, laugh_rect.centery), (laugh_rect.right, laugh_rect.centery), 5)
        # ... (other expressions) ...
        elif expression == "angry":
            frown_rect = [center_x - base_width*0.3, mouth_rect_center_y + base_height*0.05, base_width*0.6, base_height*0.4]
            pygame.draw.arc(surface, self.WHITE, frown_rect, 0, math.pi, 7)
        elif expression == "lovely":
            pygame.draw.ellipse(surface, self.WHITE, (center_x - 20, mouth_rect_center_y, 40, 25))
        elif expression == "talking":
            frame = talking_frame_idx # This is self.animation_state["current_talking_mouth_frame"]
            if frame == 0: # Closed / slight line
                pygame.draw.line(surface, self.WHITE, (center_x - base_width*0.25, mouth_rect_center_y + 10), (center_x + base_width*0.25, mouth_rect_center_y + 10), 5)
            elif frame == 1: # Small 'o'
                pygame.draw.ellipse(surface, self.WHITE, (center_x - base_width*0.15, mouth_rect_center_y + 5, base_width*0.3, base_height*0.25))
            elif frame == 2: # Medium open
                pygame.draw.ellipse(surface, self.WHITE, (center_x - base_width*0.3, mouth_rect_center_y, base_width*0.6, base_height*0.4))
            elif frame == 3: # Wider open, slightly taller
                pygame.draw.ellipse(surface, self.WHITE, (center_x - base_width*0.35, mouth_rect_center_y - 7, base_width*0.7, base_height*0.55))
            elif frame == 4: # Medium 'o' (like 'oo' sound)
                pygame.draw.ellipse(surface, self.WHITE, (center_x - base_width*0.25, mouth_rect_center_y - 2, base_width*0.5, base_height*0.45))
        elif expression == "sleepy" or expression == "neutral":
            pygame.draw.line(surface, self.WHITE, (center_x - base_width*0.2, mouth_rect_center_y + 10), (center_x + base_width*0.2, mouth_rect_center_y + 10), 5)
        elif expression == "thinking" or expression == "processing":
            points = [
                (center_x - base_width*0.2, mouth_rect_center_y + 10), (center_x - base_width*0.05, mouth_rect_center_y + 5),
                (center_x + base_width*0.05, mouth_rect_center_y + 5), (center_x + base_width*0.2, mouth_rect_center_y + 10),
            ]
            pygame.draw.lines(surface, self.WHITE, False, points, 5)
        elif expression == "shying":
            shy_smile_rect = [center_x - base_width*0.15, mouth_rect_center_y, base_width*0.3, base_height*0.25]
            pygame.draw.arc(surface, self.WHITE, shy_smile_rect, math.pi, 2 * math.pi, 5)
        elif expression == "listening":
            pygame.draw.line(surface, self.WHITE, (center_x - base_width*0.15, mouth_rect_center_y + 8), (center_x + base_width*0.15, mouth_rect_center_y + 8), 4)

    def _draw_blush_effect(self, surface, center_x, eye_y, current_alpha):
        if current_alpha <= 0: return
        blush_radius_x = 60; blush_radius_y = 30
        blush_y_pos = eye_y + self.EYE_HEIGHT // 2 + 30 
        cheek_x_offset = self.EYE_SPACING + self.EYE_WIDTH // 2 - 10
        blush_surf = pygame.Surface((blush_radius_x * 2, blush_radius_y * 2), pygame.SRCALPHA)
        blush_color = (self.BLUSH_COLOR_BASE[0], self.BLUSH_COLOR_BASE[1], self.BLUSH_COLOR_BASE[2], int(current_alpha))
        pygame.draw.ellipse(blush_surf, blush_color, (0, 0, blush_radius_x, blush_radius_y))
        left_cheek_pos = (center_x - cheek_x_offset - blush_radius_x, blush_y_pos - blush_radius_y / 2)
        right_cheek_pos = (center_x + cheek_x_offset, blush_y_pos - blush_radius_y / 2) # Adjusted for single ellipse on surf
        surface.blit(blush_surf, left_cheek_pos)
        surface.blit(blush_surf, right_cheek_pos) # Blit same surf again for right side

    def _update_animations_and_state(self, current_time_ticks, current_expr_locked):
        with self.animation_lock:
            if not self.animation_state["is_blinking"] and \
               current_time_ticks - self.animation_state["last_blink_time"] > self.animation_state["blink_interval"]:
                self.animation_state["is_blinking"] = True
                self.animation_state["last_blink_time"] = current_time_ticks
            if self.animation_state["is_blinking"] and \
               current_time_ticks - self.animation_state["last_blink_time"] > self.animation_state["blink_duration"]:
                self.animation_state["is_blinking"] = False
                self.animation_state["last_blink_time"] = current_time_ticks
                self.animation_state["blink_interval"] = random.randint(2000, 7000)

            if current_expr_locked == "talking":
                if current_time_ticks - self.animation_state["talking_mouth_frame_start_time"] > self.animation_state["talking_mouth_frame_interval"]:
                    self.animation_state["current_talking_mouth_frame"] = (self.animation_state["current_talking_mouth_frame"] + 1) % self.animation_state["num_talking_mouth_frames"]
                    self.animation_state["talking_mouth_frame_start_time"] = current_time_ticks
                self.animation_state["talking_eye_squeeze_phase"] += 0.2 
                self.animation_state["talking_eye_squeeze_factor"] = 1.0 - 0.05 * abs(math.sin(self.animation_state["talking_eye_squeeze_phase"]))
            else:
                self.animation_state["talking_eye_squeeze_factor"] = 1.0

            should_blush = current_expr_locked in ["shying", "lovely"]
            self.animation_state["blush_target_alpha"] = 200 if should_blush else 0
            if self.animation_state["blush_alpha"] != self.animation_state["blush_target_alpha"]:
                if self.animation_state["blush_alpha"] < self.animation_state["blush_target_alpha"]:
                    self.animation_state["blush_alpha"] = min(self.animation_state["blush_target_alpha"], self.animation_state["blush_alpha"] + 15)
                else:
                    self.animation_state["blush_alpha"] = max(self.animation_state["blush_target_alpha"], self.animation_state["blush_alpha"] - 15)

            if current_expr_locked == "thinking" or current_expr_locked == "processing":
                self.animation_state["pupil_offset_x"] = -15; self.animation_state["pupil_offset_y_extra"] = -10
            elif current_expr_locked == "shying":
                self.animation_state["pupil_offset_x"] = 0; self.animation_state["pupil_offset_y_extra"] = 15
            elif current_expr_locked == "listening":
                self.animation_state["pupil_offset_x"] = 0; self.animation_state["pupil_offset_y_extra"] = -5
            else: 
                self.animation_state["pupil_offset_x"] = 0; self.animation_state["pupil_offset_y_extra"] = 0
        
        with self.animation_lock: # Return copies
            return ( self.animation_state["is_blinking"], self.animation_state["current_talking_mouth_frame"],
                     self.animation_state["blush_alpha"], self.animation_state["pupil_offset_x"],
                     self.animation_state["pupil_offset_y_extra"], self.animation_state["talking_eye_squeeze_factor"] )

    def _draw_scene(self):
        with self.expression_lock:
            expr_to_draw = self.current_expression; msg_to_display = self.message
        current_time = pygame.time.get_ticks()
        is_blinking_val, talking_frame_idx_val, blush_alpha_val, \
        pupil_offset_x_val, pupil_offset_y_extra_val, eye_squeeze_val = \
            self._update_animations_and_state(current_time, expr_to_draw)

        self.screen.fill(self.BLACK)
        eye_actual_y = self.FACE_CENTER_Y - self.EYE_Y_OFFSET
        left_eye_x = self.FACE_CENTER_X - self.EYE_SPACING
        right_eye_x = self.FACE_CENTER_X + self.EYE_SPACING
        self._draw_stylized_eye(self.screen, left_eye_x, eye_actual_y, self.EYE_WIDTH, self.EYE_HEIGHT, self.PUPIL_RADIUS_NORMAL, expr_to_draw, is_blinking_val, pupil_offset_x_val, pupil_offset_y_extra_val, eye_squeeze_val)
        self._draw_stylized_eye(self.screen, right_eye_x, eye_actual_y, self.EYE_WIDTH, self.EYE_HEIGHT, self.PUPIL_RADIUS_NORMAL, expr_to_draw, is_blinking_val, pupil_offset_x_val, pupil_offset_y_extra_val, eye_squeeze_val)
        mouth_actual_y = self.FACE_CENTER_Y + self.MOUTH_Y_OFFSET
        self._draw_animated_mouth(self.screen, self.FACE_CENTER_X, mouth_actual_y, self.MOUTH_BASE_WIDTH, self.MOUTH_BASE_HEIGHT, expr_to_draw, talking_frame_idx_val)
        self._draw_blush_effect(self.screen, self.FACE_CENTER_X, eye_actual_y, blush_alpha_val)

        if msg_to_display:
            text_surface = self.font.render(msg_to_display, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 70))
            self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def set_expression(self, expression: str, message: str = ""):
        with self.expression_lock:
            self.current_expression = expression
            if message: self.message = message
            elif expression == "neutral": self.message = "Hi! I'm Loki."

    def run(self):
        self.set_expression("neutral", "Hi! I'm Loki. How can I help?")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    # You can add manual test keys here if needed
            self._draw_scene()
            self.clock.tick(30)
        pygame.quit()

# if __name__ == '__main__':
#     # For testing gui_face.py independently with the stubbed VoiceAI
#     from voice_ai_stub import VoiceAIStubbed # Assuming you save the stub as voice_ai_stub.py
#     face_gui = RobotFaceGUI()
#     voice_stub = VoiceAIStubbed(face_gui) # Create instance of the stub
#     test_thread = threading.Thread(target=voice_stub.run_assistant_loop, daemon=True)
#     test_thread.start()
#     face_gui.run()
………………………….gui_face.py
# main.py
import threading
from src.gui_face import RobotFaceGUI
from src.voice_ai import VoiceAI # We'll use the STUBBED version below

def main():
    print("Starting Loki AI Assistant (Animation Test Mode)...")

    robot_face = RobotFaceGUI()
    voice_assistant = VoiceAI(robot_face_gui=robot_face) # Pass GUI to STUBBED VoiceAI

    voice_thread = threading.Thread(target=voice_assistant.run_assistant_loop, daemon=True)
    voice_thread.start()

    robot_face.run() # This runs the Pygame loop

    print("Loki AI Assistant (Animation Test Mode) is shutting down.")

if __name__ == "__main__":
    main()


…………………..main.py
# src/voice_ai.py
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from src.config import GENAI_API_KEY
import time

# --- Microphone Preference ---
# Set this to the EXACT name of the microphone you want to try from your list,
# or set to None to let the script try to find a suitable one.
# Examples from your list:
# MIC_NAME_PREFERENCE = "Microphone (Realtek(R) Audio)" # (This is a good one to try, corresponds to Index 1, 5, 9)
# MIC_NAME_PREFERENCE = "Microphone Array (Realtek HD Audio Mic input)" # (This one had issues previously)
MIC_NAME_PREFERENCE = "Microphone (Realtek(R) Audio)" # <<< TRY THIS or another specific one from your list
# MIC_NAME_PREFERENCE = None # To let it auto-detect

# Configure Gemini AI
genai.configure(api_key=GENAI_API_KEY)
try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    print("GenAI Model Initialized.")
except Exception as e:
    print(f"ERROR: Could not initialize GenAI model: {e}")
    model = None

# Initialize text-to-speech engine
engine = pyttsx3.init()
if engine:
    engine.setProperty("rate", 170)
    print("TTS Engine Initialized.")
else:
    print("ERROR: pyttsx3 engine could not be initialized. Loki won't speak audibly.")

def get_mic_index(mic_name_preference=None):
    mic_list = sr.Microphone.list_microphone_names()
    if not mic_list:
        print("ERROR: No microphones found by SpeechRecognition.")
        return None

    print("\n--- Available Microphones ---")
    for i, name in enumerate(mic_list):
        print(f"  Index {i}: {name}")
    print("-----------------------------")

    if mic_name_preference:
        # Try exact match first
        for i, name in enumerate(mic_list):
            if mic_name_preference.lower() == name.lower().strip(): # Exact match, strip whitespace
                print(f"Found PREFERRED microphone (exact match): '{name}' at index {i}")
                return i
        # Try partial match
        for i, name in enumerate(mic_list):
            if mic_name_preference.lower() in name.lower(): # Partial match
                print(f"Found PREFERRED microphone (partial match): '{name}' at index {i}")
                return i
        print(f"Warning: Preferred microphone '{mic_name_preference}' not found by exact or partial match. Searching for alternatives.")
    
    # Common terms to search for if no preference or preference not found
    common_mic_terms = ["microphone array", "usb audio", "default", "realtek audio input", "internal microphone"]
    # Prioritize non-"array" Realtek if "Realtek(R) Audio" was not the preference already chosen
    if not (mic_name_preference and "realtek(r) audio" in mic_name_preference.lower()):
        for i, name in enumerate(mic_list):
            if "realtek(r) audio" in name.lower() and "array" not in name.lower():
                print(f"Found suitable microphone (common term 'Realtek(R) Audio'): '{name}' at index {i}")
                return i
                
    for term in common_mic_terms:
        for i, name in enumerate(mic_list):
            if term in name.lower():
                print(f"Found suitable microphone (common term '{term}'): '{name}' at index {i}")
                return i
    
    # Fallback: Use the first non-"mapper" microphone if possible
    for i, name in enumerate(mic_list):
        if "mapper" not in name.lower(): # Avoid "Microsoft Sound Mapper" as primary
             print(f"Warning: Using first non-mapper microphone as fallback: '{name}' at index {i}")
             return i

    # Very last resort: use the first one if all else fails
    if mic_list:
        print(f"CRITICAL WARNING: Using the very first microphone as last resort: '{mic_list[0]}' at index 0. This may not be correct.")
        return 0
    
    return None

class VoiceAI:
    def __init__(self, robot_face_gui):
        self.gui = robot_face_gui
        self.recognizer = sr.Recognizer()
        self.mic_index = get_mic_index(MIC_NAME_PREFERENCE)
        self.mic_initialized_successfully = False

        if self.mic_index is None:
            error_msg = "No microphone could be selected!"
            print(f"❌ {error_msg}")
            self.gui.set_expression("sad", error_msg)
            if engine: self.speak_tts_only(error_msg)
            return

        mic_name_to_try = sr.Microphone.list_microphone_names()[self.mic_index]
        print(f"Attempting to use microphone: '{mic_name_to_try}' (Index: {self.mic_index})")
        self.gui.set_expression("neutral", "Initializing Mic...")
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                print("Calibrating microphone... Please be quiet for a moment.")
                self.gui.set_expression("neutral", "Calibrating mic...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                print("Calibration complete.")
                self.gui.set_expression("neutral", "Mic calibrated!")
                self.mic_initialized_successfully = True
        except Exception as e:
            error_msg = f"Mic Init Error ({mic_name_to_try}): {e}"
            print(f"❌ {error_msg}")
            print("   Listening might be impaired or non-functional. Using default energy threshold.")
            self.gui.set_expression("sad", "Mic Problem!")
            if engine: self.speak_tts_only(f"I'm having trouble with my microphone: {str(e)[:50]}")
            self.recognizer.energy_threshold = 3000 
            self.mic_initialized_successfully = True 

        if self.mic_initialized_successfully:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8 
            print("Microphone setup complete (or attempted with fallback).")
        else:
            print("CRITICAL: Microphone did not initialize. Voice input will likely fail.")

    def speak_tts_only(self, text:str):
        if engine and text:
            print(f"🔊 TTS Alert: {text}")
            engine.say(text)
            engine.runAndWait()

    def speak(self, text: str, expression_after_speak="neutral"):
        if not engine:
            print(f"TTS Engine not available. Cannot speak: {text}")
            short_display_text = f"Loki (no TTS): {text[:30]}{'...' if len(text) > 30 else ''}"
            self.gui.set_expression("talking", short_display_text)
            time.sleep(min(3.0, len(text)/10.0)) 
            self.gui.set_expression(expression_after_speak)
            return

        if not text: return

        short_display_text = f"Loki: {text[:35]}{'...' if len(text) > 35 else ''}"
        self.gui.set_expression("talking", short_display_text)
        
        print(f"🤖 Loki says: {text}")
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            error_msg = f"TTS Error: {e}"
            print(f"❌ {error_msg}")
            self.gui.set_expression("sad", "TTS Problem!")
            time.sleep(2)
        
        self.gui.set_expression(expression_after_speak)

    def listen(self, timeout=7, phrase_time_limit=10):
        if not self.mic_initialized_successfully or self.mic_index is None:
            self.gui.set_expression("sad", "Mic Unavailable")
            time.sleep(1)
            return None

        mic_name_in_use = sr.Microphone.list_microphone_names()[self.mic_index]
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                self.gui.set_expression("listening", "Listening...")
                print(f"🎤 Listening via '{mic_name_in_use}'...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("No speech detected in time.")
            self.gui.set_expression("neutral", "Didn't hear you.")
            return None
        except Exception as e:
            error_msg = f"Listen Error ({mic_name_in_use}): {e}"
            print(f"❌ {error_msg}")
            self.gui.set_expression("sad", "Listen Problem!")
            time.sleep(1)
            return None

        self.gui.set_expression("processing", "Thinking...")
        try:
            query = self.recognizer.recognize_google(audio)
            print(f"🗣️ You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            self.speak("Sorry, I didn't quite catch that.", "neutral")
            return None
        except sr.RequestError as e:
            error_msg = f"Speech Service Error: {e}"
            print(f"❌ {error_msg}")
            self.speak("My connection to the speech service failed. Check internet.", "sad")
            return None
        except Exception as e:
            error_msg = f"Speech Process Error: {e}"
            print(f"❌ {error_msg}")
            self.speak("An unexpected error occurred while processing speech.", "sad")
            return None

    def get_gemini_response(self, question: str):
        if not model:
            return "My AI brain (GenAI) is not available right now."
        if not question:
            return "What was the question?"
            
        self.gui.set_expression("thinking", "Consulting GenAI...")
        print(f"🧠 Querying GenAI with: \"{question}\"")
        try:
            response = model.generate_content(question)
            ai_text = response.text
            if not ai_text or ai_text.isspace():
                return "I received an empty response from the AI."
            return ai_text
        except Exception as e:
            error_msg = f"GenAI API Error: {e}"
            print(f"⚠️ {error_msg}")
            self.gui.set_expression("sad", "AI Brain Error")
            return "Oops! My AI brain had a hiccup. Please try again."

    def run_assistant_loop(self):
        if not self.mic_initialized_successfully and self.mic_index is not None :
            self.speak("My microphone setup failed. I can talk, but not listen. Restart me to try again.", "sad")
            while self.gui.running:
                time.sleep(1)
                if not self.gui.running: break
            return

        if self.mic_index is None:
            self.speak("No microphone was found. I can't listen. Check mic and restart.", "sad")
            while self.gui.running:
                time.sleep(1)
                if not self.gui.running: break
            return

        self.speak("Hi! I am Loki. How can I help you today?", "neutral")
        
        while self.gui.running:
            question = self.listen()
            if not self.gui.running: break
            if question is None:
                time.sleep(0.1)
                continue

            if any(cmd in question for cmd in ["shutdown loki", "shut down loki", "exit loki", "goodbye loki"]):
                self.speak("Okay, shutting down. Goodbye!", "sleepy")
                time.sleep(1.5)
                self.gui.running = False
                break
            
            answer = self.get_gemini_response(question)
            self.speak(answer)
            
            if not self.gui.running: break
        
        print("Voice AI loop finished.")
…………….voice.py

# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    raise ValueError("Google Generative AI API key not found. Set GENAI_API_KEY in .env file.")

IS_FULLSCREEN = True  # Set to False for windowed mode, True for fullscreen
SCREEN_WIDTH_WINDOWED = 1000
SCREEN_HEIGHT_WINDOWED = 800
……………………..config.py

import cv2
import face_recognition
import os
import pyttsx3
from datetime import datetime
import csv

print("🧠 Face Recognition + Greeting Module Starting...")

# === Initialize TTS Engine ===
engine = pyttsx3.init()
engine.setProperty('rate', 175)  # Speed of speech

def speak_greeting(name):
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    message = f"{greeting}, {name}! Welcome back."
    print(f"[Voice] {message}")
    engine.say(message)
    engine.runAndWait()

# === Load Known Faces ===
known_face_encodings = []
known_face_names = []

known_faces_dir = 'known_faces'

for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(os.path.splitext(filename)[0])

# === Open Visit Log File ===
log_file = open('visit_log.csv', mode='a', newline='')
log_writer = csv.writer(log_file)

# === Webcam & Recognition ===
video_capture = cv2.VideoCapture(0)
greeted = set()  # To avoid repeating greetings

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

        if len(face_distances) > 0:
            best_match_index = face_distances.argmin()
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

        face_names.append(name)

        if name != "Unknown" and name not in greeted:
            speak_greeting(name)
            greeted.add(name)
            log_writer.writerow([name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw the box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # Label with name..
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 1)

    cv2.imshow('VirtuX Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
log_file.close()

….face detecotor
