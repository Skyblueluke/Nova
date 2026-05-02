import speech_recognition as sr
import win32com.client
import webbrowser
import os
import re
from datetime import datetime
import time

# =========================
# VOICE ENGINE
# =========================
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    print("NOVA:", text)
    speaker.Rate = -1
    speaker.Volume = 100
    speaker.Speak(text)

# =========================
# MEMORY STATE
# =========================
memory = {
    "last_app": None,
    "last_site": None,
    "last_query": None,
    "last_action": None
}

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

uk_sites = {
    "amazon": "https://www.amazon.co.uk",
    "ebay": "https://www.ebay.co.uk",
    "bbc": "https://www.bbc.co.uk",
    "bbcnews": "https://www.bbc.co.uk/news",
    "google": "https://www.google.co.uk",
    "youtube": "https://www.youtube.com"
}

# =========================
# INPUT
# =========================
def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 0.8
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return ""

# =========================
# CLEANER (NLU PREPROCESSOR)
# =========================
def clean(text):
    text = text.lower()

    fillers = [
        "can you", "could you", "please", "hey", "nova",
        "for me", "just", "would you", "sir", "now"
    ]

    for f in fillers:
        text = text.replace(f, "")

    return " ".join(text.split())

# =========================
# INTENT DETECTION
# =========================
def get_intent(text):

    if "repeat" in text or "again" in text:
        return "repeat"

    if "youtube" in text and "search" in text:
        return "youtube_search"

    if "youtube" in text:
        return "youtube"

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
# ENTITY EXTRACTION
# =========================
def extract_target(text, keyword):
    return text.replace(keyword, "").strip()

# =========================
# EXECUTION ENGINE
# =========================
def execute(text):

    intent = get_intent(text)

    # ---------- OPEN ----------
    if intent == "open":
        return handle_open(text)

    # ---------- YOUTUBE SEARCH ----------
    if intent == "youtube_search":
        query = extract_target(text, "youtube")
        query = extract_target(query, "search")

        memory["last_query"] = query

        speak(f"Searching YouTube for {query}, sir.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

        memory["last_action"] = "youtube_search"
        return True

    # ---------- YOUTUBE ----------
    if intent == "youtube":
        speak("Opening YouTube, sir.")
        webbrowser.open("https://www.youtube.com")

        memory["last_site"] = "youtube"
        memory["last_action"] = "youtube"
        return True

    # ---------- SEARCH ----------
    if intent == "search":
        query = extract_target(text, "search")

        speak(f"Searching for {query}, sir.")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    # ---------- TIME ----------
    if intent == "time":
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}, sir.")
        return True

    # ---------- IDENTITY ----------
    if intent == "identity":
        speak("I am NOVA, your neural operating virtual assistant.")
        return True

    # ---------- UNKNOWN ----------
    return False

# =========================
# OPEN HANDLER
# =========================
def handle_open(text):

    target = extract_target(text, "open")

    noise = ["for", "me", "please", "the", "a", "an", "could", "you", "just"]
    words = target.split()
    words = [w for w in words if w not in noise]

    target = "".join(words)

    if len(target) < 2:
        speak("I didn't catch that properly, sir.")
        return True

    # ---------- APP ----------
    for app in apps:
        if app in target:
            speak(f"Opening {app}, sir.")
            os.startfile(apps[app])

            memory["last_app"] = app
            memory["last_action"] = "open_app"
            return True

    # ---------- SITE ----------
    site = re.sub(r"[^a-z0-9]", "", target)

    url = uk_sites.get(site, f"https://www.{site}.com")

    speak(f"Opening {site}, sir.")
    webbrowser.open(url)

    memory["last_site"] = site
    memory["last_action"] = "open_site"
    return True

# =========================
# MAIN LOOP
# =========================
speak("NOVA core v3 online.")

while True:

    raw = listen()
    if not raw:
        continue

    text = clean(raw)

    if "stop" in text:
        speak("Shutting down, sir.")
        break

    success = execute(text)

    if not success:
        speak("I couldn't process that request, sir.")

    time.sleep(0.3)
