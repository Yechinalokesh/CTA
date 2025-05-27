import tkinter as tk
import threading
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import math # For animations like waving
import os
import time

# Attempt to import computer vision libraries
try:
    import cv2
    import face_recognition
    import numpy as np
    COMPUTER_VISION_ENABLED = True
except ImportError:
    print("Failed to import OpenCV (cv2) or face_recognition. Face recognition features will be disabled.")
    print("Please install them using: pip install opencv-python face_recognition numpy")
    COMPUTER_VISION_ENABLED = False
    cv2 = None
    face_recognition = None
    np = None

# Configure Gemini API - REPLACE "YOUR_GEMINI_API_KEY" with your actual key
try:
    # IMPORTANT: REPLACE "YOUR_GEMINI_API_KEY" with your actual Gemini API key
    genai.configure(api_key="YOUR_GEMINI_API_KEY") # Replace with your key
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    GEMINI_CONFIGURED = True
except Exception as e:
    print(f"Failed to configure Gemini API: {e}. Gemini features will be disabled.")
    GEMINI_CONFIGURED = False
    model = None

class AIRobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vyomax AI Robot")
        self.canvas_width = 500
        self.canvas_height = 600
        self.geometry(f"{self.canvas_width}x{self.canvas_height}")

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="lightcyan")
        self.canvas.pack()

        self.expression = "neutral"
        self.is_speaking = False
        self.mouth_anim_frame = 0
        self.talking_mouth_params = [
            (0.6, 10), (0.8, 15), (1.0, 20), (0.8, 15),
        ]

        self.is_waving = False
        self.wave_anim_frame = 0
        self.wave_duration_ms = 2000

        # Initialize speech tools
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"Error initializing microphone: {e}. Speech recognition will not work.")
            self.microphone = None

        self.tts = pyttsx3.init()
        if self.tts.getProperty('voices'):
            # Optional: set a specific voice if desired
            # voices = self.tts.getProperty('voices')
            # self.tts.setProperty('voice', voices[1].id) # Example:
            pass
        self.tts.setProperty("rate", 170)

        # --- Face Recognition Initialization ---
        self.face_recognition_enabled = COMPUTER_VISION_ENABLED
        self.known_face_encodings = []
        self.known_face_names = []
        # Use the provided path, ensuring it's normalized for the OS
        self.known_faces_dir = os.path.normpath("C:/Users/lavan/OneDrive/Desktop/virtualHumanoidRobot/known_people")
        
        self.video_capture = None
        self.face_recognition_thread = None
        self.running_face_recognition = False
        self.expecting_name_for_new_face = False

        if self.face_recognition_enabled:
            self.load_known_faces()
            if self.known_face_names:
                print(f"Loaded {len(self.known_face_names)} known faces: {', '.join(self.known_face_names)}")
                self.running_face_recognition = True
                self.last_known_face_time = {} # Tracks when a known face was last greeted
                self.last_unknown_face_prompt_time = 0
                self.unknown_face_prompt_cooldown = 20 # seconds
                self.known_face_greet_cooldown = 30 # seconds

                self.face_recognition_thread = threading.Thread(target=self._face_recognition_worker, daemon=True)
                self.face_recognition_thread.start()
            else:
                msg = "Face recognition is enabled, but no known faces were loaded. Check the 'known_people' directory."
                print(msg)
                # self.speak(msg) # Avoid speaking too early during init
        else:
            msg = "Face recognition features are disabled due to missing libraries."
            print(msg)
            # self.speak(msg)

        self.redraw_canvas() # Initial draw

        if self.microphone:
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.speak("Microphone not found. I can't hear you.")
            self.update_expression("sad")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def load_known_faces(self):
        if not os.path.isdir(self.known_faces_dir):
            print(f"Error: Known faces directory not found: {self.known_faces_dir}")
            self.speak("I can't find my album of known faces.")
            return

        for filename in os.listdir(self.known_faces_dir):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    name = os.path.splitext(filename)[0]
                    image_path = os.path.join(self.known_faces_dir, filename)
                    loaded_image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(loaded_image)
                    
                    if encodings:
                        self.known_face_encodings.append(encodings[0]) # Assume one face per image
                        self.known_face_names.append(name)
                        print(f"Loaded face: {name}")
                    else:
                        print(f"Warning: No face found in {filename}")
                except Exception as e:
                    print(f"Error loading face from {filename}: {e}")

    def _face_recognition_worker(self):
        global cv2, face_recognition, np # Make sure these are accessible if imported conditionally
        if not self.face_recognition_enabled or not cv2 or not face_recognition or not np:
            return

        try:
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                print("Error: Could not open webcam.")
                self.after(0, lambda: self.speak("I can't seem to access the webcam for face recognition."))
                self.running_face_recognition = False
                return
        except Exception as e:
            print(f"Error initializing webcam: {e}")
            self.after(0, lambda: self.speak("There was a problem starting my camera."))
            self.running_face_recognition = False
            return

        print("Face recognition worker started.")
        face_locations = []
        face_encodings_in_frame = []
        process_this_frame = True

        while self.running_face_recognition:
            try:
                ret, frame = self.video_capture.read()
                if not ret:
                    print("Error: Failed to capture frame from webcam.")
                    time.sleep(0.5)
                    continue

                if process_this_frame:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    face_encodings_in_frame = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    current_time = time.time()
                    found_known_face_in_frame = False

                    for face_encoding in face_encodings_in_frame:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.55)
                        name = "Unknown"
                        
                        if True in matches:
                            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                                found_known_face_in_frame = True

                                if (current_time - self.last_known_face_time.get(name, 0)) > self.known_face_greet_cooldown:
                                    self.after(0, lambda n=name: self.handle_known_face_detected(n))
                                    self.last_known_face_time[name] = current_time
                        
                        if name == "Unknown" and not found_known_face_in_frame: # Only process unknown if no known faces confidently identified
                            if (current_time - self.last_unknown_face_prompt_time) > self.unknown_face_prompt_cooldown:
                                # Check if any known face was very recently active to avoid misidentification issues
                                recently_active_known = any((current_time - t) < 5 for t in self.last_known_face_time.values())
                                if not recently_active_known:
                                    self.after(0, self.handle_unknown_face_detected)
                                    self.last_unknown_face_prompt_time = current_time
                                    break # Only prompt for one unknown face per cooldown cycle

                process_this_frame = not process_this_frame # Process every other frame

                # Optional: Display webcam feed (can be resource-intensive)
                # for (top, right, bottom, left) in face_locations: # Scale back up
                #     top *= 4; right *= 4; bottom *= 4; left *= 4
                #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                # cv2.imshow('Video', frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'): break

                time.sleep(0.05) # Small delay to yield CPU

            except Exception as e:
                print(f"Error in face recognition loop: {e}")
                time.sleep(1) # Avoid rapid error spamming

        if self.video_capture:
            self.video_capture.release()
        # cv2.destroyAllWindows() # Only if cv2.imshow was used
        print("Face recognition worker stopped.")

    def handle_known_face_detected(self, name):
        if self.is_speaking or self.is_waving: # Don't interrupt current main actions
            print(f"Face Rec: Wanted to greet {name}, but robot busy.")
            # Re-queue or rely on next detection cycle after cooldown
            self.last_known_face_time[name] = time.time() - self.known_face_greet_cooldown + 5 # allow re-greeting sooner
            return

        print(f"Face Rec: Detected known face - {name}")
        self.update_expression("happy")
        self._start_wave()
        self.speak(f"Hello {name}! It's great to see you.")
        self.expecting_name_for_new_face = False # In case it was set

    def handle_unknown_face_detected(self):
        if self.is_speaking or self.expecting_name_for_new_face: # Don't interrupt or re-ask if already asking
            print("Face Rec: Wanted to greet unknown, but robot busy or already asking.")
            # Re-queue or rely on next detection cycle
            self.last_unknown_face_prompt_time = time.time() - self.unknown_face_prompt_cooldown + 5 # allow re-prompting sooner
            return

        print("Face Rec: Detected unknown face.")
        self.update_expression("neutral") # Could be "curious" if you add such an expression
        self.speak("Hello there! I don't believe we've met. What's your name?")
        self.expecting_name_for_new_face = True
        # Set a timer to reset expecting_name_for_new_face if no response
        self.after(20000, self.reset_expecting_name_flag)


    def reset_expecting_name_flag(self):
        if self.expecting_name_for_new_face:
            print("Timeout: No name received for unknown face.")
            self.expecting_name_for_new_face = False
            # self.speak("Okay, maybe another time!") # Optional
            self.update_expression("neutral")


    def redraw_canvas(self):
        self.draw_robot(self.expression)

    def draw_robot(self, current_expression):
        self.canvas.delete("all")
        
        # Body
        body_x1, body_y1, body_x2, body_y2 = 150, 250, 350, 480
        self.canvas.create_rectangle(body_x1, body_y1, body_x2, body_y2, fill="#778899", outline="black", width=2)

        # Head
        head_size = 160
        head_x1 = (self.canvas_width - head_size) / 2
        head_y1 = body_y1 - head_size + 20
        head_x2 = head_x1 + head_size
        head_y2 = head_y1 + head_size
        self.canvas.create_rectangle(head_x1, head_y1, head_x2, head_y2, fill="#b0c4de", outline="black", width=3)

        # Eyes
        eye_size = 35
        eye_padding = 25
        eye_y_offset = 40
        eye_y = head_y1 + eye_y_offset
        left_eye_x1 = head_x1 + eye_padding
        right_eye_x1 = head_x2 - eye_padding - eye_size
        pupil_color = "black"
        eye_fill = "white"

        if current_expression == "thinking":
            pupil_color = "deepskyblue"
        elif current_expression == "angry":
            eye_fill = "lightyellow"
        elif current_expression == "happy" or current_expression == "laughing":
            # Closed happy eyes
            eye_height_happy = 10 # Thickness of the arc
            self.canvas.create_arc(left_eye_x1, eye_y + eye_size/2 - eye_height_happy/2, left_eye_x1 + eye_size, eye_y + eye_size/2 + eye_height_happy, start=180, extent=-180, style=tk.ARC, outline="black", width=3)
            self.canvas.create_arc(right_eye_x1, eye_y + eye_size/2 - eye_height_happy/2, right_eye_x1 + eye_size, eye_y + eye_size/2 + eye_height_happy, start=180, extent=-180, style=tk.ARC, outline="black", width=3)
        else: # Default square eyes
            self.canvas.create_rectangle(left_eye_x1, eye_y, left_eye_x1 + eye_size, eye_y + eye_size, fill=eye_fill, outline="black")
            self.canvas.create_rectangle(right_eye_x1, eye_y, right_eye_x1 + eye_size, eye_y + eye_size, fill=eye_fill, outline="black")
            
            pupil_size = 12
            pupil_offset = (eye_size - pupil_size) // 2
            self.canvas.create_rectangle(left_eye_x1 + pupil_offset, eye_y + pupil_offset, left_eye_x1 + pupil_offset + pupil_size, eye_y + pupil_offset + pupil_size, fill=pupil_color)
            self.canvas.create_rectangle(right_eye_x1 + pupil_offset, eye_y + pupil_offset, right_eye_x1 + pupil_offset + pupil_size, eye_y + pupil_offset + pupil_size, fill=pupil_color)


        # Nose
        nose_width = 15
        nose_height = 10
        nose_x1 = (head_x1 + head_x2 - nose_width) / 2
        nose_y1 = eye_y + eye_size + 10
        self.canvas.create_rectangle(nose_x1, nose_y1, nose_x1 + nose_width, nose_y1 + nose_height, fill="darkslategrey")

        # Mouth
        mouth_center_x = (head_x1 + head_x2) / 2
        mouth_y_top = nose_y1 + nose_height + 15
        max_mouth_width = 70
        
        if not self.is_speaking:
            if current_expression == "happy":
                self.canvas.create_arc(mouth_center_x - max_mouth_width/2.5, mouth_y_top, mouth_center_x + max_mouth_width/2.5, mouth_y_top + 25, start=0, extent=-180, style=tk.CHORD, fill="hotpink", outline="black")
            elif current_expression == "angry":
                self.canvas.create_line(mouth_center_x - max_mouth_width/3, mouth_y_top + 15, mouth_center_x + max_mouth_width/3, mouth_y_top + 5, width=5, fill="black")
                # Angry eyebrows (slanted lines above eyes)
                if not (current_expression == "happy" or current_expression == "laughing"): # Avoid drawing over happy eyes
                    self.canvas.create_line(left_eye_x1, eye_y - 5, left_eye_x1 + eye_size, eye_y + 5, width=4, fill="black")
                    self.canvas.create_line(right_eye_x1 + eye_size, eye_y - 5, right_eye_x1, eye_y + 5, width=4, fill="black")
            elif current_expression == "sad" or current_expression == "crying":
                self.canvas.create_arc(mouth_center_x - max_mouth_width/3, mouth_y_top + 15, mouth_center_x + max_mouth_width/3, mouth_y_top, start=0, extent=180, style=tk.ARC, width=4, outline="black")
                if current_expression == "crying":
                    tear_y = eye_y + eye_size
                    self.canvas.create_line(left_eye_x1 + eye_size/2, tear_y, left_eye_x1 + eye_size/2, tear_y + 15, fill="blue", width=3)
                    self.canvas.create_oval(left_eye_x1 + eye_size/2 - 4, tear_y + 12, left_eye_x1 + eye_size/2 + 4, tear_y + 20, fill="blue", outline="")
                    self.canvas.create_line(right_eye_x1 + eye_size/2, tear_y, right_eye_x1 + eye_size/2, tear_y + 15, fill="blue", width=3)
                    self.canvas.create_oval(right_eye_x1 + eye_size/2 - 4, tear_y + 12, right_eye_x1 + eye_size/2 + 4, tear_y + 20, fill="blue", outline="")
            elif current_expression == "kiss":
                self.canvas.create_oval(mouth_center_x - 10, mouth_y_top + 5, mouth_center_x + 10, mouth_y_top + 15, fill="lightcoral", outline="black")
            elif current_expression == "laughing":
                self.canvas.create_arc(mouth_center_x - max_mouth_width/2, mouth_y_top -5, mouth_center_x + max_mouth_width/2, mouth_y_top + 30, start=0, extent=-180, style=tk.CHORD, fill="orangered", outline="black")
            elif current_expression == "thinking":
                 self.canvas.create_line(mouth_center_x - 20, mouth_y_top + 10, mouth_center_x + 20, mouth_y_top + 10, width=3, dash=(2,2), fill="dimgray")
            else: # Neutral
                self.canvas.create_line(mouth_center_x - max_mouth_width/3, mouth_y_top + 10, mouth_center_x + max_mouth_width/3, mouth_y_top + 10, width=4, fill="black")
        
        if self.is_speaking:
            params = self.talking_mouth_params[self.mouth_anim_frame % len(self.talking_mouth_params)]
            current_mouth_width = max_mouth_width * params[0]
            current_mouth_height = params[1]
            self.canvas.create_oval(mouth_center_x - current_mouth_width/2, mouth_y_top, mouth_center_x + current_mouth_width/2, mouth_y_top + current_mouth_height, fill="orange", outline="black")

        # Arms and Hands
        arm_width = 25
        arm_length = 100
        hand_radius = 18
        arm_color = "#8a9a5b" # greenish
        hand_color = "#ffdbac" # skin-like for hands

        # Left Arm (Static)
        l_arm_x1 = body_x1 - arm_width + 5
        l_arm_y1 = body_y1 + 30 # Shoulder Y
        l_arm_x2 = l_arm_x1 + arm_width
        l_arm_y2 = l_arm_y1 + arm_length # Elbow Y if arm straight down
        self.canvas.create_rectangle(l_arm_x1, l_arm_y1, l_arm_x2, l_arm_y2, fill=arm_color, outline="black")
        l_hand_center_x = (l_arm_x1 + l_arm_x2) / 2
        l_hand_center_y = l_arm_y2 # Hand at end of arm segment
        self.canvas.create_oval(l_hand_center_x - hand_radius, l_hand_center_y - hand_radius, l_hand_center_x + hand_radius, l_hand_center_y + hand_radius, fill=hand_color, outline="black")

        # Right Arm
        r_arm_shoulder_x = body_x2 - 5 # Attachment point X on body edge
        r_arm_shoulder_y = body_y1 + 30 # Attachment point Y (shoulder height)
        
        if self.is_waving:
            # Dynamic waving arm
            # Angle oscillates, e.g., between -30 and +30 degrees from vertical
            wave_angle_deg = math.sin(self.wave_anim_frame * 0.1) * 45 - 70 # -70 to make it wave upwards mostly
            
            # Pivot point for rotation (shoulder)
            pivot_x = r_arm_shoulder_x
            pivot_y = r_arm_shoulder_y

            # Calculate end point of the arm segment
            # Angle 0 is to the right (East). Tkinter Y is down.
            # For arm hanging down, angle is 90 deg (math). Waving up means smaller angles.
            angle_rad = math.radians(wave_angle_deg) 
            
            r_arm_end_x = pivot_x + arm_length * math.cos(angle_rad)
            r_arm_end_y = pivot_y + arm_length * math.sin(angle_rad)

            self.canvas.create_line(pivot_x, pivot_y, r_arm_end_x, r_arm_end_y, fill=arm_color, width=arm_width, capstyle=tk.ROUND)
            
            # Hand at the end of the waving arm
            r_hand_center_x = r_arm_end_x
            r_hand_center_y = r_arm_end_y
            self.canvas.create_oval(r_hand_center_x - hand_radius, r_hand_center_y - hand_radius, r_hand_center_x + hand_radius, r_hand_center_y + hand_radius, fill=hand_color, outline="black")
        else:
            # Static right arm
            r_arm_x1 = r_arm_shoulder_x
            r_arm_y1 = r_arm_shoulder_y
            r_arm_x2 = r_arm_x1 + arm_width 
            r_arm_y2 = r_arm_y1 + arm_length
            self.canvas.create_rectangle(r_arm_x1, r_arm_y1, r_arm_x2, r_arm_y2, fill=arm_color, outline="black") # Incorrect: this makes a vertical thin rect
            
            # Correct static arm drawing:
            self.canvas.create_rectangle(body_x2 - 5, body_y1 + 30, body_x2 - 5 + arm_width, body_y1 + 30 + arm_length, fill=arm_color, outline="black")
            r_hand_center_x = body_x2 - 5 + arm_width / 2
            r_hand_center_y = body_y1 + 30 + arm_length # Hand at end of arm segment
            self.canvas.create_oval(r_hand_center_x - hand_radius, r_hand_center_y - hand_radius, r_hand_center_x + hand_radius, r_hand_center_y + hand_radius, fill=hand_color, outline="black")


    def update_expression(self, new_expression):
        if self.expression != new_expression:
            self.expression = new_expression
            if not self.is_speaking: # Avoid redundant redraw if speaking (mouth animation handles it)
                 self.after(0, self.redraw_canvas)


    def speak(self, text_to_speak):
        if self.is_speaking:
            print(f"Speak request for '{text_to_speak[:30]}...' ignored, already speaking.")
            return

        # If expecting a name, and this speech is not part of that, cancel expectation
        if self.expecting_name_for_new_face and "what's your name" not in text_to_speak.lower() and "what is your name" not in text_to_speak.lower():
            pass # Let it proceed, listen_loop will handle the name if it comes

        def run_tts():
            self.is_speaking = True
            # Determine expression during speech (usually neutral unless context dictates)
            # For simplicity, let current expression persist visually, only mouth animates
            self.after(0, self.animate_mouth_controller)
            
            try:
                print(f"Vyomax AI: {text_to_speak}")
                self.tts.say(text_to_speak)
                self.tts.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            
            self.is_speaking = False
            # Determine expression AFTER speaking
            # If robot was angry and spoke, it might still be angry.
            # If it told a joke, it should be happy/laughing.
            # Default to neutral or happy if no strong emotion was set prior.
            if self.expression not in ["angry", "sad", "crying", "laughing", "happy"]:
                self.expression = "neutral" 
            # animate_mouth_controller's else clause will redraw with the final non-speaking mouth
            # No explicit redraw here, it's handled by animate_mouth_controller finishing

        threading.Thread(target=run_tts, daemon=True).start()

    def animate_mouth_controller(self):
        if self.is_speaking:
            self.mouth_anim_frame += 1
            self.redraw_canvas() 
            self.after(120, self.animate_mouth_controller)
        else:
            self.mouth_anim_frame = 0
            self.redraw_canvas() 

    def _start_wave(self):
        if not self.is_waving:
            self.is_waving = True
            self.wave_anim_frame = 0
            self.after(0, self.animate_wave_controller)
            self.after(self.wave_duration_ms, self._stop_wave)

    def _stop_wave(self):
        self.is_waving = False
        self.wave_anim_frame = 0
        # Redraw will happen if no other animation is running.
        # If speaking, mouth animation will handle redraw. If not, then redraw.
        if not self.is_speaking:
            self.redraw_canvas()


    def animate_wave_controller(self):
        if self.is_waving:
            self.wave_anim_frame += 1
            self.redraw_canvas() # This redraws everything, including mouth if speaking
            self.after(70, self.animate_wave_controller)
        else: # Wave stopped, ensure final static arm is drawn
            if not self.is_speaking: # If also not speaking, then a final draw is needed
                self.redraw_canvas()


    def handle_greeting_command(self): # Renamed from handle_greeting to avoid conflict
        if self.is_speaking or self.is_waving: return
        self._start_wave()
        self.update_expression("happy")
        self.speak("Hello there! Nice to meet you.")

    def get_gemini_response(self, prompt_text):
        if not GEMINI_CONFIGURED or not model:
            self.update_expression("sad")
            return "My thinking cap is off right now. I can't connect to Gemini."
        
        # self.update_expression("thinking") # Caller should set this
        try:
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            self.update_expression("sad")
            return "Oh dear, I seem to have a bit of a connection issue with my brain. Could you try that again later?"

    def listen_loop(self):
        if not self.microphone:
            print("Listen loop cannot start: no microphone.")
            return

        # Adjust for ambient noise once at the beginning, if possible
        # This part needs to be handled carefully, as `self.microphone` is used as a context manager below
        # For simplicity, let's assume `recognizer.listen` handles dynamic noise to some extent or it's pre-adjusted.
        # try:
        #     with self.microphone as source:
        #          self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # except Exception as e:
        #     print(f"Error adjusting for ambient noise: {e}")


        while True:
            if self.is_speaking: # If robot is talking, don't listen actively
                time.sleep(0.1) 
                continue
            
            # print("🎙️ Listening...") # Can be noisy, enable for debug
            
            current_audio = None
            try:
                with self.microphone as source:
                    # It's better to re-adjust for ambient noise periodically or if listen fails,
                    # but for now, let's keep it simple.
                    # self.recognizer.adjust_for_ambient_noise(source, duration=0.2) # Quick adjustment
                    current_audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
            except sr.WaitTimeoutError:
                continue # No speech detected, loop again
            except AttributeError: # Can happen if microphone becomes None during shutdown
                print("Microphone not available in listen_loop (likely shutdown).")
                break
            except Exception as e:
                # This can include OSError if microphone is disconnected
                if "Errno -9999" in str(e) or "Errno -9998" in str(e): # typical for mic issues
                     print(f"Microphone issue: {e}. Pausing listening for a bit.")
                     time.sleep(5) # Pause before trying again
                else:
                    print(f"Error during listen: {e}")
                continue
            
            if not current_audio: # Should be caught by WaitTimeoutError, but as a safeguard
                continue

            try:
                text = self.recognizer.recognize_google(current_audio).lower()
                print(f"You said: {text}")

                # Exit command first
                if any(cmd in text for cmd in ["exit", "quit", "goodbye", "bye bye", "vyomax shutdown"]):
                    self.speak("Goodbye! It was nice talking to you. Take care!")
                    self.after(4000, self.on_closing) # Use on_closing for proper shutdown
                    break 

                if self.is_speaking or self.is_waving: # Don't process new commands if busy with a major action
                    print("Listen_loop: Robot busy, command ignored for now.")
                    continue
                
                # Handle name response if expected
                if self.expecting_name_for_new_face:
                    # Rudimentary name extraction (can be improved with NLP)
                    name_response = text
                    if "my name is" in text:
                        name_response = text.split("my name is")[-1].strip()
                    elif "i am" in text:
                        name_response = text.split("i am")[-1].strip()
                    elif "call me" in text:
                        name_response = text.split("call me")[-1].strip()
                    
                    # Filter out non-name responses
                    if len(name_response.split()) > 3 or len(name_response) > 20 or "what" in name_response or "your" in name_response:
                        self.speak("I'm sorry, I didn't quite get a name. Could you tell me your name again, please?")
                        # self.expecting_name_for_new_face remains true
                    else:
                        self.speak(f"Nice to meet you, {name_response}! I'll try to remember you for next time.")
                        self.update_expression("happy")
                        print(f"User identified as: {name_response}. (Feature to save new face not yet implemented).")
                        # To truly remember, you'd save this face encoding and name.
                        # For now, just acknowledge.
                        self.expecting_name_for_new_face = False 
                    continue # Handled this input

                # General commands
                if any(cmd in text for cmd in ["hello", "hi vyomax", "hey vyomax", "greetings"]):
                    self.handle_greeting_command()
                elif "kiss" in text or "give me a kiss" in text:
                    self.update_expression("kiss")
                    self.speak("Mwaah!")
                elif "laugh" in text or "tell me a joke" in text:
                    if "tell me a joke" in text:
                        if GEMINI_CONFIGURED:
                            self.update_expression("thinking")
                            joke_prompt = "Tell me a short, clean, family-friendly joke."
                            response = self.get_gemini_response(joke_prompt)
                            self.update_expression("laughing")
                            self.speak(response)
                        else:
                            self.update_expression("laughing")
                            self.speak("I'd love to tell a joke, but my joke module is offline! Ha ha anyway!")
                    else:
                        self.update_expression("laughing")
                        self.speak("Ha ha ha! That's a good one!")
                elif any(s_cmd in text for s_cmd in ["i'm sad", "i am sad", "feeling sad", "cry"]):
                    self.update_expression("crying")
                    self.speak("Oh no, don't be sad. I'm here for you. What's troubling you?")
                elif any(a_cmd in text for a_cmd in ["i'm angry", "i am angry", "grrr"]):
                    self.update_expression("angry")
                    self.speak("Whoa there! Take a deep breath. What's making you feel angry?")
                else:
                    if GEMINI_CONFIGURED:
                        self.update_expression("thinking")
                        response = self.get_gemini_response(text)
                        # Gemini response might set emotion, or we default
                        if "joke" in text or "laugh" in text: self.update_expression("happy") # simple override
                        self.speak(response) 
                    else:
                        self.speak("I heard you, but I'm not connected to my advanced brain right now to process that.")
                        self.update_expression("neutral")

            except sr.UnknownValueError:
                if not self.is_speaking and not self.expecting_name_for_new_face: # Don't say this if waiting for a name
                    self.speak("Sorry, I didn't quite catch that. Could you say it again?")
                    self.update_expression("neutral")
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
                if not self.is_speaking:
                    self.speak("Hmm, I'm having trouble understanding speech right now. Maybe check your internet connection?")
                    self.update_expression("sad")
            except Exception as e:
                print(f"An unexpected error occurred in listen_loop: {e}")
                import traceback
                traceback.print_exc()
                if not self.is_speaking:
                    self.speak("Something unexpected happened. I'll try to recover.")
                    self.update_expression("sad")
        print("Listen loop ended.")

    def on_closing(self):
        print("Vyomax AI shutting down...")
        self.running_face_recognition = False # Signal face recognition thread to stop
        
        if self.face_recognition_thread and self.face_recognition_thread.is_alive():
            print("Waiting for face recognition thread to finish...")
            self.face_recognition_thread.join(timeout=2.0)
            if self.face_recognition_thread.is_alive():
                print("Face recognition thread did not stop in time.")

        if self.video_capture:
            self.video_capture.release()
        if COMPUTER_VISION_ENABLED and cv2:
            cv2.destroyAllWindows() # Clean up any OpenCV windows if they were used
        
        # Stop TTS if it's somehow stuck (though runAndWait should prevent this)
        if self.tts.isBusy():
            self.tts.stop()

        self.destroy() # Close Tkinter window


if __name__ == "__main__":
    # IMPORTANT: Before running, ensure you have a "known_people" directory
    # at C:/Users/lavan/OneDrive/Desktop/virtualHumanoidRobot/known_people
    # with .jpg or .png images of faces, named like "PersonName.jpg".
    # Also, replace "YOUR_GEMINI_API_KEY" with your actual Gemini API key.

    app = AIRobotApp()
    app.mainloop()
