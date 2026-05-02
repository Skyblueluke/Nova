import speech_recognition as sr
import win32com.client
import webbrowser
import os
import re
from datetime import datetime
import time
import random

# =========================
# VOICE ENGINE
# =========================
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    print("NOVA:", text)
    speaker.Rate = -1
    speaker.Volume = 100
    speaker.Speak(text)

acknowledgements = [
    "At once, sir.",
    "Understood.",
    "Right away.",
    "Processing your request.",
    "Certainly."
]

def jarvis_ack():
    speak(random.choice(acknowledgements))

# =========================
# MEMORY
# =========================
memory = {
    "last_app": None,
    "last_site": None,
    "last_query": None
}

# =========================
# APPS
# =========================
apps = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "spotify": r"C:\Users\skybl\AppData\Roaming\Spotify\Spotify.exe",
    "notepad": r"notepad",
    "calculator": r"calc",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE"
}

app_aliases = {
    "word": ["word", "document", "doc"],
    "excel": ["excel", "spreadsheet", "sheet"],
    "powerpoint": ["powerpoint", "power point", "slides", "presentation", "power"],
    "outlook": ["outlook", "email", "mail"],
    "chrome": ["chrome", "browser", "internet"],
    "spotify": ["spotify", "music"],
    "notepad": ["notepad", "notes"],
    "calculator": ["calculator", "calc"]
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
# CLEANING
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

def fix_speech_errors(text):
    corrections = {
        "mzon": "amazon",
        "amzon": "amazon",
        "amazn": "amazon",
        "tube": "youtube",
        "yotube": "youtube",
        "googl": "google"
    }

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    return text

def is_valid_command(text):
    if not text or not isinstance(text, str):
        return False

    text = text.strip()

    if len(text) < 3:
        return False

    if len(text.split()) == 1 and len(text) < 4:
        return False

    return True

# =========================
# INTENT
# =========================
def get_intent(text):

    if any(x in text for x in ["repeat", "again"]):
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

    return "unknown"

# =========================
# SITE RESOLUTION (FIXES YOUR BUG)
# =========================
def resolve_site(site):

    known = {
        "amazon": "https://www.amazon.co.uk",
        "ebay": "https://www.ebay.co.uk",
        "bbc": "https://www.bbc.co.uk",
        "google": "https://www.google.co.uk",
        "youtube": "https://www.youtube.com"
    }

    site = site.lower().strip()

    # exact match
    if site in known:
        return known[site]

    # fuzzy match (THIS FIXES "mzon" / "tube")
    for k in known:
        if k in site or site in k:
            return known[k]

    # safety fallback
    if len(site) < 4:
        return None

    return f"https://www.{site}.com"

# =========================
# HANDLERS
# =========================

def extract_target(text, keyword):
    return text.replace(keyword, "").strip()

def handle_open(text):

    target = extract_target(text, "open").lower()

    noise = ["for", "me", "please", "the", "a", "an", "could", "you", "just"]

    for n in noise:
        target = target.replace(f" {n} ", " ")

    target = target.strip()

    print("DEBUG target:", target)

    # ---------- APP MATCH ----------
    for app, aliases in app_aliases.items():
        for alias in aliases:
            if alias in target:
                print(f"DEBUG matched app: {app}")

                speak(f"Opening {app}, sir.")
                print("DEBUG apps keys:", apps.keys())
                print("DEBUG app requested:", app)
                os.startfile(apps[app])

                memory["last_app"] = app
                memory["last_action"] = "open_app"
                return True   # 🚨 CRITICAL

    # ---------- SITE MATCH ----------
    site = re.sub(r"[^a-z0-9]", "", target)

    url = resolve_site(site)

    if not url:
        speak("I couldn't identify the website properly, sir.")
        return True

    print(f"DEBUG opening site: {site}")

    speak(f"Opening {site}, sir.")
    webbrowser.open(url)

    memory["last_site"] = site
    memory["last_action"] = "open_site"

    return True

# =========================
# EXECUTION
# =========================
def execute(text):

    intent = get_intent(text)

    # ✅ ADD THIS BLOCK
    if intent in ["open", "youtube_search", "youtube", "search", "repeat"]:
        jarvis_ack()

    if intent == "open":
        return handle_open(text)

    if intent == "youtube_search":
        query = text.replace("youtube", "").replace("search", "").strip()

        speak(f"Searching YouTube for {query}, sir.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

        memory["last_query"] = query
        return True

    if intent == "youtube":
        speak("Opening YouTube, sir.")
        webbrowser.open("https://www.youtube.com")
        memory["last_site"] = "youtube"
        return True

    if intent == "search":
        query = text.replace("search", "").strip()

        speak(f"Searching for {query}, sir.")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    if intent == "time":
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}, sir.")
        return True

    if intent == "repeat":

        if memory["last_query"]:
            webbrowser.open(f"https://www.youtube.com/results?search_query={memory['last_query']}")
            speak("Repeating last search, sir.")
            return True

        if memory["last_site"]:
            webbrowser.open(resolve_site(memory["last_site"]))
            speak("Opening last site again, sir.")
            return True

        if memory["last_app"]:
            os.startfile(apps[memory["last_app"]])
            speak("Reopening last app, sir.")
            return True

        speak("Nothing to repeat, sir.")
        return True

    return False

# =========================
# MAIN LOOP (STABLE)
# =========================
speak("Hello sir, I am your neural operating virtual assistant, NOVA. How can I assist you today?")

while True:

    raw = listen()

    if not raw or not isinstance(raw, str):
        continue

    text = clean(raw)

    if not text:
        continue

    text = fix_speech_errors(text)

    if not is_valid_command(text):
        speak("I didn't catch that clearly, sir.")
        continue

    if "stop" in text:
        speak("Shutting down, sir. Have a great day!")
        break

    try:
        success = execute(text)
    except Exception as e:
        print("ERROR:", e)
        speak("Something went wrong, sir.")
        continue

    if not success:
        speak("I couldn't process that request, sir.")

    time.sleep(0.3)
