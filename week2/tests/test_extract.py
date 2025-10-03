import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


# generated with user guidance
# Tests added to cover imperative lines, LLM handling, careers content, and ignoring plain sentences
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


def test_extract_imperative_lines_without_markers():
    text = (
        "Implement authentication middleware\n"
        "create database schema for users\n"
        "Update deployment pipeline"
    )
    items = extract_action_items(text)
    assert "Implement authentication middleware" in items
    assert "create database schema for users" in items
    assert "Update deployment pipeline" in items


def test_ignore_plain_non_action_sentences():
    text = (
        "The system uses SQLite for persistence.\n"
        "There are many careers like teacher, engineer, or nurse.\n"
        "We discussed several options during the meeting."
    )
    items = extract_action_items(text)
    assert items == []


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


def test_llm_extract_make_sure_and_careers(monkeypatch):
    from ..app import services

    def chat_mock(model=None, messages=None, **kwargs):
        return {
            "message": {
                "content": (
                    "{" "\"items\": ["
                    "\"Make sure to follow up with the hiring manager\","
                    "\"Schedule meeting with the software engineer candidates\","
                    "\"Prepare outreach email for teachers and nurses\""
                    "]}"
                )
            }
        }

    monkeypatch.setattr(services.extract, "chat", chat_mock)

    text = (
        "make sure to follow up with the hiring manager\n"
        "Discuss various careers like software engineer, teacher, nurse\n"
        "Schedule meeting with the software engineer candidates\n"
        "Prepare outreach email for teachers and nurses"
    )

    items = extract_action_items_llm(text)
    assert "Make sure to follow up with the hiring manager" in items
    assert "Schedule meeting with the software engineer candidates" in items
    assert "Prepare outreach email for teachers and nurses" in items
