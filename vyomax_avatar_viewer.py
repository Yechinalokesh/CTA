# Step C.1: Import necessary libraries
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import pyttsx3
import speech_recognition as sr
import threading
import requests
import os 
import time 

# Step C.2: Setup Text-to-Speech Engine
engine = pyttsx3.init()

# Optional: You can try to set a specific voice if you want
# voices = engine.getProperty('voices')
# For example, to use the first available voice:
# engine.setProperty('voice', voices[0].id) 
# To use the second (if it exists, often a female voice on Windows):
# if len(voices) > 1:
#    engine.setProperty('voice', voices[1].id)
# engine.setProperty('rate', 160) # You can adjust speech rate (words per minute)

def speak(text):
    """Makes Nova speak the given text."""
    print(f"Nova: {text}") 
    engine.say(text)
    engine.runAndWait()

# Step C.3: Function to Interact with Ollama (Nova's Brain)
def ask_ollama(prompt):
    """Sends a prompt to the Ollama API and gets a response."""
    ollama_api_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3", # Make sure you have 'llama3' pulled in Ollama (ollama pull llama3)
        "prompt": prompt,
        "stream": False # Keeps it simple for now
    }
    try:
        print(f"User (to Ollama): {prompt}") 
        # Timeout added for robustness
        response = requests.post(ollama_api_url, json=payload, timeout=60) # 60 seconds timeout
        response.raise_for_status() 
        
        response_data = response.json()
        full_response = response_data.get("response", "").strip()
        
        return full_response
    except requests.exceptions.Timeout:
        print("Error: Connection to Ollama timed out.")
        return "Sorry, my connection to my thinking brain timed out. Please try again."
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return "I'm having trouble connecting to my brain right now. Please make sure Ollama is running with the llama3 model."
    except Exception as e:
        print(f"Error processing Ollama response: {e}")
        return "Sorry, I encountered an issue while thinking."

# Step C.4: Function to Listen to Your Voice and Reply
def listen_and_reply():
    """Listens for voice input, processes it, and generates a spoken reply."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Adjust for ambient noise to improve recognition
        # recognizer.adjust_for_ambient_noise(source, duration=0.5) 
        
        speak("I'm listening, Lokesh.") 
        status_label.config(text="Listening...") 
        window.update_idletasks() 

        try:
            print("Mic check: Listening for audio...")
            # Increased timeout slightly, phrase_time_limit can be longer
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15) 
            status_label.config(text="Processing...")
            window.update_idletasks()
            print("Mic check: Audio captured, now recognizing...")

            command = recognizer.recognize_google(audio) 
            print(f"You said: {command}")
            status_label.config(text=f"You said: {command[:35]}...") 
            window.update_idletasks()

            if command:
                # Make Nova "think" before replying to add a slight dramatic pause
                think_time_start = time.time()
                reply_from_ollama = ask_ollama(command)
                think_time_end = time.time()
                print(f"Ollama took {think_time_end - think_time_start:.2f} seconds to respond.")
                
                if reply_from_ollama: # Make sure we got a reply
                    speak(reply_from_ollama)
                else: # If Ollama returned an empty string for some reason
                    speak("I thought about it, but I don't have a specific response for that.")
            else: # Should not happen if recognize_google succeeds
                speak("I didn't quite catch that, could you say it again?")

        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Could you please try speaking again?")
            print("No speech detected within timeout.")
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand what you said. Can you try rephrasing?")
            print("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            speak("Hmm, I'm having trouble reaching my speech understanding service. Please check your internet connection.")
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            speak("Oh dear, an unexpected hiccup occurred while I was listening.")
            print(f"An unexpected error in listen_and_reply: {e}")
        finally:
            # Reset status label after interaction
            status_label.config(text="Hi, I'm Nova! Click the button to talk.") 
            window.update_idletasks()


def start_listening_thread():
    """Starts the listening process in a new thread to keep GUI responsive."""
    talk_button.config(state=tk.DISABLED) # Disable button to prevent multiple clicks
    # Create a new thread that will run the 'listen_and_reply' function
    # 'daemon=True' means the thread will close when the main program closes
    listening_thread = threading.Thread(target=listen_and_reply, daemon=True)
    listening_thread.start()
    # We need a way to re-enable the button after the thread is done
    check_if_thread_is_done(listening_thread)

def check_if_thread_is_done(thread_to_check):
    """Checks if the thread is still running. If not, re-enables the button."""
    if thread_to_check.is_alive():
        # If still running, check again after 100 milliseconds
        window.after(100, lambda: check_if_thread_is_done(thread_to_check))
    else:
        # If not running, re-enable the button
        talk_button.config(state=tk.NORMAL)
        status_label.config(text="Hi, I'm Nova! Click the button to talk.")
        print("Listening thread finished, button re-enabled.")


# Step C.5: Class for Animating the GIF
class AnimatedGIF(tk.Label):
    def __init__(self, master, path, size=(200, 200)): 
        self.master = master
        self.path = path
        self.size = size 
        self.frames = []
        self.delay = 100  
        self.idx = 0

        self._load_gif()
        
        # Important: Initialize the tk.Label part of this class AFTER frames are loaded
        if self.frames: # Only initialize if frames were loaded successfully
            super().__init__(master, image=self.frames[0], bg="black")
            self.after(self.delay, self._play) # Start animation
        else: # If frames list is empty (GIF loading failed)
            # Create a fallback label to show an error
            super().__init__(master, text="Error: GIF not loaded!", fg="red", bg="black", font=("Arial", 14))
            print(f"CRITICAL: AnimatedGIF class could not load frames for {self.path}")


    def _load_gif(self):
        try:
            im = Image.open(self.path)
            
            try:
                self.delay = im.info['duration']
                if self.delay == 0: # Some GIFs have 0 duration, use a default
                    self.delay = 100
            except KeyError:
                self.delay = 100 

            for i in range(im.n_frames):
                im.seek(i)
                frame_copy = im.copy().convert("RGBA") 
                resized_frame = frame_copy.resize(self.size, Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(resized_frame))
            print(f"Successfully loaded {len(self.frames)} frames from {self.path} with delay {self.delay}ms.")
                
        except FileNotFoundError:
            print(f"ERROR: GIF file not found at '{self.path}'. Make sure it's in the 'assets' folder.")
            self.frames = [] # Ensure frames list is empty on error
        except Exception as e:
            print(f"ERROR: Could not load GIF '{self.path}'. Reason: {e}")
            self.frames = [] # Ensure frames list is empty on error


    def _play(self):
        if not self.frames: 
            return # Stop if no frames
        try:
            self.config(image=self.frames[self.idx])
            self.idx = (self.idx + 1) % len(self.frames)
            self.after(self.delay, self._play)
        except tk.TclError as e:
            # This can happen if the window is closed while the animation is trying to update
            print(f"Tkinter error during animation (likely window closed): {e}")
        except Exception as e:
            print(f"Unexpected error in _play: {e}")


# Step C.6: Create the Main GUI Window only if this script is run directly
if __name__ == '__main__': 
    window = tk.Tk()
    window.title("Nova AI Companion - Lokesh's Project") # Personalized title
    window.geometry("800x600") 
    window.configure(bg="black") 

    # Step C.7: Load and Display the Animated GIF
    gif_path = "assets/nova.gif" # Path to your GIF
    nova_animation = AnimatedGIF(window, gif_path, size=(300,300)) # You can change (300,300)
    if nova_animation.frames: # Only pack if GIF loaded
        nova_animation.pack(pady=20) 
    else: # If GIF failed to load, show a message on the GUI
        error_label_gif = tk.Label(window, text=f"Could not load GIF from {gif_path}", fg="red", bg="black", font=("Arial", 12))
        error_label_gif.pack(pady=20)

    # Step C.8: Add a Status Label
    status_label = tk.Label(window, text="Initializing Nova...", fg="lime green", bg="black", font=("Arial", 16))
    status_label.pack(pady=10)

    # Step C.9: Add a Button to Start Talking
    talk_button = tk.Button(window, text="🎤 Talk to Nova", 
                            font=("Arial", 14, "bold"), 
                            bg="#4CAF50", fg="white",  
                            activebackground="#45a049", # Color when button is pressed
                            activeforeground="white",
                            padx=15, pady=10,          
                            relief=tk.RAISED,          
                            bd=3,                      
                            command=start_listening_thread)
    talk_button.pack(pady=20)

    # Step C.10: Initial Welcome Message from Nova (in a thread)
    def initial_greeting_task():
        time.sleep(1) # Wait a tiny bit for window to fully appear
        speak("Hello Lokesh! I am Nova, your personal AI companion. I'm online and ready when you are.")
        status_label.config(text="Hi, I'm Nova! Click the button to talk.")
    
    threading.Thread(target=initial_greeting_task, daemon=True).start()

    # Step C.11: Start the GUI Event Loop
    window.mainloop()
