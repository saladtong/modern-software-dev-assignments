from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..services.extract import extract_action_items
from ..schemas import (
    ActionExtractRequest,
    ActionExtractResponse,
    ActionItemListItem,
    ActionItemResponse,
)


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ActionExtractResponse)
def extract(payload: ActionExtractRequest) -> ActionExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

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
    except Exception:
        raise HTTPException(status_code=500, detail="failed to extract action items")


@router.get("", response_model=List[ActionItemListItem])
def list_all(note_id: Optional[int] = None) -> List[ActionItemListItem]:
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
    except Exception:
        raise HTTPException(status_code=500, detail="failed to list action items")


@router.post("/{action_item_id}/done", response_model=Dict[str, Any])
def mark_done(action_item_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        done = bool(payload.get("done", True))
        db.mark_action_item_done(action_item_id, done)
        return {"id": action_item_id, "done": done}
    except Exception:
        raise HTTPException(status_code=500, detail="failed to mark done")


