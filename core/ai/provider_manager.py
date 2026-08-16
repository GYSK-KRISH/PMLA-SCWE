"""AI Provider Manager for PMLA-SCWE.

Handles API configuration, OpenAI and Google Gemini provider execution,
preference routing (auto/openai/gemini), and automatic fallback chains.
"""

from __future__ import annotations
import os
from typing import Any


def load_ai_config() -> dict[str, Any]:
    """Loads current AI configuration from environment variables."""
    provider_pref = os.environ.get("AI_PROVIDER", "auto").lower().strip()
    if provider_pref not in ("auto", "openai", "gemini"):
        provider_pref = "auto"

    return {
        "provider": provider_pref,
        "openai_key": os.environ.get("OPENAI_API_KEY"),
        "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "gemini_key": os.environ.get("GEMINI_API_KEY"),
        "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    }


def get_available_providers(cfg: dict[str, Any] | None = None) -> list[str]:
    """Detects available configured providers with non-empty API keys."""
    if cfg is None:
        cfg = load_ai_config()

    providers = []
    if cfg.get("gemini_key") and str(cfg["gemini_key"]).strip():
        providers.append("gemini")
    if cfg.get("openai_key") and str(cfg["openai_key"]).strip():
        providers.append("openai")
    return providers


def select_provider_order(cfg: dict[str, Any] | None = None) -> list[str]:
    """Determines prioritized provider sequence based on user preference and key availability."""
    if cfg is None:
        cfg = load_ai_config()

    available = get_available_providers(cfg)
    if not available:
        return []

    pref = cfg["provider"]
    if pref == "openai":
        order = []
        if "openai" in available:
            order.append("openai")
        if "gemini" in available:
            order.append("gemini")
        return order
    elif pref == "gemini":
        order = []
        if "gemini" in available:
            order.append("gemini")
        if "openai" in available:
            order.append("openai")
        return order
    else:  # 'auto' -> default to gemini if both available, else whichever is present
        order = []
        if "gemini" in available:
            order.append("gemini")
            if "openai" in available:
                order.append("openai")
        elif "openai" in available:
            order.append("openai")
        return order


def call_openai(cfg: dict[str, Any], system_prompt: str, user_prompt: str) -> str:
    """Executes a chat completion call using the OpenAI SDK."""
    from openai import OpenAI
    client = OpenAI(api_key=cfg["openai_key"])
    response = client.chat.completions.create(
        model=cfg["openai_model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()


def call_gemini(cfg: dict[str, Any], system_prompt: str, user_prompt: str) -> str:
    """Executes a content generation call using the Google GenAI SDK."""
    from google import genai
    client = genai.Client(api_key=cfg["gemini_key"])
    response = client.models.generate_content(
        model=cfg["gemini_model"],
        contents=user_prompt,
        config={
            "system_instruction": system_prompt,
            "temperature": 0.4
        }
    )
    return response.text.strip()


def execute_ai_completion(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    """Executes AI generation across available providers with automated fallback.

    Returns:
        Structured response dictionary with provider metadata:
        {
            "success": bool,
            "provider": str | None,
            "model": str | None,
            "response": str,
            "fallback_used": bool,
            "is_offline_fallback": bool,
            "error": str | None
        }
    """
    cfg = load_ai_config()
    available = get_available_providers(cfg)

    if not available:
        return {
            "success": False,
            "provider": None,
            "model": None,
            "response": "",
            "fallback_used": False,
            "is_offline_fallback": True,
            "error": "No OpenAI or Gemini API key configured."
        }

    order = select_provider_order(cfg)
    errors = []

    for idx, provider_name in enumerate(order):
        fallback_used = (idx > 0)
        try:
            if provider_name == "openai":
                output = call_openai(cfg, system_prompt, user_prompt)
                return {
                    "success": True,
                    "provider": "openai",
                    "model": cfg["openai_model"],
                    "response": output,
                    "fallback_used": fallback_used,
                    "is_offline_fallback": False,
                    "error": None
                }
            elif provider_name == "gemini":
                output = call_gemini(cfg, system_prompt, user_prompt)
                return {
                    "success": True,
                    "provider": "gemini",
                    "model": cfg["gemini_model"],
                    "response": output,
                    "fallback_used": fallback_used,
                    "is_offline_fallback": False,
                    "error": None
                }
        except Exception as exc:
            errors.append(f"{provider_name.upper()} failed: {exc}")

    # All online providers failed
    return {
        "success": False,
        "provider": None,
        "model": None,
        "response": "",
        "fallback_used": len(order) > 1,
        "is_offline_fallback": True,
        "error": " | ".join(errors)
    }


def get_ai_status_summary() -> dict[str, Any]:
    """Returns configuration and online/offline status for UI rendering."""
    cfg = load_ai_config()
    available = get_available_providers(cfg)
    order = select_provider_order(cfg)

    active_provider = order[0].capitalize() if order else None
    active_model = None
    if active_provider == "Openai":
        active_model = cfg["openai_model"]
    elif active_provider == "Gemini":
        active_model = cfg["gemini_model"]

    return {
        "openai_configured": "openai" in available,
        "gemini_configured": "gemini" in available,
        "active_provider": active_provider,
        "active_model": active_model,
        "status": "Online" if active_provider else "Offline",
        "provider_preference": cfg["provider"],
        "fallback_available": len(available) > 1
    }
