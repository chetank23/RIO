"""
agents/common/llm_client.py
---------------------------
Multi-provider LLM gateway supporting Groq, Google Gemini, Ollama, and Anthropic.
Enforces the core system rules:
1. Grounded answering: Always invokes database tools; never answers from internal LLM weights.
2. Temporal anchor: Strictly injects live timestamp/date/day context into every system prompt.
3. Offline resiliency: Gracefully cascades to deterministic tool extraction if API keys are absent or services offline.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import httpx

from backend.models.identity import User
from backend import config

logger = logging.getLogger(__name__)


def get_current_timestamp_context() -> Dict[str, str]:
    """
    Returns the live temporal anchor for prompt injection and relative date resolution.
    Format:
      - current_datetime: '2026-11-13 14:30:00 (Friday)'
      - current_date: '2026-11-13'
      - current_day: 'FRI'
      - tomorrow_date: '2026-11-14'
      - tomorrow_day: 'SAT'
    """
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)
    return {
        "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S (%A)"),
        "current_date": now.strftime("%Y-%m-%d"),
        "current_day": now.strftime("%a").upper()[:3],
        "tomorrow_date": tomorrow.strftime("%Y-%m-%d"),
        "tomorrow_day": tomorrow.strftime("%a").upper()[:3],
    }


def build_system_prompt_with_temporal_context(user: User, base_role: str = "Query Agent") -> str:
    """
    Constructs the canonical system prompt with live date/time anchor and strict database grounding rules.
    """
    ctx = get_current_timestamp_context()
    return (
        f"You are the RIO-MJP Campus Assistant {base_role}.\n"
        f"======================================================================\n"
        f"CURRENT DATE & TIME: {ctx['current_datetime']}\n"
        f"TODAY:               {ctx['current_day']} ({ctx['current_date']})\n"
        f"TOMORROW:            {ctx['tomorrow_day']} ({ctx['tomorrow_date']})\n"
        f"CALLER CONTEXT:      User ID #{user.id}, Role: {user.role}, Email: {user.email}\n"
        f"======================================================================\n"
        f"GROUND RULES (MANDATORY):\n"
        f"1. Single Source of Truth: The campus SQLite database is the authoritative repository.\n"
        f"   Never invent, extrapolate, or answer campus information from pre-trained model memory.\n"
        f"2. Tool Invocation: For any question regarding timetables, rooms, faculty, courses, bookings,\n"
        f"   or events, you MUST invoke the appropriate database tool.\n"
        f"3. Relative Temporal Resolution: Resolve 'today', 'tomorrow', 'next class', 'Wednesday', etc.,\n"
        f"   strictly using the current date and time provided above.\n"
    )


def call_llm_tool_selector(
    message: str,
    tools: List[Dict[str, Any]],
    user: User,
    timeout_seconds: float = 8.0,
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    Attempts to select a tool call from the user message across available LLM providers in priority order:
    1. Groq (if GROQ_API_KEY)
    2. Google Gemini (if GEMINI_API_KEY)
    3. Ollama (if OLLAMA_BASE_URL is reachable and configured)
    4. Anthropic (if ANTHROPIC_API_KEY)

    Returns (tool_name, tool_arguments) if an LLM selects a valid tool, or None to fall back to deterministic extraction.
    """
    system_prompt = build_system_prompt_with_temporal_context(user)

    # 1. Groq (OpenAI-compatible Tool Calling API)
    groq_key = os.environ.get("GROQ_API_KEY", config.GROQ_API_KEY).strip()
    if groq_key and not groq_key.startswith("mock-") and not groq_key.startswith("test-"):
        try:
            groq_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                    },
                }
                for t in tools
            ]
            payload = {
                "model": config.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                "tools": groq_tools,
                "tool_choice": "auto",
                "max_tokens": 512,
            }
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                if res.status_code == 200:
                    data = res.json()
                    choice = data.get("choices", [{}])[0].get("message", {})
                    tool_calls = choice.get("tool_calls", [])
                    if tool_calls:
                        fn = tool_calls[0].get("function", {})
                        fn_name = fn.get("name")
                        fn_args = json.loads(fn.get("arguments", "{}"))
                        return fn_name, fn_args
        except Exception as exc:
            logger.warning(f"Groq tool call failed or timed out: {exc}")

    # 2. Google Gemini (REST API Function Calling)
    gemini_key = os.environ.get("GEMINI_API_KEY", config.GEMINI_API_KEY).strip()
    if gemini_key and not gemini_key.startswith("mock-") and not gemini_key.startswith("test-"):
        try:
            gemini_tools = [
                {
                    "function_declarations": [
                        {
                            "name": t["name"],
                            "description": t["description"],
                            "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                        }
                        for t in tools
                    ]
                }
            ]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent?key={gemini_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": message}]}],
                "tools": gemini_tools,
            }
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            if "functionCall" in part:
                                fc = part["functionCall"]
                                return fc.get("name"), fc.get("args", {})
        except Exception as exc:
            logger.warning(f"Gemini tool call failed or timed out: {exc}")

    # 3. Ollama (Local LLM Tool Calling)
    ollama_url = os.environ.get("OLLAMA_BASE_URL", config.OLLAMA_BASE_URL).strip()
    use_ollama = os.environ.get("USE_OLLAMA", "false").strip().lower() in ("1", "true", "yes")
    if use_ollama and ollama_url:
        try:
            ollama_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                    },
                }
                for t in tools
            ]
            payload = {
                "model": config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                "tools": ollama_tools,
                "stream": False,
            }
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.post(f"{ollama_url}/api/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    msg_obj = data.get("message", {})
                    tool_calls = msg_obj.get("tool_calls", [])
                    if tool_calls:
                        fn = tool_calls[0].get("function", {})
                        return fn.get("name"), fn.get("arguments", {})
        except Exception as exc:
            logger.warning(f"Ollama tool call failed or timed out: {exc}")

    # 4. Anthropic Claude (SDK Tool Calling)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", config.ANTHROPIC_API_KEY).strip()
    if anthropic_key and not anthropic_key.startswith("mock-") and not anthropic_key.startswith("test-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            from anthropic.types import ToolParam

            anthropic_tools: list[ToolParam] = [
                {
                    "name": str(t["name"]),
                    "description": str(t["description"]),
                    "input_schema": t.get("parameters", {}),
                }
                for t in tools
            ]
            response = client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
                tools=anthropic_tools,
            )
            for block in response.content:
                if block.type == "tool_use":
                    return block.name, block.input
        except Exception as exc:
            logger.warning(f"Anthropic tool call failed: {exc}")

    return None

