import speech_recognition as sr
import win32com.client
import time
import random
import webbrowser
from datetime import datetime
import os
import re

# =========================
# VOICE ENGINE
# =========================
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    print("NOVA:", text)

    voices = speaker.GetVoices()
    if voices.Count > 1:
        speaker.Voice = voices.Item(1)

    speaker.Rate = -1
    speaker.Volume = 100
    speaker.Speak(text)


# =========================
# MEMORY (CONTEXT STATE)
# =========================
memory = {
    "last_app": None,
    "last_site": None,
    "last_query": None
}


# =========================
# SPEECH INPUT
# =========================
def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 0.8
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You:", command)
        return command
    except:
        return ""


# =========================
# STARTUP
# =========================
speak("Hello sir. NOVA online. How can I assist you today?")


# =========================
# APPS
# =========================
apps = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "spotify": r"C:\Users\skybl\AppData\Roaming\Spotify\Spotify.exe",
    "notepad": "notepad",
    "calculator": "calc",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE"
}


# =========================
# CLEAN INPUT
# =========================
def clean(text):
    text = text.lower()

    fillers = [
        "can you", "could you", "please", "hey", "nova",
        "for me", "just", "would you", "i want you to",
        "sir", "now"
    ]

    for f in fillers:
        text = text.replace(f, "")

    return " ".join(text.split())


# =========================
# INTENT DETECTION
# =========================
def get_intent(text):

    if any(x in text for x in ["again", "repeat", "do that"]):
        return "repeat"

    if "youtube" in text and "search" in text:
        return "youtube_search"

    if "youtube" in text or "music" in text:
        return "youtube_search"

    if "open" in text:
        return "open"

    if "search" in text:
        return "search"

    if "time" in text:
        return "time"

    if "your name" in text:
        return "identity"

    return "unknown"


# =========================
# EXECUTION
# =========================
def execute(command):

    intent = get_intent(command)

    # ---------- OPEN ----------
    if intent == "open":
        return handle_open(command)

    # ---------- YOUTUBE SEARCH ----------
    elif intent == "youtube_search":
        query = command

        for word in ["youtube", "search", "for", "on", "please"]:
            query = query.replace(word, "")

        query = query.strip()

        memory["last_query"] = query

        speak(f"Searching YouTube for {query}, sir.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True

    # ---------- YOUTUBE ----------
    elif intent == "youtube":
        speak("Opening YouTube, sir.")
        webbrowser.open("https://www.youtube.com")
        memory["last_site"] = "youtube"
        return True

    # ---------- GOOGLE SEARCH ----------
    elif intent == "search":
        query = command.replace("search", "").strip()

        speak(f"Searching for {query}, sir.")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    # ---------- TIME ----------
    elif intent == "time":
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}, sir.")
        return True

    # ---------- IDENTITY ----------
    elif intent == "identity":
        speak("I am NOVA, your neural operating virtual assistant.")
        return True

    # ---------- REPEAT ----------
    elif intent == "repeat":

        if memory["last_query"]:
            speak(f"Repeating YouTube search for {memory['last_query']}, sir.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={memory['last_query']}")
            return True

        if memory["last_site"]:
            speak(f"Opening {memory['last_site']} again, sir.")
            webbrowser.open(f"https://www.{memory['last_site']}.com")
            return True

        if memory["last_app"]:
            speak(f"Reopening {memory['last_app']}, sir.")
            os.startfile(apps[memory["last_app"]])
            return True

        speak("I have nothing to repeat, sir.")
        return True

    return False


# =========================
# OPEN HANDLER
# =========================
def handle_open(text):

    target = text.lower()

    noise_words = [
        "open", "for", "me", "please", "the", "a", "an",
        "could", "you", "just", "and", "now", "sir"
    ]

    words = target.split()
    words = [w for w in words if w not in noise_words]

    target = "".join(words)

    # ---------- SAFETY CHECK ----------
    if len(target) < 3:
        speak("I didn't catch the website properly, sir.")
        return True

    # ---------- APP CHECK ----------
    for app in apps:
        if app in target:
            speak(f"Opening {app}, sir.")
            os.startfile(apps[app])
            memory["last_app"] = app
            return True

    # ---------- CLEAN SITE ----------
    site = re.sub(r"[^a-z0-9]", "", target)

    uk_sites = {
        "amazon": "https://www.amazon.co.uk",
        "ebay": "https://www.ebay.co.uk",
        "bbc": "https://www.bbc.co.uk",
        "bbcnews": "https://www.bbc.co.uk/news",
        "google": "https://www.google.co.uk",
        "youtube": "https://www.youtube.com"
    }

    url = uk_sites.get(site, f"https://www.{site}.com")

    speak(f"Opening {site}, sir.")
    webbrowser.open(url)

    memory["last_site"] = site
    return True


# =========================
# MAIN LOOP
# =========================
while True:

    raw = listen()
    if not raw:
        continue

    text = clean(raw)

    if "stop" in text:
        speak("Shutting down, sir. Have a great day.")
        break

    success = execute(text)

    if not success:
        speak("I'm not sure how to help with that yet, sir.")

    time.sleep(0.5)
