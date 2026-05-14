"""Shared engine utilities and re-exports."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Dict, List

from .types import Message


class EngineConnectionError(Exception):
    """Недоступен движок LLM."""


def messages_to_dicts(messages: Sequence[Message]) -> List[Dict[str, Any]]:
    """Конвертирует сообщения в OpenAI-формат."""
    out: List[Dict[str, Any]] = []
    for m in messages:
        d: Dict[str, Any] = {"role": m.role.value, "content": m.content}
        if m.name:
            d["name"] = m.name
        if m.tool_calls:
            d["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments,
                    },
                }
                for tc in m.tool_calls
            ]
        if m.tool_call_id:
            d["tool_call_id"] = m.tool_call_id
        out.append(d)
    return out
