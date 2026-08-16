"""PMLA-SCWE AI Teacher Copilot Package.

Version 1.4 — AI Teacher Copilot & Intelligent Decision Support
"""

from .provider_manager import (
    load_ai_config,
    get_available_providers,
    select_provider_order,
    execute_ai_completion,
    get_ai_status_summary,
)
from .context_builder import (
    build_grounded_student_context,
    build_class_context,
    build_comparison_context,
)
from .copilot_service import (
    explain_student_risk,
    create_study_plan,
    identify_weak_topics,
    generate_intervention_plan,
    summarize_class_performance,
    compare_two_students,
    draft_parent_summary,
    suggest_teacher_actions,
    ask_copilot,
    dispatch_copilot_action,
)

__all__ = [
    "load_ai_config",
    "get_available_providers",
    "select_provider_order",
    "execute_ai_completion",
    "get_ai_status_summary",
    "build_grounded_student_context",
    "build_class_context",
    "build_comparison_context",
    "explain_student_risk",
    "create_study_plan",
    "identify_weak_topics",
    "generate_intervention_plan",
    "summarize_class_performance",
    "compare_two_students",
    "draft_parent_summary",
    "suggest_teacher_actions",
    "ask_copilot",
    "dispatch_copilot_action",
]
