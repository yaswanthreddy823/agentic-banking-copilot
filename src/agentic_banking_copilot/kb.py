"""Synthetic banking knowledge base.

These documents are invented for this demo. They describe generic,
plausible bank policies — they are not any real bank's policies.
"""

from __future__ import annotations

import json
from pathlib import Path

KB_PATH = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.json"


def load_knowledge_base() -> list[dict]:
    """Load the synthetic knowledge base from data/knowledge_base.json."""
    with open(KB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["documents"]
