# 🧠 Buddy - Your Smart AI Voice Assistant

Buddy is a smart, GUI-based AI voice assistant that uses voice commands to perform a variety of real-time tasks such as:
- Answering questions (via LLM & SerpAPI)
- Generating images with Stability AI
- Performing system operations (open apps, control volume, shutdown)
- Searching and playing music on YouTube
- Capturing screenshots and photos
- Managing timers and reminders
- And more...

---

## 🚀 Features

- 🎤 Wake Word Detection (e.g., "hey buddy", "ok buddy")
- 🗣️ Voice Command Recognition (Speech-to-Text)
- 💬 Smart LLM Responses via DeepSeek/OpenRouter API
- 🌐 Real-Time Answers via SerpAPI
- 🖼️ AI Image Generation (Stability API)
- 📸 Open Camera and Take Photos
- 🔊 Volume and Media Controls
- 🧠 Smart Intent Recognition for OS, YouTube, Timer, and More
- 🎧 Background Listening with PyQt5 GUI
- 🧱 Modular Design with Backend + GUI Frontend

---

## 🖥️ GUI Interface

Built with **PyQt5**, the interface includes:
- GIF-based avatar animation
- Real-time chat transcript viewer
- 🎤 Voice button to issue commands manually
- 🛑 Stop Speaking button to interrupt TTS
- ⏱️ Timer visualization (optional)

---

## 🔧 System Requirements

- OS: Windows 10/11
- Python: 3.10+
- RAM: 4GB minimum
- Internet connection (for API calls and real-time responses)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/buddy-voice-assistant.git
cd buddy-voice-assistant
pip install -r requirements.txt

SETUP
Add your API keys in buddy.py:
openai.api_key = "your_openrouter_api_key"
serpapi_api_key = "your_serpapi_key"
STABILITY_API_KEY = "your_stability_api_key"
Run the assistant:
bash
python buddy_gui.py
```
FUTURE ENHANCEMENTS
Custom voice profiles

Wake-word training

Offline fallback mode

Weather forecast widget

Image generation gallery

AND MORE......

Contributing
Pull requests are welcome! For major changes, please open an issue first.

✨ Developed by
Mohammed Fawwaz
@fawwazsid

