from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    text = text or ""
    if not text.strip():
        return []

    # Allow overriding the model via env; choose a lightweight default
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")

    # JSON schema for structured output. We ask for an object with a single
    # property `items` that is an array of strings.
    schema: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "items": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["items"],
    }

    # Improved guidance with few-shot examples and candidate grounding
    system_prompt = (
        "You extract concrete TODO items from messy notes. "
        "Rules: return ONLY JSON per schema; write items in imperative mood; deduplicate; "
        "exclude dates, names, and narrative unless essential; keep each item concise (<= 15 words)."
    )
    candidate_items = extract_action_items(text)
    examples = (
        "Examples:\n"
        "Input: '- [ ] Set up database' -> 'Set up database'\n"
        "Input: 'todo: update docs' -> 'update docs'\n"
        "Input: 'Discuss architecture tradeoffs' -> (exclude)\n"
    )
    user_prompt = (
        "Extract action items from the notes below. Prefer cleaning from CANDIDATES; "
        "include additional items only if clearly implied.\n\n"
        f"{examples}\n"
        f"CANDIDATES: {json.dumps(candidate_items)}\n\n"
        f"NOTES:\n{text}"
    )

    response_content: str | None = None
    # Strategy 1: simple JSON forcing (format="json") for maximum compatibility
    try:
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + "\n\nOutput as {\"items\": [\"...\"]} only."},
            ],
            format="json",
            options={"temperature": 0},
        )
        response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
    except Exception:
        response_content = None

    # Strategy 2: JSON Schema structured outputs (if supported)
    if not response_content:
        try:
            response = chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "action_items",
                        "schema": schema,
                    },
                },
                options={"temperature": 0},
            )
            response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
        except Exception:
            response_content = None

    # Strategy 3: plain prompt with explicit JSON instruction
    if not response_content:
        fallback_user_prompt = (
            "Extract action items and return ONLY a JSON object: {\\"items\\": [\\"...\\"]}. "
            "No prose.\n\n" f"NOTES:\n{text}"
        )
        try:
            response = chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": fallback_user_prompt},
                ],
                options={"temperature": 0},
            )
            response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
        except Exception:
            # If Ollama is unavailable or model pull fails, fall back to heuristic extractor
            return extract_action_items(text)

    items: List[str] = []
    if response_content:
        # Strip code-fence wrappers like ```json ... ``` if present
        fenced = response_content.strip()
        if fenced.startswith("```") and fenced.endswith("```"):
            try:
                inner = fenced.strip("`")
                if inner.lower().startswith("json\n"):
                    inner = inner.split("\n", 1)[1]
                response_content = inner
            except Exception:
                pass
        # Try parsing as an object with `items`, but also handle if the model
        # returns a bare array.
        # Processing the json
        try:
            parsed = json.loads(response_content)
            if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                items = [str(x).strip() for x in parsed["items"] if str(x).strip()]
            elif isinstance(parsed, list):
                items = [str(x).strip() for x in parsed if str(x).strip()]
        except json.JSONDecodeError:
            # Last resort: extract lines that look like list items
            for line in response_content.splitlines():
                candidate = BULLET_PREFIX_PATTERN.sub("", line).strip()
                if candidate:
                    items.append(candidate)

    # Normalize & deduplicate
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(cleaned)

    # If LLM returned nothing useful, fall back to heuristic extractor
    if not unique:
        return extract_action_items(text)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
