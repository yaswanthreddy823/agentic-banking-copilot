"""Guardrails: PII redaction and prompt-injection detection.

Redaction runs before anything is logged or returned in a trace, so a
trace can be shown to a reviewer without leaking the raw input.
Injection detection is deliberately conservative pattern matching:
a flagged input is escalated to a human, never silently answered.
"""

from __future__ import annotations

import re

_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_ACCOUNT = re.compile(r"\b\d{9,12}\b")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
_PHONE = re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")

_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard policy",
    "disregard your instructions",
    "you are now",
    "system prompt",
    "reveal your instructions",
    "pretend you are",
    "override compliance",
    "bypass the check",
]


def redact_text(text: str) -> str:
    """Replace common PII patterns with placeholders."""
    text = _SSN.sub("[REDACTED_SSN]", text)
    text = _ACCOUNT.sub("[REDACTED_ACCOUNT]", text)
    text = _EMAIL.sub("[REDACTED_EMAIL]", text)
    text = _PHONE.sub("[REDACTED_PHONE]", text)
    return text


def detect_injection(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in _INJECTION_PATTERNS)
