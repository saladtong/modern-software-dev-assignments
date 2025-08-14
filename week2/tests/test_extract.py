from __future__ import annotations

from week2.app.services.extract import extract_action_items


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


def test_extract_keyword_lines():
    text = """
    Discussion:
    Action: Add logging
    Todo: Refactor extract module
    Next: Document endpoints
    """.strip()

    items = extract_action_items(text)
    assert "Add logging" in items
    assert "Refactor extract module" in items
    assert "Document endpoints" in items


