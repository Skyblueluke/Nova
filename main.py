import speech_recognition as sr
import win32com.client
import time
import random

# --- VOICE (WORKING SYSTEM) ---
speaker = win32com.client.Dispatch("SAPI.SpVoice")



def speak(text):
    print("NOVA:", text)

    voices = speaker.GetVoices()

    if voices.Count > 1:
        speaker.Voice = voices.Item(1)

    # Better balance
    speaker.Rate = -1   # slightly slow, not drunk
    speaker.Volume = 100

    # Remove artificial pauses (IMPORTANT)
    speaker.Speak(text)

# --- LISTEN ---
def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You:", command)
        return command
    except:
        return ""

# --- STARTUP ---
speak("Hello sir. I am your Neural Operating Virtual Assistant, or NOVA for short. How can I assist you today?")

acknowledgements = [
    "At once, sir.",
    "Understood.",
    "Right away.",
    "Processing your request.",
    "Certainly."
]

def jarvis_ack():
    speak(random.choice(acknowledgements))

# --- MAIN LOOP ---
while True:
    text = listen()

    if not text:
        continue

    if "stop" in text.lower():
        speak("Shutting down sir. Have a great day!")
        break

    jarvis_ack()
    speak(f"You said {text}, sir.")
    time.sleep(0.5)
