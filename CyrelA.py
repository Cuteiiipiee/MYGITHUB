import speech_recognition as sr
import wikipedia
import time
import tempfile
from gtts import gTTS
import pygame
import random
import os
import pyttsx3
import difflib

# === Predefined AI responses ===
smart_responses = {
    "how are you": [
        "I'm doing great, thanks for asking! How about you?",
        "Feeling awesome and ready to help you!",
        "Just living the AI life, always learning."
    ],
    "who are you": [
        "I’m your intelligent voice assistant, always here for you.",
        "Just a friendly AI trying to make your day easier.",
        "I’m like Wikipedia’s cool cousin with extra brains!"
    ],
    "hello": [
        "Hey there! Nice to hear your voice.",
        "Hello human! What's on your mind today?",
        "Hi! Ready when you are."
    ],
    "joke": [
        "Why don’t scientists trust atoms? Because they make up everything!",
        "I tried to catch fog yesterday… Mist!",
        "Parallel lines have so much in common. It’s a shame they’ll never meet."
    ]
}

# === Setup audio ===
pygame.mixer.init()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)  # pick a different one if available
engine.setProperty('rate', 170)  # speaking speed

def say(text):
    """Speak text using gTTS if online, fallback to pyttsx3 offline."""
    print(f"Speaking: {text}")
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            temp_file = f.name
        tts.save(temp_file)

        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        os.unlink(temp_file)
    except Exception as e:
        print(f"[Offline TTS Fallback] {e}")
        engine.say(text)
        engine.runAndWait()

# === Setup recognizer ===
rec = sr.Recognizer()

# === Short memory ===
history = []

# === Smart response with fuzzy matching ===
def ai_response(cmd):
    keys = list(smart_responses.keys())
    match = difflib.get_close_matches(cmd, keys, n=1, cutoff=0.5)
    if match:
        key = match[0]
        return random.choice(smart_responses[key])
    return None

# === Introduction (once only) ===
say("Hello! I'm your smart AI assistant. You can ask me anything, or say exit to quit.")

# === Main loop ===
while True:
    try:
        with sr.Microphone() as mic:
            print("Listening...")
            rec.adjust_for_ambient_noise(mic, 1)
            audio = rec.listen(mic, timeout=5, phrase_time_limit=10)

            print("Processing...")
            cmd = rec.recognize_google(audio).lower().strip()
            print(f"You said: {cmd}")

            # Exit command
            if "exit" in cmd or "quit" in cmd:
                say("Goodbye! Talk to you soon.")
                print("Exiting...")
                break

            # Smart response first
            ans = ai_response(cmd)
            if not ans:
                try:
                    ans = wikipedia.summary(cmd, sentences=2)
                except wikipedia.exceptions.DisambiguationError as e:
                    options = ", ".join(e.options[:3])
                    ans = f"That could mean: {options}. Can you be more specific?"
                except wikipedia.exceptions.PageError:
                    ans = "Sorry, I couldn't find information about that."

            print(f"AI says: {ans}")
            say(ans)

            # Keep last 5 interactions
            history.append((cmd, ans))
            if len(history) > 5:
                history.pop(0)

    except sr.UnknownValueError:
        say("Sorry, I didn’t catch that. Please repeat.")
    except sr.RequestError as e:
        say(f"Network error: {e}")
