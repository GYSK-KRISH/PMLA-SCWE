"""Centralized AI assistant facade for backward compatibility with existing views.

Version 1.4 — Delegates all AI logic to the modular `core.ai` package while preserving legacy signatures.
"""

from __future__ import annotations
import re
from typing import Any

from . import ai
from .ai.prompt_templates import SYSTEM_COPILOT_PROMPT as SYSTEM_PROMPT


def load_ai_config() -> dict[str, Any]:
    return ai.load_ai_config()


def get_available_providers(cfg: dict[str, Any] | None = None) -> list[str]:
    return ai.get_available_providers(cfg)


def select_provider(cfg: dict[str, Any], available: list[str]) -> list[str]:
    return ai.select_provider_order(cfg)


def call_openai(cfg: dict[str, Any], system_prompt: str, user_prompt: str) -> str:
    from .ai.provider_manager import call_openai as _call_openai
    return _call_openai(cfg, system_prompt, user_prompt)


def call_gemini(cfg: dict[str, Any], system_prompt: str, user_prompt: str) -> str:
    from .ai.provider_manager import call_gemini as _call_gemini
    return _call_gemini(cfg, system_prompt, user_prompt)


def execute_with_fallback(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    return ai.execute_ai_completion(system_prompt, user_prompt)


def get_ai_status() -> dict[str, Any]:
    return ai.get_ai_status_summary()


def detect_intent(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["class summary", "all students", "class insights", "class overview", "summary of the class"]):
        return "class_summary"
    if any(k in q for k in ["study plan", "revision schedule", "remedial plan", "timetable"]):
        return "study_plan"
    if any(k in q for k in ["weak topic", "weakest", "struggling", "gap"]):
        return "weak_topics"
    if any(k in q for k in ["compare", "versus", "vs", "comparison"]):
        return "compare_students"
    if any(k in q for k in ["parent", "letter", "guardian", "email"]):
        return "parent_summary"
    if any(k in q for k in ["intervention", "action plan", "remedial"]):
        return "intervention_plan"
    if any(k in q for k in ["suggest", "advice", "teacher action", "next step"]):
        return "teacher_actions"
    if any(k in q for k in ["risk", "flagged", "threat"]):
        return "risk_analysis"
    return "general_question"


def extract_student_id(query: str) -> int | None:
    match = re.search(r"\bstudent\s*(?:id)?\s*#?(\d+)\b", query, re.IGNORECASE)
    if match:
        return int(match.group(1))

    nums = re.findall(r"\b(\d+)\b", query)
    if len(nums) == 1:
        return int(nums[0])

    return None


def build_student_context(student_id: int) -> str:
    ctx = ai.build_grounded_student_context(student_id)
    return ctx["text"]


def build_class_context() -> str:
    ctx = ai.build_class_context()
    return ctx["text"]


# ---------------------------------------------------------------------------
# Legacy Callers & High-Level Inquiries
# ---------------------------------------------------------------------------

def ask_ai(question: str) -> dict[str, Any]:
    sid = extract_student_id(question)
    intent = detect_intent(question)

    if intent == "class_summary":
        return ai.summarize_class_performance()
    elif sid is not None:
        if intent == "risk_analysis":
            return ai.explain_student_risk(sid)
        elif intent == "study_plan":
            return ai.create_study_plan(sid, 7)
        elif intent == "weak_topics":
            return ai.identify_weak_topics(sid)
        elif intent == "intervention_plan":
            return ai.generate_intervention_plan(sid)
        elif intent == "parent_summary":
            return ai.draft_parent_summary(sid)
        elif intent == "teacher_actions":
            return ai.suggest_teacher_actions(sid)
        else:
            return ai.ask_copilot(question, student_id=sid)
    else:
        return ai.ask_copilot(question)


def ask_ai_about_student(student_id: int, question: str) -> dict[str, Any]:
    intent = detect_intent(question)
    if intent == "risk_analysis":
        return ai.explain_student_risk(student_id)
    elif intent == "study_plan":
        return ai.create_study_plan(student_id, 7)
    elif intent == "weak_topics":
        return ai.identify_weak_topics(student_id)
    elif intent == "intervention_plan":
        return ai.generate_intervention_plan(student_id)
    elif intent == "parent_summary":
        return ai.draft_parent_summary(student_id)
    elif intent == "teacher_actions":
        return ai.suggest_teacher_actions(student_id)
    else:
        return ai.ask_copilot(question, student_id=student_id)


def get_ai_suggestions(student_id: int) -> dict[str, Any]:
    return ai.suggest_teacher_actions(student_id)


def analyze_student(student_id: int) -> dict[str, Any]:
    return ai.explain_student_risk(student_id)


def generate_intervention_plan(student_id: int) -> dict[str, Any]:
    return ai.generate_intervention_plan(student_id)


def get_class_insights() -> dict[str, Any]:
    return ai.summarize_class_performance()
