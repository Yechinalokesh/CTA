import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from vyomax_gui import VyomaxGUI
import threading

# Configure Gemini API
genai.configure(api_key="AIzaSyDk_lFU3yTW9UQ8qqnHqFSyTP6axFas2NU")
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Initialize GUI on main thread
gui = VyomaxGUI()

# Setup TTS engine globally
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    def run():
        gui.switch_face("talking")
        engine.say(text)
        engine.runAndWait()
        gui.switch_face("idle")
    threading.Thread(target=run, daemon=True).start()

def chat_with_ai(question):
    gui.switch_face("thinking")
    try:
        response = model.generate_content(question)
        reply = response.text
    except Exception as e:
        reply = "Oops, Vyomax had a brain freeze!"
    return reply

def listen_and_respond():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            print("🎙️ Listening...")
            gui.switch_face("thinking")
            audio = r.listen(source)
            try:
                query = r.recognize_google(audio)
                print("You said:", query)
            except:
                print("Didn't catch that.")
                continue

            if "exit" in query.lower():
                speak("Goodbye Lokesh!")
                break
            if query:
                response = chat_with_ai(query)
                print("Vyomax:", response)
                speak(response)

# Start your listening loop in a background thread
listener_thread = threading.Thread(target=listen_and_respond, daemon=True)
listener_thread.start()

# Start the Tkinter mainloop on the main thread — IMPORTANT
gui.run()  # <-- This calls self.window.mainloop() inside VyomaxGUI.run()
