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

    system_prompt = (
        "You are an expert at extracting concrete, actionable TODO items from notes. "
        "Return only valid JSON that conforms to the provided schema. "
        "Items should be concise, imperative, and deduplicated."
    )
    user_prompt = (
        "Extract action items from the following notes. "
        "Ignore narrative text that is not an action item.\n\n"
        f"NOTES:\n{text}"
    )

    response_content: str | None = None
    try:
        # Prefer structured outputs if supported by the installed Ollama version
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # Ollama supports `format` for JSON/JSON Schema structured outputs.
            # See: https://ollama.com/blog/structured-outputs
            format={
                "type": "json_schema",
                "json_schema": {
                    "name": "action_items",
                    "schema": schema,
                },
            },
            options={"temperature": 0},
        )
        # Expected shape: { "message": { "content": "{...json...}" }, ... }
        response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
    except Exception:
        # Fallback: request plain JSON (array) without schema enforcement
        fallback_user_prompt = (
            "Extract action items from the following notes and return ONLY a JSON "
            "object with an `items` array of strings (no preface, no trailing text).\n\n"
            f"NOTES:\n{text}"
        )
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": fallback_user_prompt},
            ],
            options={"temperature": 0},
        )
        response_content = response.get("message", {}).get("content")  # type: ignore[assignment]

    items: List[str] = []
    if response_content:
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
