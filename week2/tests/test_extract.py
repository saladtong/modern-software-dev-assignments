import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_llm_extract_bullet_list(monkeypatch):
    from ..app import services

    def chat_mock(model=None, messages=None, **kwargs):
        # Return structured content expected by extract_action_items_llm
        return {
            "message": {
                "content": (
                    "{" "\"items\": ["
                    "\"Set up database\","
                    "\"implement API extract endpoint\","
                    "\"Write tests\""
                    "]}"
                )
            }
        }

    # Patch the chat function used inside the extractor module
    monkeypatch.setattr(services.extract, "chat", chat_mock)

    text = """
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    """.strip()

    items = extract_action_items_llm(text)
    assert items == [
        "Set up database",
        "implement API extract endpoint",
        "Write tests",
    ]


def test_llm_extract_keyword_prefixed(monkeypatch):
    from ..app import services

    def chat_mock(model=None, messages=None, **kwargs):
        return {
            "message": {
                "content": (
                    "{" "\"items\": ["
                    "\"setup CI pipeline\","
                    "\"update documentation\""
                    "]}"
                )
            }
        }

    monkeypatch.setattr(services.extract, "chat", chat_mock)

    text = """
    Notes from standup:
    todo: setup CI pipeline
    action: update documentation
    """.strip()

    items = extract_action_items_llm(text)
    assert "setup CI pipeline" in items
    assert "update documentation" in items


def test_llm_extract_empty_input_short_circuits(monkeypatch):
    from ..app import services

    def chat_mock(*args, **kwargs):
        raise AssertionError("chat should not be called for empty input")

    monkeypatch.setattr(services.extract, "chat", chat_mock)

    assert extract_action_items_llm("") == []
