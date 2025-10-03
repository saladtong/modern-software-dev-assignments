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
    # Fallback: if nothing matched, first try line-wise imperative detection
    if not extracted:
        for raw_line in lines:
            candidate = raw_line.strip()
            if not candidate:
                continue
            if _looks_imperative(candidate):
                extracted.append(candidate)
    # Second fallback: sentence-wise split for cases without newlines or trailing punctuation
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
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

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
        "Think step by step INTERNALLY to identify candidate action lines (bullets, numbered items, keyword prefixes like 'todo:'/'action:'/'next:', "
        "and sentences starting with imperative verbs such as add, create, implement, fix, update, write, check, verify, refactor, document, design, investigate). "
        "Convert phrasings like 'make sure to pay rent' to 'Pay rent'. Convert narrative like 'I have to figure out where a good study space is' to a concise action like 'Find a good study space'. "
        "OUTPUT REQUIREMENT: Return ONLY valid JSON conforming to the schema. Do not include any reasoning, commentary, or code fences."
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
        # Strip code-fences like ```json ... ``` or ``` ... ``` if present
        fenced = response_content.strip()
        if fenced.startswith("```") and fenced.endswith("```"):
            try:
                inner = fenced.strip("`")
                if "\n" in inner:
                    inner = inner.split("\n", 1)[1]
                response_content = inner
            except Exception:
                pass

        # If the model mixed prose with JSON, try to isolate the first JSON object/array
        content = response_content.strip()
        start_obj = content.find("{"); end_obj = content.rfind("}")
        start_arr = content.find("["); end_arr = content.rfind("]")
        candidate_json = None
        if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
            candidate_json = content[start_obj : end_obj + 1]
        elif start_arr != -1 and end_arr != -1 and end_arr > start_arr:
            candidate_json = content[start_arr : end_arr + 1]
        if candidate_json is None:
            candidate_json = content

        # Try parsing as an object with `items`, but also handle a bare array
        try:
            parsed = json.loads(candidate_json)
            if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                items = [str(x).strip() for x in parsed["items"] if str(x).strip()]
            elif isinstance(parsed, list):
                items = [str(x).strip() for x in parsed if str(x).strip()]
        except json.JSONDecodeError:
            # Last resort: extract lines that look like list items from the model output
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
