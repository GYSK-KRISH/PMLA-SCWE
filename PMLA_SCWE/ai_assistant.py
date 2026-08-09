"""AI Assistant module for PMLA-SCWE using OpenAI or Gemini."""

from __future__ import annotations
import os
import re
from .analytics import get_student_analytics_summary

SYSTEM_PROMPT = """You are the PMLA-SCWE academic analytics assistant.

You help teachers understand student academic performance,
attendance, progress and cyber-wellness data.

Explain information clearly and simply.

Use only the data provided.

Never invent student information.

Do not provide medical or psychological diagnoses.

Give practical educational suggestions.

Clearly distinguish between actual student data
and your interpretation.
"""

def get_ai_client() -> tuple[str, object] | None:
    """Detects and returns the configured AI client (OpenAI or Gemini).
    
    Returns:
        A tuple of (provider_name, client_object) or None if not configured.
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            return "openai", client
        except ImportError:
            pass

    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            return "gemini", client
        except ImportError:
            pass

    return None


def ask_ai(question: str) -> str:
    """Sends a general question to the configured AI provider and returns the response."""
    if not question.strip():
        return "Please enter a valid question."

    client_info = get_ai_client()
    if not client_info:
        return "AI is not configured. Please add the API key as an environment variable."

    provider, client = client_info

    try:
        if provider == "openai":
            model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()

        elif provider == "gemini":
            model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            response = client.models.generate_content(
                model=model,
                contents=question,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.7
                }
            )
            return response.text.strip()

    except Exception as e:
        return f"AI service is currently unavailable. You can continue using the normal PMLA-SCWE analytics. (Error: {e})"

    return "AI configuration issue."


def ask_ai_about_student(student_id: int, question: str) -> str:
    """Sends student analytics context along with a question to the AI."""
    summary = get_student_analytics_summary(student_id)
    if not summary:
        return f"Student ID {student_id} not found in the database."

    # Build context summary string using only actual student data
    context = (
        f"Student ID: {summary['student_id']}\n"
        f"Student Name: {summary['student_name']}\n"
        f"Class Section: {summary['class_section']}\n"
        f"Academic Average Score: {summary['academic_average']:.2f}% ({summary['academic_status']})\n"
        f"Attendance Percentage: {summary['attendance_percentage']:.2f}% ({summary['attendance_status']})\n"
        f"Cyber-Wellness Score: {summary['cyber_wellness_score']:.2f}% ({summary['wellness_status']})\n"
        f"Weekly Progress: {summary['weekly_progress']:.2f}%\n"
        f"Progress Trend: {summary['trend']}\n"
        f"Learning Health Score: {summary['learning_health_score']:.2f}\n"
        f"Risk Level: {summary['risk_level']}\n"
        f"Risk Reasons: {', '.join(summary['risk_reasons']) if summary['risk_reasons'] else 'None'}\n"
    )

    full_prompt = (
        f"Here is the data for the student:\n\n{context}\n"
        f"Teacher's Question: {question}"
    )

    return ask_ai(full_prompt)


def get_ai_suggestions(student_id: int) -> str:
    """Retrieves AI suggestions for a student based on their data."""
    question = (
        "Provide structured educational suggestions for this student in the following format:\n\n"
        "Academic:\n"
        "[suggestions]\n\n"
        "Attendance:\n"
        "[suggestions]\n\n"
        "Cyber Wellness:\n"
        "[suggestions]\n\n"
        "Teacher Action:\n"
        "[suggestions]"
    )
    return ask_ai_about_student(student_id, question)


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
