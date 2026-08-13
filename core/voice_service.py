"""Voice services handling Speech-to-Text and Text-to-Speech synthesis."""

from __future__ import annotations
import re


def listen_for_command() -> str:
    """Captures microphone input and converts it to text (Speech-to-Text)."""
    try:
        import speech_recognition as sr
    except ImportError:
        return "[Error: SpeechRecognition library is not installed. Please run: pip install SpeechRecognition]"

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("\nListening for your command... (Speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            audio = recognizer.listen(source, timeout=5.0, phrase_time_limit=8.0)
            print("Processing speech...")
            command = recognizer.recognize_google(audio)
            print(f"Heard command: '{command}'")
            return command
    except sr.WaitTimeoutError:
        return "[Error: Listening timed out. No speech detected.]"
    except sr.UnknownValueError:
        return "[Error: Speech not recognized. Please speak clearly.]"
    except sr.RequestError as e:
        return f"[Error: API Request error from Speech Recognition service; {e}]"
    except Exception as e:
        return f"[Error: Microphone or capture error; {e}. Please ensure microphone is connected.]"


def speak_response(text: str) -> bool:
    """Reads aloud the AI text response using text-to-speech (optional)."""
    try:
        import pyttsx3
        # Remove markdown symbols for cleaner speech
        clean_text = re.sub(r"[\*#_`\-]", "", text)
        engine = pyttsx3.init()
        engine.say(clean_text)
        engine.runAndWait()
        return True
    except Exception:
        # Ignore speech failures and let the user view the text response
        return False
