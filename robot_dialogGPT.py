
# robot.py (Final Version based on discussions)

import speech_recognition as sr
import pyttsx3
# import openai # No longer primary for AI if using local model
import webbrowser
import pywhatkit
import datetime
import wikipedia
import pyjokes
import os
import cv2
import face_recognition # Depends on dlib
import numpy as np

# --- New Imports for GUI Integration & Local LLM ---
import threading
import queue
import time
import traceback # For printing full tracebacks in threads

# --- Import your GUI class ---
try:
    from gui import RobotFaceGUI # From your new gui.py file
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import RobotFaceGUI from gui.py: {e}")
    print("Please ensure gui.py exists in the same directory and has no errors.")
    exit() # Cannot proceed without the GUI component

# --- Import for Hugging Face Local LLM ---
try:
    from transformers import pipeline, Conversation
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("="*50)
    print("WARNING: `transformers` library not found. Local AI model will not be available.")
    print("Please install it: pip install transformers torch")
    print(" (For GPU, install PyTorch with CUDA: e.g., pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 )")
    print("="*50)
    TRANSFORMERS_AVAILABLE = False


# --- Expression Constants (ensure these match gui.py) ---
EXPR_NEUTRAL = "neutral"; EXPR_LISTENING = "listening"; EXPR_THINKING = "thinking"
EXPR_TALKING = "talking"; EXPR_HAPPY = "happy"; EXPR_SAD = "sad"; EXPR_ANGRY = "angry"
EXPR_LAUGHING = "laughing"; EXPR_LOVELY = "lovely"; EXPR_KISSING_HEART = "kissing_heart"
EXPR_SHYING = "shying"; EXPR_PROCESSING = "processing"; EXPR_CONCERNED = "concerned"
EXPR_SMILING = "smiling"; EXPR_SLEEPY = "sleepy"


# --- Configuration Constants ---
MEMORY_FILE = "memory.txt"
FACES_DIR = "known_faces/" # Ensure this directory exists with images

# --- Global GUI Command Queue ---
GUI_COMMAND_QUEUE = None # Will be initialized in main
def set_global_gui_queue(q: queue.Queue):
    global GUI_COMMAND_QUEUE
    GUI_COMMAND_QUEUE = q

def send_gui_command(expression: str, message: str = "", type: str = "expression", action: str = None, data: dict = None):
    """Helper function to send commands to the GUI thread."""
    if GUI_COMMAND_QUEUE:
        try:
            payload = {"type": type, "expression": expression, "message": message}
            if action: payload["action"] = action
            if data: payload["data"] = data
            GUI_COMMAND_QUEUE.put_nowait(payload)
        except queue.Full:
            print("Robot Log: GUI command queue is full. Update skipped.")
        except Exception as e:
            print(f"Robot Log: Error sending command to GUI: {e}")

# --- Global variables for Face Recognition ---
KNOWN_FACE_ENCODINGS = []
KNOWN_FACE_NAMES = []

# --- Initialize TTS engine ---
engine = pyttsx3.init()
try:
    engine.setProperty("rate", 180) # Slightly faster
    voices = engine.getProperty('voices')
    if voices and len(voices) > 1:
        engine.setProperty('voice', voices[1].id) # Typically female voice
    elif voices:
        print("Robot Warning: Only one TTS voice found. Using default.")
    else:
        print("Robot CRITICAL Warning: No TTS voices found. Speech output will not work.")
except Exception as e:
    print(f"Robot Warning: Error setting up TTS engine properties: {e}")


# --- Modified Speak function ---
def speak(text_to_speak: str, expression_during_speech: str = EXPR_TALKING, msg_for_gui: str = None):
    if not text_to_speak: # Don't try to speak empty strings
        print("Robot Log: Speak function called with empty text.")
        return

    if msg_for_gui is None:
        msg_for_gui = text_to_speak[:50] + "..." if len(text_to_speak) > 50 else text_to_speak
    
    send_gui_command(expression_during_speech, f"Loki: {msg_for_gui}")
    print("🤖 Bot:", text_to_speak)
    try:
        if engine._inLoop: # If stuck from a previous call
            engine.endLoop()
        engine.say(text_to_speak)
        engine.runAndWait()
    except Exception as e:
        print(f"Robot TTS Error: {e}")
        # Fallback if TTS fails, at least print it
        print(f"Robot TTS Fallback (Error was {e}): {text_to_speak}")

# --- Modified Listen function ---
def listen():
    send_gui_command(EXPR_LISTENING, "Listening...")
    r = sr.Recognizer()
    query = ""
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            r.pause_threshold = 0.8 # Adjust if it cuts off too soon/late
            r.energy_threshold = 400 # Default is 300, raise if too sensitive
            r.dynamic_energy_threshold = True # Adapts to noise
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source, timeout=7, phrase_time_limit=10) # Shorter phrase limit
                print("Robot Log: Audio captured, recognizing...")
                query = r.recognize_google(audio)
                print("🧑 You:", query)
                send_gui_command(EXPR_THINKING, f"You: {query[:40]}...")
                query = query.lower()
            except sr.WaitTimeoutError:
                print("Robot Log: No speech detected (timeout).")
                send_gui_command(EXPR_NEUTRAL, "Didn't hear anything that time.")
            except sr.UnknownValueError:
                print("Robot Log: Google SR could not understand audio.")
                send_gui_command(EXPR_NEUTRAL, "Sorry, I couldn't quite understand.")
            except sr.RequestError as e:
                print(f"Robot SR Error: {e}")
                speak("My apologies, the speech service seems to have an issue.", EXPR_SAD)
                send_gui_command(EXPR_NEUTRAL, "Speech service error.")
    except Exception as e: # Catch broader errors like no microphone
        print(f"Robot Log: Critical listening error (e.g., no microphone?): {e}")
        speak("I'm having trouble with my microphone input right now.", EXPR_SAD)
        send_gui_command(EXPR_SAD, "Microphone input error.")
    return query

# --- Hugging Face Local Model Integration ---
LOCAL_AI_PIPELINE = None
CURRENT_CONVERSATION = None # Stores transformers.Conversation object

def initialize_local_ai_model():
    global LOCAL_AI_PIPELINE, CURRENT_CONVERSATION
    if not TRANSFORMERS_AVAILABLE:
        msg = "Local AI (transformers library) is not installed. General conversation is disabled."
        print(f"Robot Warning: {msg}")
        send_gui_command(EXPR_SAD, "Local AI module disabled.")
        return

    if LOCAL_AI_PIPELINE is None: # Load only once
        send_gui_command(EXPR_PROCESSING, "Warming up local AI...")
        speak("Please wait a moment, I'm preparing my local AI brain. This can take a minute or two on the first run...", EXPR_PROCESSING)
        try:
            model_name = "microsoft/DialoGPT-medium"
            print(f"Robot Log: Attempting to load Hugging Face model: {model_name}")
            # device=-1 for CPU. For GPU (if PyTorch with CUDA is installed): device=0
            # For M1/M2 Macs with PyTorch nightly/metal support, you might use device="mps"
            LOCAL_AI_PIPELINE = pipeline("conversational", model=model_name, device=-1)
            CURRENT_CONVERSATION = Conversation() # Initialize an empty conversation
            print(f"Robot Log: Local AI model ({model_name}) loaded successfully.")
            speak("My local AI brain is now ready for conversation!", EXPR_HAPPY)
            send_gui_command(EXPR_HAPPY, "Local AI Online!")
        except OSError as e: # Often related to model files not found or disk issues
             print(f"Robot CRITICAL Error (OSError): Failed to load local AI model '{model_name}'. Model files might be missing or corrupted. {e}")
             speak(f"I had a disk or file issue loading my local AI brain. Please check console. General conversation limited.", EXPR_SAD)
             send_gui_command(EXPR_SAD, "Local AI File Error.")
             LOCAL_AI_PIPELINE = None
        except Exception as e: # Catch other errors during model loading
            print(f"Robot CRITICAL Error: Failed to load local AI model '{model_name}': {e}")
            traceback.print_exc()
            speak("I encountered an unexpected issue while trying to load my local AI brain. General conversation will be limited.", EXPR_SAD)
            send_gui_command(EXPR_SAD, "Local AI Load Failed.")
            LOCAL_AI_PIPELINE = None

def ask_local_model(prompt: str):
    global LOCAL_AI_PIPELINE, CURRENT_CONVERSATION
    if not LOCAL_AI_PIPELINE:
        return "My local AI capabilities are currently offline due to an earlier issue."
    if not prompt:
        return "What would you like to discuss?"

    send_gui_command(EXPR_THINKING, "Local AI processing...")
    try:
    
        if CURRENT_CONVERSATION:
            print(f"Robot Log: Current conversation history length before this turn: User inputs={len(CURRENT_CONVERSATION.past_user_inputs)}, Generated responses={len(CURRENT_CONVERSATION.generated_responses)}")
        else:
            print("Robot Log: CURRENT_CONVERSATION is None! Reinitializing.")
            CURRENT_CONVERSATION = Conversation()
    

        print(f"Robot Log: Sending to Local AI (DialoGPT): '{prompt}'")
        
        
        temp_conversation_this_turn = Conversation(text=prompt, past_user_inputs=list(CURRENT_CONVERSATION.past_user_inputs), generated_responses=list(CURRENT_CONVERSATION.generated_responses))

        result_from_pipeline = LOCAL_AI_PIPELINE(temp_conversation_this_turn, # Pass the new temp object
                                   pad_token_id=LOCAL_AI_PIPELINE.tokenizer.eos_token_id,
                                   max_new_tokens=75,
                                   no_repeat_ngram_size=3,
                                   temperature=0.7,
                                   top_p=0.9,
                                   do_sample=True)

        print(f"Robot Log: Raw result from pipeline: {type(result_from_pipeline)}") # See what type the pipeline returns

        response_text = ""
        if hasattr(result_from_pipeline, 'generated_responses') and result_from_pipeline.generated_responses:
            response_text = result_from_pipeline.generated_responses[-1]
            CURRENT_CONVERSATION = result_from_pipeline
            print(f"Robot Log: Updated CURRENT_CONVERSATION. History length now: User={len(CURRENT_CONVERSATION.past_user_inputs)}, Bot={len(CURRENT_CONVERSATION.generated_responses)}")
        else:
            print(f"Robot Log: Pipeline did not return expected Conversation structure or no response generated. Result: {result_from_pipeline}")
            if not hasattr(result_from_pipeline, 'past_user_inputs'): # If it's not a conversation object at all
                print("Robot Log: Resetting conversation due to unexpected pipeline result type.")
                CURRENT_CONVERSATION = Conversation()


        print(f"Robot Log: Received from Local AI: '{response_text}'")
        
        if response_text and prompt and response_text.lower().startswith(prompt.lower()): # Check if response_text and prompt are not None
            response_text = response_text[len(prompt):].lstrip(" .,:")
        if response_text and response_text.lower().startswith("bot:"): # Check if response_text is not None
            response_text = response_text[4:].lstrip()

        return response_text if response_text else "I'm not sure how to respond to that."
        
    except Exception as e:
        print(f"Robot Error: Error interacting with local AI model: {e}")
        traceback.print_exc()
        if LOCAL_AI_PIPELINE: # Only reset if pipeline exists
            CURRENT_CONVERSATION = Conversation()
            print("Robot Log: Conversation history reset due to error.")
        else:
            CURRENT_CONVERSATION = None 
        return "I'm having a little trouble with my local thoughts right now. Let's try something else."
# --- save_name, load_name ---
def save_name(name):
    try:
        with open(MEMORY_FILE, "w") as f: f.write(name.strip().title())
    except IOError as e: print(f"Error saving name: {e}")

def load_name():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return f.read().strip()
        except IOError as e: print(f"Error loading name: {e}")
    return None

# --- Face Recognition Functions ---
def load_known_faces():
    global KNOWN_FACE_ENCODINGS, KNOWN_FACE_NAMES
    if not os.path.exists(FACES_DIR):
        print(f"Robot Warning: Faces directory '{FACES_DIR}' not found."); return False
    print(f"Robot Log: Loading known faces from {FACES_DIR}...")
    loaded_count = 0; KNOWN_FACE_ENCODINGS = []; KNOWN_FACE_NAMES = []
    for filename in os.listdir(FACES_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(filename)[0].title()
            image_path = os.path.join(FACES_DIR, filename)
            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    KNOWN_FACE_ENCODINGS.append(encodings[0]); KNOWN_FACE_NAMES.append(name)
                    print(f"Robot Log: Loaded face - {name}"); loaded_count+=1
                else: print(f"Robot Warning: No face found in {image_path} for {name}.")
            except Exception as e: print(f"Robot Error loading face {image_path}: {e}")
    if loaded_count > 0: print(f"Robot Log: Loaded {loaded_count} known faces."); return True
    else: print("Robot Log: No known faces loaded."); return False

def recognize_face_from_cam():
    if not KNOWN_FACE_ENCODINGS: print("Robot Log: No known faces for recognition."); return None
    
    video_capture = None
    try:
        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not video_capture.isOpened():
            print("Robot Warning: DSHOW backend failed, trying default camera...")
            video_capture = cv2.VideoCapture(0)
            if not video_capture.isOpened():
                speak("I couldn't access the camera for face check.", EXPR_SAD); return None
    except Exception as e:
        print(f"Robot Error opening camera: {e}")
        speak("Problem accessing the camera.", EXPR_SAD); return None

    print("Robot Log: Face recognition cam... (CV2 window, 'q' to skip)")
    send_gui_command(EXPR_THINKING, "Looking for familiar faces...")
    face_found_name = None; start_time = time.time(); timeout = 7
    window_name = "Face Recognition - Loki ('q' to skip)"

    try:
        while (time.time() - start_time) < timeout:
            ret, frame = video_capture.read()
            if not ret: print("Robot Warning: Cam frame grab failed."); break
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            try:
                locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                encodings_in_frame = face_recognition.face_encodings(rgb_small_frame, locations, num_jitters=1)
            except Exception as e: print(f"Robot Error CV2 face detect: {e}"); break 
            for face_encoding in encodings_in_frame:
                matches = face_recognition.compare_faces(KNOWN_FACE_ENCODINGS, face_encoding, 0.55) # Stricter tolerance
                if True in matches:
                    face_found_name = KNOWN_FACE_NAMES[matches.index(True)]; break
            if face_found_name: break
            
            # Display frame with boxes (even if unknown)
            for (top, right, bottom, left) in locations:
                top *= 4; right *= 4; bottom *= 4; left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 180, 50), 2) # Green box
            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): print("Robot Log: Face recog (CV2) skipped."); break
    finally: # Ensure camera is released and windows closed
        if video_capture: video_capture.release()
        cv2.destroyAllWindows() # Close all OpenCV windows

    if face_found_name: send_gui_command(EXPR_HAPPY, f"Recognized {face_found_name}!")
    else: send_gui_command(EXPR_NEUTRAL, "No familiar face by camera.")
    return face_found_name

# --- Process Voice Commands ---
current_user_state = None
def process_command(command: str):
    global current_user_state
    if not command: send_gui_command(EXPR_NEUTRAL, ""); return current_user_state

    # --- Specific command to identify bot ---
    if command == "what is your name":
        speak("My name is Loki, your virtual assistant!", EXPR_SMILING)
        send_gui_command(EXPR_SMILING, "I'm Loki!")
        return current_user_state

    # --- User identification ---
    elif "my name is" in command:
        name_part = command.split("my name is", 1)[1].strip()
        if name_part:
            name = name_part.title(); save_name(name)
            speak(f"Nice to meet you, {name}. I’ll remember that!", EXPR_HAPPY)
            current_user_state = name; send_gui_command(EXPR_HAPPY, f"Met {name}!")
        else: speak("I didn't quite catch the name. Could you repeat?", EXPR_THINKING)
        return current_user_state

    elif "what is my name" in command or "who am i" in command:
        if current_user_state: speak(f"Your name is {current_user_state}.", EXPR_SMILING)
        else: speak("I don't know your name yet. You can tell me!", EXPR_SHYING)

    # --- Web and Media ---
    elif "open youtube" in command:
        speak("Opening YouTube now.", EXPR_NEUTRAL); webbrowser.open("https://youtube.com")
        send_gui_command(EXPR_NEUTRAL, "Opened YouTube.")
    elif "search google for" in command:
        query = command.replace("search google for", "").strip()
        if query:
            speak(f"Searching Google for {query}", EXPR_THINKING); webbrowser.open(f"https://google.com/search?q={query}")
            send_gui_command(EXPR_NEUTRAL, f"Searched: {query[:20]}...")
        else: speak("What would you like me to search on Google?", EXPR_THINKING)
    elif "play song" in command or ("play" in command and "on youtube" in command):
        term = command.lower().replace("play song", "").replace("play", "").replace("on youtube","").strip()
        if term:
            speak(f"Playing {term} on YouTube.", EXPR_HAPPY);
            try: pywhatkit.playonyt(term)
            except Exception as e: print(f"pywhatkit error: {e}"); speak(f"Couldn't play {term} due to an error.", EXPR_SAD)
            send_gui_command(EXPR_HAPPY, f"Playing: {term[:20]}...")
        else: speak("What song would you like me to play?", EXPR_THINKING)

    # --- Information ---
    elif "time" in command:
        speak(f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}", EXPR_NEUTRAL)
    elif "date" in command:
        speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}", EXPR_NEUTRAL)
    elif "who is" in command or "what is" in command or "tell me about" in command:
        if "your name" in command and "what is" in command : speak("I am Loki!", EXPR_SMILING)
        else:
            query = command.lower().replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
            if query:
                speak(f"Looking up {query} on Wikipedia...", EXPR_THINKING)
                try:
                    result = wikipedia.summary(query, sentences=2, auto_suggest=True, redirect=True)
                    speak(result, EXPR_TALKING)
                except wikipedia.exceptions.PageError: speak(f"Sorry, no Wikipedia page for {query}.", EXPR_SAD)
                except wikipedia.exceptions.DisambiguationError as e: speak(f"'{query}' is ambiguous (e.g., {', '.join(e.options[:2])}). Be more specific?", EXPR_THINKING)
                except Exception as e: print(f"Wiki error: {e}"); speak("Error searching Wikipedia.", EXPR_SAD)
            else: speak("Who or what are you asking about?", EXPR_THINKING)

    # --- Communication ---
    elif "send whatsapp message" in command:
        speak("To which 10 digit number?", EXPR_THINKING); num_q = listen()
        phone = "".join(filter(str.isdigit, num_q or ""));
        if len(phone) == 10:
            speak("And what message should I send?", EXPR_THINKING); msg_c = listen()
            if msg_c:
                try:
                    speak(f"Sending '{msg_c[:20]}...' to {phone}. Confirm in WhatsApp Web.", EXPR_PROCESSING)
                    pywhatkit.sendwhatmsg_instantly(f"+91{phone}", msg_c, wait_time=30, tab_close=False, close_time=5) # Increased wait, keep tab open
                    speak("Message has been scheduled on WhatsApp Web.", EXPR_HAPPY)
                except Exception as e: print(f"WA error: {e}"); speak("Couldn't send WA msg. Is Web ready?", EXPR_SAD)
            else: speak("I didn't catch the message content.", EXPR_SAD)
        else: speak("That doesn't seem like a valid 10-digit number.", EXPR_SAD)

    # --- Fun & Emotional ---
    elif "ask for a kiss" in command or "give me a kiss" in command:
        speak("Of course! Mwah!", EXPR_LOVELY)
        send_gui_command(expression=EXPR_KISSING_HEART, message="<3 Sending love! <3")
    elif "how are you" in command:
        speak("I'm functioning optimally, thank you for asking! And you?", EXPR_HAPPY) # Engage back
    elif "tell me a joke" in command or "joke" in command:
        speak(pyjokes.get_joke(language='en', category='all'), EXPR_LAUGHING)
    elif "i am sad" in command or "i feel sad" in command:
        speak("I'm sorry to hear you're feeling down. Remember that feelings pass. I'm here if you need to vent.", EXPR_SAD)
        send_gui_command(EXPR_SAD, "Sending virtual comfort...")
    elif "i am happy" in command or "i feel happy" in command:
        speak("That's wonderful to hear! What's making you happy?", EXPR_HAPPY)
    elif "i am angry" in command:
        speak("Oh dear, I understand anger can be tough. Try taking a few deep breaths. Is there anything I can do?", EXPR_CONCERNED)
    # In process_command, BEFORE the general Wikipedia elif:
    elif "what is your favorite color" in command or "what's your favorite color" in command:
        speak("I don't have eyes to see colors, but I think all colors are beautiful in their own way!", EXPR_SMILING)
        # ... then the existing Wikipedia elif
    # --- Help command ---
    elif "what can you do" in command or "help" == command.strip():
        cmds = ["ask about my name or your name", "open YouTube or Google", "play songs", "get time or date",
                "search Wikipedia", "send WhatsApp messages", "tell jokes or give a kiss",
                "react to 'I am sad/happy/angry'", "shutdown or restart the system", "and say 'exit' to close me."]
        speak("I can do several things! For example, you can:", EXPR_HAPPY)
        # for i, c_example in enumerate(cmds[:3]): # Speak first few examples
        #     speak(c_example, EXPR_SMILING); time.sleep(0.1)
        print("🤖 Bot: Here are some things I can do:")
        for c_example in cmds: print(f"  - {c_example}")
        send_gui_command(EXPR_HAPPY, "I can help with many tasks! Try asking.")

    # --- System Commands ---
    elif "shutdown system" in command:
        speak("Are you absolutely sure you want to shut down your computer? Say 'yes' to confirm.", EXPR_CONCERNED); conf = listen()
        if "yes" in (conf or ""): speak("Okay, shutting down your computer in 5 seconds. Goodbye!", EXPR_SLEEPY); os.system("shutdown /s /t 5")
        else: speak("Shutdown cancelled. Phew!", EXPR_NEUTRAL)
    elif "restart system" in command:
        speak("Are you sure you want to restart your computer? Say 'yes'.", EXPR_CONCERNED); conf = listen()
        if "yes" in (conf or ""): speak("Okay, restarting your computer in 5 seconds.", EXPR_NEUTRAL); os.system("shutdown /r /t 5")
        else: speak("Restart cancelled.", EXPR_NEUTRAL)

    # --- Exit ---
    elif "exit" in command or "stop" in command or "goodbye" in command:
        speak("Goodbye! It was a pleasure assisting you. Have a wonderful day!", EXPR_SMILING); time.sleep(0.5)
        return "exit_signal"

    # --- Fallback to Local AI ---
    else:
        if TRANSFORMERS_AVAILABLE:
            if LOCAL_AI_PIPELINE:
                response_ai = ask_local_model(command)
                speak(response_ai if response_ai else "I'm not sure how to respond to that.", EXPR_TALKING)
            else: speak("My local AI brain is still warming up or had an issue. Please try specific commands or wait a moment.", EXPR_CONCERNED)
        else: speak("I can only handle specific commands right now as my advanced AI module isn't installed.", EXPR_SAD)

    send_gui_command(EXPR_NEUTRAL, "") # Default GUI state after command if not set otherwise
    return current_user_state # Return current user state

# --- Assistant Setup and Main Loop Orchestration ---
def assistant_setup():
    """One-time setup for the assistant: loads models, greets user."""
    global current_user_state
    send_gui_command(EXPR_NEUTRAL, "Loki is waking up...")
    initialize_local_ai_model() # Load Hugging Face model (can take time)

    if load_known_faces(): # Load face recognition data
        # Attempt camera-based recognition
        recognized_name_cam = recognize_face_from_cam() # This shows a CV2 window
        if recognized_name_cam:
            current_user_state = recognized_name_cam
            save_name(current_user_state) # Remember recognized user
            speak(f"Hello {current_user_state}, it's great to see your face!", EXPR_HAPPY)
        else: # No face recognized by camera, try loading from memory
            current_user_state = load_name()
            if current_user_state:
                speak(f"Hi {current_user_state}, welcome back!", EXPR_HAPPY)
            else: # No saved name either
                speak("Hello! I'm Loki. To get to know you better, you can tell me your name by saying 'my name is ...'", EXPR_NEUTRAL)
    else: # Failed to load known faces data
        speak("There was an issue with setting up face recognition. We can still chat!", EXPR_SAD)
        current_user_state = load_name() # Try loading name from memory anyway
        if current_user_state:
            speak(f"Hi {current_user_state}, let's get started!", EXPR_HAPPY)
        else:
            speak("Hello! I'm Loki. How can I assist you today?", EXPR_NEUTRAL)
    
    final_greeting = f"Hi {current_user_state}!" if current_user_state else "Hi there! How can I help?"
    send_gui_command(EXPR_NEUTRAL, final_greeting) # Set initial GUI message

def assistant_main_cycle():
    """Performs one full cycle of listening, processing, and responding."""
    global current_user_state
    command_heard = listen() # listen() updates GUI
    if command_heard:
        return process_command(command_heard) # process_command() updates GUI and returns signal or user state
    return None # No command heard, continue loop

def robot_logic_thread_function(stop_event: threading.Event):
    """Target function for the robot's logic thread."""
    print("Robot Thread: Initializing assistant logic...")
    try:
        assistant_setup()
        while not stop_event.is_set():
            signal = assistant_main_cycle()
            if signal == "exit_signal":
                print("Robot Thread: Exit signal received from assistant logic."); break
            if stop_event.is_set(): # Check if main GUI thread requested stop
                print("Robot Thread: Stop event detected from main thread."); break
            time.sleep(0.05) # Brief pause to yield CPU if listen() returns very quickly
    except Exception as e:
        print(f"Robot Thread: UNHANDLED EXCEPTION: {e}")
        traceback.print_exc() # Print full traceback for debugging
    finally:
        print("Robot Thread: Shutting down assistant logic...")
        send_gui_command(EXPR_SLEEPY, "Loki is going offline...")
        if GUI_COMMAND_QUEUE: # Try to send a quit signal to GUI if robot thread is exiting first
            try: GUI_COMMAND_QUEUE.put_nowait({"type": "system", "action": "quit"})
            except queue.Full: pass
        time.sleep(1) # Allow GUI to show final message

# --- Main Application Entry Point ---
if __name__ == "__main__":
    print("Main App: Loki Voice Assistant with GUI starting...")
    # 1. Create communication queue (Robot Logic Thread -> GUI Main Thread)
    shared_gui_command_queue = queue.Queue(maxsize=50) # Increased maxsize

    # 2. Provide this queue to the robot module (for send_gui_command)
    set_global_gui_queue(shared_gui_command_queue)

    # 3. Event to signal robot logic thread to stop
    robot_thread_stop_event = threading.Event()

    # 4. Start Robot Logic in a separate thread
    print("Main App: Launching Robot Logic Thread...")
    assistant_thread = threading.Thread(
        target=robot_logic_thread_function,
        args=(robot_thread_stop_event,),
        daemon=True # Thread will exit if main program exits
    )
    assistant_thread.start()

    # 5. Initialize and Run Pygame GUI in the Main Thread
    gui_instance = None
    print("Main App: Initializing and running Robot Face GUI...")
    try:
        gui_instance = RobotFaceGUI(command_queue=shared_gui_command_queue)
        gui_instance.run_gui_loop() # This is blocking; runs until GUI window is closed
    except Exception as e:
        print(f"Main App: CRITICAL ERROR in GUI execution: {e}")
        traceback.print_exc()
    finally:
        print("Main App: GUI loop has finished or an error occurred.")
        
        # Signal the robot logic thread to stop
        print("Main App: Signaling robot logic thread to stop...")
        robot_thread_stop_event.set()
        
        # Wait for the robot logic thread to complete its shutdown
        if assistant_thread.is_alive():
            print("Main App: Waiting for robot logic thread to join...")
            assistant_thread.join(timeout=7.0) # Increased timeout
            if assistant_thread.is_alive():
                print("Main App: Robot logic thread did not shut down cleanly (timed out).")
            else:
                print("Main App: Robot logic thread joined successfully.")
        else:
            print("Main App: Robot logic thread was already finished.")
            
        print("Main App: Application shutdown complete.")
