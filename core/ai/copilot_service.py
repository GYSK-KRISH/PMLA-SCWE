"""High-Level AI Teacher Copilot Service for PMLA-SCWE.

Provides 8 predefined grounded copilot actions + conversational query dispatch,
enforcing human-in-the-loop advisory notices and automated deterministic offline fallback.
"""

from __future__ import annotations
from typing import Any

from . import provider_manager, context_builder, prompt_templates, response_parser


def explain_student_risk(student_id: int) -> dict[str, Any]:
    """Action 1: Explains student risk breakdown and evidence."""
    ctx = context_builder.build_grounded_student_context(student_id)
    if not ctx["found"]:
        return {
            "success": False,
            "action": "explain_risk",
            "response": f"⚠️ Student #{student_id} not found in database.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Student not found"
        }

    user_prompt = prompt_templates.build_explain_risk_prompt(ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("explain_risk", student_id=student_id)

    return response_parser.parse_and_validate_copilot_response(res["response"], "explain_risk", res)


def create_study_plan(student_id: int, duration_days: int = 7) -> dict[str, Any]:
    """Action 2: Generates personalized 7, 14, or 30-day remedial study plan."""
    ctx = context_builder.build_grounded_student_context(student_id)
    if not ctx["found"]:
        return {
            "success": False,
            "action": "study_plan",
            "response": f"⚠️ Student #{student_id} not found in database.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Student not found"
        }

    duration = duration_days if duration_days in (7, 14, 30) else 7
    user_prompt = prompt_templates.build_study_plan_prompt(ctx["text"], duration_days=duration)
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("study_plan", student_id=student_id, duration_days=duration)

    return response_parser.parse_and_validate_copilot_response(res["response"], "study_plan", res)


def identify_weak_topics(student_id: int) -> dict[str, Any]:
    """Action 3: Identifies diagnostic weak learning areas and suggests remediation."""
    ctx = context_builder.build_grounded_student_context(student_id)
    if not ctx["found"]:
        return {
            "success": False,
            "action": "identify_weak_topics",
            "response": f"⚠️ Student #{student_id} not found in database.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Student not found"
        }

    user_prompt = prompt_templates.build_weak_topics_prompt(ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("identify_weak_topics", student_id=student_id)

    return response_parser.parse_and_validate_copilot_response(res["response"], "identify_weak_topics", res)


def generate_intervention_plan(student_id: int) -> dict[str, Any]:
    """Action 4: Drafts structured teacher intervention plan requiring confirmation."""
    ctx = context_builder.build_grounded_student_context(student_id)
    if not ctx["found"]:
        return {
            "success": False,
            "action": "generate_intervention",
            "response": f"⚠️ Student #{student_id} not found in database.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Student not found"
        }

    user_prompt = prompt_templates.build_intervention_plan_prompt(ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("generate_intervention", student_id=student_id)

    return response_parser.parse_and_validate_copilot_response(res["response"], "generate_intervention", res)


def summarize_class_performance(class_name: str | None = None, section: str | None = None) -> dict[str, Any]:
    """Action 5: Generates aggregate classroom briefing for teacher prep."""
    class_ctx = context_builder.build_class_context(class_name, section)
    user_prompt = prompt_templates.build_class_summary_prompt(class_ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("class_summary", class_name=class_name, section=section)

    return response_parser.parse_and_validate_copilot_response(res["response"], "class_summary", res)


def compare_two_students(student_id_1: int, student_id_2: int) -> dict[str, Any]:
    """Action 6: Compares two students constructively without ranking."""
    comp_ctx = context_builder.build_comparison_context(student_id_1, student_id_2)
    if not comp_ctx["valid"]:
        return {
            "success": False,
            "action": "compare_students",
            "response": f"⚠️ {comp_ctx['text']}",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": comp_ctx["text"]
        }

    user_prompt = prompt_templates.build_compare_students_prompt(comp_ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback(
            "compare_students",
            student_id=student_id_1,
            compare_student_id=student_id_2
        )

    return response_parser.parse_and_validate_copilot_response(res["response"], "compare_students", res)


def draft_parent_summary(student_id: int) -> dict[str, Any]:
    """Action 7: Drafts respectful, teacher-reviewed parent progress letter."""
    ctx = context_builder.build_grounded_student_context(student_id)
    if not ctx["found"]:
        return {
            "success": False,
            "action": "parent_summary",
            "response": f"⚠️ Student #{student_id} not found in database.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Student not found"
        }

    user_prompt = prompt_templates.build_parent_summary_prompt(ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("parent_summary", student_id=student_id)

    return response_parser.parse_and_validate_copilot_response(res["response"], "parent_summary", res)


def suggest_teacher_actions(student_id: int) -> dict[str, Any]:
    """Action 8: Generates prioritized pedagogical next steps checklist."""
    ctx = context_builder.build_grounded_student_context(student_id)
    if not ctx["found"]:
        return {
            "success": False,
            "action": "suggest_actions",
            "response": f"⚠️ Student #{student_id} not found in database.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Student not found"
        }

    user_prompt = prompt_templates.build_suggest_actions_prompt(ctx["text"])
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("suggest_actions", student_id=student_id)

    return response_parser.parse_and_validate_copilot_response(res["response"], "suggest_actions", res)


def ask_copilot(query: str, student_id: int | None = None) -> dict[str, Any]:
    """Handles free-form teacher inquiry with optional student context."""
    if not query.strip():
        return {
            "success": False,
            "action": "general_inquiry",
            "response": "Please enter a valid teacher inquiry.",
            "provider": None,
            "model": None,
            "fallback_used": False,
            "is_offline_fallback": False,
            "error": "Empty query"
        }

    context_text = None
    if student_id is not None:
        ctx = context_builder.build_grounded_student_context(student_id)
        if ctx["found"]:
            context_text = ctx["text"]

    user_prompt = prompt_templates.build_general_copilot_prompt(context_text, query)
    res = provider_manager.execute_ai_completion(prompt_templates.SYSTEM_COPILOT_PROMPT, user_prompt)

    if not res["success"] or res.get("is_offline_fallback"):
        return response_parser.generate_deterministic_fallback("general_inquiry", student_id=student_id, query=query)

    return response_parser.parse_and_validate_copilot_response(res["response"], "general_inquiry", res)


def dispatch_copilot_action(action_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Unified dispatcher for all 8 Copilot actions."""
    sid = params.get("student_id")
    if sid is not None:
        try:
            sid = int(sid)
        except (ValueError, TypeError):
            sid = None

    if action_name in ("explain_risk", "explain_student_risk"):
        return explain_student_risk(sid) if sid else {"success": False, "response": "Please select a Student ID."}
    elif action_name in ("study_plan", "create_study_plan"):
        dur = int(params.get("duration_days", 7))
        return create_study_plan(sid, duration_days=dur) if sid else {"success": False, "response": "Please select a Student ID."}
    elif action_name in ("identify_weak_topics", "weak_topics"):
        return identify_weak_topics(sid) if sid else {"success": False, "response": "Please select a Student ID."}
    elif action_name in ("generate_intervention", "intervention_plan"):
        return generate_intervention_plan(sid) if sid else {"success": False, "response": "Please select a Student ID."}
    elif action_name in ("class_summary", "summarize_class"):
        c_name = params.get("class_name")
        sec = params.get("section")
        return summarize_class_performance(c_name, sec)
    elif action_name in ("compare_students", "compare_two_students"):
        sid2 = params.get("compare_student_id")
        try:
            sid2 = int(sid2) if sid2 is not None else None
        except (ValueError, TypeError):
            sid2 = None
        if not sid or not sid2:
            return {"success": False, "response": "Please provide two valid Student IDs to compare."}
        return compare_two_students(sid, sid2)
    elif action_name in ("parent_summary", "draft_parent_summary"):
        return draft_parent_summary(sid) if sid else {"success": False, "response": "Please select a Student ID."}
    elif action_name in ("suggest_actions", "teacher_actions"):
        return suggest_teacher_actions(sid) if sid else {"success": False, "response": "Please select a Student ID."}
    else:
        return ask_copilot(params.get("query", ""), student_id=sid)
