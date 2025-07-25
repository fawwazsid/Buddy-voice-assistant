import os
import threading
import webbrowser
import datetime
import time
import speech_recognition as sr
import pyttsx3
import requests
import openai
import re
import pytz
import json
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import cv2
import pyautogui
import ctypes
import subprocess
import difflib
import re
WAKE_WORDS = ["buddy", "hey buddy", "hello buddy"]
# ----------------- API KEYS -----------------
openai.api_key = "add your api key"
openai.api_base = "https://openrouter.ai/api/v1"
serpapi_api_key = "add your serpapi keys"
STABILITY_API_KEY = "add your stability api key"

# ----------------- Text-to-Speech -----------------
engine = pyttsx3.init()
voices = engine.getProperty("voices")
for voice in voices:
    if "male" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break

def speak(text):
    print("Buddy:", text)
    threading.Thread(target=_speak_thread, args=(text,), daemon=True).start()

def _speak_thread(text):
    engine.say(text)
    engine.runAndWait()

def clean_text(text):
    text = re.sub(r"[#*_`~>\[\]()]", "", text)
    text = re.sub(r"\n+", ". ", text)
    return text.strip()
# ----------------- Wake word -----------------
def wait_for_wake_word():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Waiting for wake word...")
        audio = r.listen(source, timeout=None, phrase_time_limit=5)
        try:
            trigger_text = r.recognize_google(audio)
            print("You said (wake):", trigger_text)
            for word in WAKE_WORDS:
                if word.lower() in trigger_text.lower():
                    return True
        except sr.UnknownValueError:
            pass  # Unrecognized speech
        except sr.RequestError as e:
            print("Wake word recognition error:", e)
    return False
def respond_to_wake_word():
    engine.setProperty("volume", 1.0)
    speak("Hmm") 
# ----------------- Listening -----------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source, timeout=20, phrase_time_limit=10)
        try:
            command = r.recognize_google(audio)
            print("You said:", command)
            return command.lower()
        except:
            try:
                speak("Sorry, could you repeat that?")
            except:
                pass
            return ""
def smart_match(command, keywords):
    for key in keywords:
        if key in command:
            return key
        # Try fuzzy match
        matches = difflib.get_close_matches(key, command.split(), cutoff=0.7)
        if matches:
            return key
    return None 
def open_application_via_search(app_name):
    try:
        speak(f"Opening {app_name}")
        pyautogui.hotkey('win')
        time.sleep(1)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(1)
        pyautogui.press('enter')
    except Exception as e:
        speak(f"Sorry, I couldn't open {app_name}")       

# ----------------- Search Logs -----------------
def log_search(term):
    try:
        with open("search_history.json", "a", encoding="utf-8") as f:
            json.dump({"search": term, "timestamp": str(datetime.datetime.now())}, f)
            f.write("\n")
    except:
        pass

# ----------------- AI Text (LLM) -----------------
def ask_llm(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Sorry, I couldn't get an answer from the AI."

# ----------------- Real-Time Search (SerpAPI) -----------------
def serp_search(query):
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": serpapi_api_key
        }
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        if "answer_box" in data:
            return data["answer_box"].get("snippet") or data["answer_box"].get("answer", "")
        if "organic_results" in data and data["organic_results"]:
            return data["organic_results"][0].get("snippet", "Here's something I found.")
        return "Sorry, I couldn't find anything relevant."
    except Exception as e:
        return f"SerpAPI error: {e}"

# ----------------- AI Image Generation -----------------
def generate_image(prompt, output_path="generated_image.png"):
    import base64

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json",
    }
    files = {
        'prompt': (None, prompt),
        'model': (None, 'stable-diffusion-xl-v1'),
        'output_format': (None, 'png'),
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        result = response.json()

        if "image" in result:
            image_data = base64.b64decode(result["image"])
            with open(output_path, "wb") as f:
                f.write(image_data)
            speak("Image generated successfully.")
            os.startfile(output_path)
        else:
            speak("Image generation failed. No image in response.")
    except requests.exceptions.HTTPError as http_err:
        print("HTTP error:", http_err)
        print("Response:", response.text)
        speak("There was a problem with the image generation request.")
    except Exception as e:
        print("Image generation error:", e)
        speak("Error generating image.")        
IMAGE_TRIGGER_PHRASES = [
    "generate image of",
    "create image of",
    "draw",
    "make image of",
    "visualize"
]
# ----------------- Helper Functions -----------------
def open_camera_only():
    try:
        speak("Opening camera.")
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            speak("Unable to access the camera.")
            return

        ret, frame = cam.read()
        if ret:
            speak("Camera is working.")
        else:
            speak("Failed to capture from camera.")
        cam.release()

    except Exception as e:
        speak(f"Error opening camera: {str(e)}")
def open_camera_and_capture():
    try:
        speak("Capturing photo.")
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            speak("Unable to access the camera.")
            return

        ret, frame = cam.read()
        if not ret:
            speak("Failed to capture image.")
            return

        img_name = "captured_photo.jpg"
        cv2.imwrite(img_name, frame)
        cam.release()
        speak("Photo captured successfully.")
        os.startfile(img_name)

    except Exception as e:
        speak(f"Error capturing image: {str(e)}")


def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol_range = volume.GetVolumeRange()
    min_vol, max_vol = vol_range[0], vol_range[1]
    new_vol = min_vol + (level / 100) * (max_vol - min_vol)
    volume.SetMasterVolumeLevel(new_vol, None)

def get_city_time(city_name):
    city_map = {
        "hyderabad": "Asia/Kolkata", "mumbai": "Asia/Kolkata", "delhi": "Asia/Kolkata", "chennai": "Asia/Kolkata",
        "bangalore": "Asia/Kolkata", "kolkata": "Asia/Kolkata", "pune": "Asia/Kolkata",
        "new york": "America/New_York", "los angeles": "America/Los_Angeles", "chicago": "America/Chicago",
        "houston": "America/Chicago", "seattle": "America/Los_Angeles", "washington": "America/New_York",
        "london": "Europe/London", "paris": "Europe/Paris", "berlin": "Europe/Berlin", "madrid": "Europe/Madrid",
        "rome": "Europe/Rome", "moscow": "Europe/Moscow", "tokyo": "Asia/Tokyo", "seoul": "Asia/Seoul",
        "beijing": "Asia/Shanghai", "shanghai": "Asia/Shanghai", "hong kong": "Asia/Hong_Kong",
        "singapore": "Asia/Singapore", "dubai": "Asia/Dubai", "sydney": "Australia/Sydney",
        "toronto": "America/Toronto", "johannesburg": "Africa/Johannesburg", "cairo": "Africa/Cairo",
        "karachi": "Asia/Karachi", "dhaka": "Asia/Dhaka", "colombo": "Asia/Colombo"
    }
    try:
        key = city_name.lower().strip()
        if key in city_map:
            tz = pytz.timezone(city_map[key])
            now = datetime.datetime.now(tz)
            return f"The time in {city_name.title()} is {now.strftime('%I:%M %p')}."
        else:
            return "City not recognized."
    except:
        return "Could not get time."

def set_timer(minutes):
    speak(f"Timer set for {minutes} minutes.")
    time.sleep(minutes * 60)
    speak("Time's up!")

def shutdown_computer():
    speak("Shutting down.")
    os.system("shutdown /s /t 5")

def search_files(filename):
    speak(f"Searching for {filename}.")
    matches = []
    for root, dirs, files in os.walk("C:/"):
        if filename.lower() in [f.lower() for f in files]:
            matches.append(os.path.join(root, filename))
    if matches:
        speak(f"Found {len(matches)}. Opening first.")
        os.startfile(matches[0])
    else:
        speak("No file found.")

def youtube_search(query):
    log_search(query)
    speak(f"Searching YouTube for {query}.")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
def youtube_play(query):
    log_search(query)
    speak(f"Playing {query} on YouTube")
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        response = requests.get(url)
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        if video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            webbrowser.open(video_url)
        else:
            speak("Sorry, I couldn't find a relevant video.")
    except Exception as e:
        speak("There was a problem accessing YouTube.")
        print("YouTube search error:", e)
 

# ----------------- Core Task Logic -----------------
def perform_task(command):
    command = command.lower()

    # --- Smart Match Image Generation ---
    if smart_match(command, ["generate image", "create image", "draw", "make image", "visualize"]):
        prompt = next((command.split(phrase)[-1].strip() for phrase in IMAGE_TRIGGER_PHRASES if phrase in command), "")
        if prompt:
            speak(f"Generating image of {prompt}")
            generate_image(prompt)
        else:
            speak("Please describe what you want me to create.")
        return

    # --- Time ---
    if smart_match(command, ["time in", "current time in", "what time in"]):
        city = command.split("in")[-1].strip()
        speak(get_city_time(city))
        return

    # --- Volume ---
    if smart_match(command, ["set volume", "volume", "lower volume", "reduce volume", "increase volume"]):
        level_match = re.findall(r"\d{1,3}", command)
        if level_match:
            level = int(level_match[0])
            set_volume(level)
            speak(f"Volume set to {level} percent.")
        else:
            speak("Please say a volume level between 0 and 100.")
        return

    # --- Weather ---
    if smart_match(command, ["weather", "temperature", "forecast"]):
        city = command.split("in")[-1].strip() if "in" in command else ""
        if city:
            try:
                result = requests.get(f"http://wttr.in/{city}?format=3").text.strip()
                speak(result)
            except:
                speak("Couldn't fetch weather.")
        else:
            speak("Please mention a city for weather.")
        return

    # --- YouTube ---
    if "open youtube" in command:
        speak("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return
    if smart_match(command, ["play music", "play song", "play", "play audio", "play sound"]):
        # Extract query after 'play' (e.g., play relaxing music)
        query = command.replace("play", "").replace("music", "").replace("song", "").strip()
        if not query:
            query = "music"
        youtube_play(query)
        return

    if smart_match(command, ["search on youtube", "youtube search", "search on youtube for"]):
        search_term = command.replace("search", "").replace("on youtube", "").strip()
        if not search_term:
            speak("What should I search on YouTube?")
            return
        youtube_search(search_term)
        return
    # --- System Control Commands ---
    if "restart my pc" in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 5")
        return

    if "shutdown pc" in command or "shutdown" in command or "shut down pc" in command:
        shutdown_computer()
        return

    if "put pc to sleep" in command:
        speak("Putting system to sleep.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return

    if "lock my pc" in command:
        speak("Locking the computer.")
        ctypes.windll.user32.LockWorkStation()
        return

    if "logout" in command or "sign out" in command:
        speak("Logging out.")
        os.system("shutdown -l")
        return
    # --- Generic App Open Logic ---
    if command.startswith("open "):
        app_name = command.replace("open", "").strip()
        open_application_via_search(app_name)
        return

    # --- Multimedia and Screenshot ---
    if "mute volume" in command:
        pyautogui.press("volumemute")
        speak("Volume muted.")
        return

    if "volume up" in command:
        pyautogui.press("volumeup")
        speak("Volume increased.")
        return

    if "volume down" in command:
        pyautogui.press("volumedown")
        speak("Volume decreased.")
        return

    if "take a screenshot" in command:
        path = os.path.join(os.getcwd(), "screenshot.png")
        pyautogui.screenshot(path)
        speak("Screenshot taken.")
        os.startfile(path)
        return

    # --- Camera ---
    if "open camera and capture" in command or "take a photo" in command or "click a photo" in command or "take photo" in command:
        open_camera_and_capture()
        return
    # --- Timer ---
    if "set a timer for" in command:
        match = re.search(r"(\d+)\s*(second|seconds|minute|minutes)?", command)
    if match:
        value = int(match.group(1))
        unit = match.group(2) or "minutes"

        if "second" in unit:
            seconds = value
            speak(f"Timer set for {seconds} seconds.")
            time.sleep(seconds)
            speak("Time's up!")
        else:
            minutes = value
            speak(f"Timer set for {minutes} minutes.")
            time.sleep(minutes * 60)
            speak("Time's up!")
    else:
        speak("I couldn't understand the timer duration.")
        return


    # --- File Search ---
    if "search file" in command:
        filename = command.replace("search file", "").strip()
        search_files(filename)
        return

    # --- Final AI / Real-time Fallback ---
    log_search(command)

    realtime_keywords = [
        "who is","today", "yesterday", "recent", "latest", "breaking", "now",
        "news", "headlines", "update", "happened", "crash", "accident",
        "earthquake", "weather today", "temperature now", "score", "result", "who won"
    ]

    if any(kw in command.lower() for kw in realtime_keywords):
        speak("Let me check real-time sources...")
        serp_result = serp_search(command)
        speak(clean_text(serp_result))
    else:
        ai_reply = ask_llm(command)
        if any(x in ai_reply.lower() for x in [
            "i'm a language model", "knowledge cutoff", "i don't have access", "as of my knowledge"
        ]):
            speak("Let me find real-time info...")
            serp_result = serp_search(command)
            speak(clean_text(serp_result))
        else:
            speak(clean_text(ai_reply))


# ----------------- Greet & Run -----------------
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning! I'm Buddy.")
    elif hour < 18:
        speak("Good afternoon! I'm Buddy.")
    else:
        speak("Good evening! I'm Buddy.")

if __name__ == "__main__":
    greet_user()
    while True:
        if wait_for_wake_word():
            cmd = listen()
            if cmd:
                if "exit" in cmd or "bye" in cmd:
                    speak("Goodbye!")
                    break
                perform_task(cmd)