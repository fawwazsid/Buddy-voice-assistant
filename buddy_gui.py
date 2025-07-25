import sys
import threading
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject
from buddy import listen, perform_task, speak, wait_for_wake_word, engine  # <-- Import engine
import time
# Signal handler for safe UI updates
class Communicator(QObject):
    update_text = pyqtSignal(str)

class BuddyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.comm = Communicator()

        self.comm.update_text.connect(self.append_text)

        self.init_ui()
        self.greet_user()
        self.start_wake_word_listener()


    def init_ui(self):
        self.setWindowTitle("Buddy Voice Assistant")
        self.setGeometry(300, 150, 600, 450)

        self.setStyleSheet("""
            background-color: black;
            color: white;
            QLabel {
                color: white;
                font-size: 16px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        layout = QVBoxLayout()

        # Animated GIF
        self.gif_label = QLabel()
        self.movie = QMovie("buddy.gif")
        self.movie.setScaledSize(QSize(400, 300))
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)

        # Text Box
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        # Button Layout
        button_layout = QHBoxLayout()

        # Voice Command Button
        self.listen_button = QPushButton("🎤 Voice Command")
        self.listen_button.clicked.connect(self.manual_listen)
        button_layout.addWidget(self.listen_button)

        # Stop Speaking Button
        self.stop_button = QPushButton("🛑 Stop Speaking")
        self.stop_button.clicked.connect(self.stop_speaking)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    def greet_user(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning!"
        elif hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        full_greeting = f"{greeting} I'm Buddy, your virtual voice assistant."
        self.comm.update_text.emit(f"Buddy: {full_greeting}")
        speak(full_greeting)

    def start_wake_word_listener(self):
        thread = threading.Thread(target=self.listen_for_wake_word_loop, daemon=True)
        thread.start()

    def listen_for_wake_word_loop(self):
        while True:
            try:
                self.comm.update_text.emit("🎤 Waiting for wake word...")
                if wait_for_wake_word():
                    self.comm.update_text.emit("Buddy: Hmm?")
                    speak("Hmm?")
                    cmd = listen()
                    if cmd:
                        self.comm.update_text.emit(f"You: {cmd}")
                        if "exit" in cmd or "bye" in cmd:
                            goodbye = "Goodbye! See you soon."
                            self.comm.update_text.emit(f"Buddy: {goodbye}")
                            speak(goodbye)
                            break
                        response = perform_task(cmd)
                        if response:
                            self.comm.update_text.emit(f"Buddy: {response}")
            except Exception as e:
                self.comm.update_text.emit(f"Error: {e}")

    def manual_listen(self):
        thread = threading.Thread(target=self.manual_listen_thread, daemon=True)
        thread.start()

    def manual_listen_thread(self):
        try:
            cmd = listen()
            if cmd:
                self.comm.update_text.emit(f"You: {cmd}")
                if "exit" in cmd or "bye" in cmd:
                    goodbye = "Goodbye! See you soon."
                    self.comm.update_text.emit(f"Buddy: {goodbye}")
                    speak(goodbye)
                    return
                response = perform_task(cmd)
                if response:
                    self.comm.update_text.emit(f"Buddy: {response}")
        except Exception as e:
            self.comm.update_text.emit(f"Error: {e}")

    def stop_speaking(self):
        engine.stop()  # <-- Stop TTS immediately
        self.comm.update_text.emit("Buddy: ✋ Speech stopped.")

    def append_text(self, text):
        self.text_box.append(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    global window
    window = BuddyApp()
    window.show()
    sys.exit(app.exec_())

