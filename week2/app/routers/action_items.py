from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..exceptions import (
    handle_database_error,
    handle_external_service_error,
    handle_validation_error,
    NotFoundError,
)
from ..services.extract import extract_action_items, extract_action_items_llm
from ..schemas import (
    ActionExtractRequest,
    ActionExtractResponse,
    ActionItemListItem,
    ActionItemResponse,
    ActionItemUpdateResponse,
)


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ActionExtractResponse)
def extract(payload: ActionExtractRequest) -> ActionExtractResponse:
    """
    Extract action items from text using regex-based extraction.
    
    - **text**: The input text to extract action items from
    - **save_note**: Whether to save the input text as a note
    
    Returns extracted action items and optionally a note ID.
    """
    text = payload.text.strip()
    if not text:
        handle_validation_error("text", "is required and cannot be empty")

    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = db.insert_note(text)

        items = extract_action_items(text)
        ids = db.insert_action_items(items, note_id=note_id)
        return ActionExtractResponse(
            note_id=note_id,
            items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
        )
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error("extract action items", e)


@router.post("/extract-llm", response_model=ActionExtractResponse)
def extract_llm(payload: ActionExtractRequest) -> ActionExtractResponse:
    """
    Extract action items from text using LLM-powered extraction.
    
    - **text**: The input text to extract action items from
    - **save_note**: Whether to save the input text as a note
    
    Returns extracted action items and optionally a note ID.
    Uses AI/LLM for more sophisticated extraction compared to regex-based extraction.
    """
    text = payload.text.strip()
    if not text:
        handle_validation_error("text", "is required and cannot be empty")

    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = db.insert_note(text)

        items = extract_action_items_llm(text)
        ids = db.insert_action_items(items, note_id=note_id)
        return ActionExtractResponse(
            note_id=note_id,
            items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
        )
    except HTTPException:
        raise
    except Exception as exc:
        handle_external_service_error("LLM", exc)


@router.get("", response_model=List[ActionItemListItem])
def list_all(note_id: Optional[int] = None) -> List[ActionItemListItem]:
    """
    List all action items, optionally filtered by note ID.
    
    - **note_id**: Optional note ID to filter action items by
    
    Returns a list of action items in reverse chronological order.
    """
    try:
        rows = db.list_action_items(note_id=note_id)
        return [
            ActionItemListItem(
                id=r["id"],
                note_id=r["note_id"],
                text=r["text"],
                done=bool(r["done"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]
    except Exception as e:
        handle_database_error("list action items", e)


@router.post("/{action_item_id}/done", response_model=ActionItemUpdateResponse)
def mark_done(action_item_id: int, payload: dict) -> ActionItemUpdateResponse:
    """
    Mark an action item as done or not done.
    
    - **action_item_id**: The ID of the action item to update
    - **payload**: JSON body containing 'done' boolean field
    
    Returns the updated action item status.
    """
    try:
        done = bool(payload.get("done", True))
        db.mark_action_item_done(action_item_id, done)
        return ActionItemUpdateResponse(id=action_item_id, done=done)
    except Exception as e:
        handle_database_error("mark action item as done", e)


