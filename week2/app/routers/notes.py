from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import NoteCreate, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreate) -> NoteResponse:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    try:
        note_id = db.insert_note(content)
        note = db.get_note(note_id)
        if note is None:
            raise HTTPException(status_code=500, detail="failed to fetch created note")
        return NoteResponse(id=note["id"], content=note["content"], created_at=note["created_at"])  # type: ignore[index]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="failed to create note")


@router.get("", response_model=List[NoteResponse])
def list_notes() -> List[NoteResponse]:
    # List all notes in reverse chronological order
    try:
        rows = db.list_notes()
        return [
            NoteResponse(id=r["id"], content=r["content"], created_at=r["created_at"])  # type: ignore[index]
            for r in rows
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="failed to list notes")


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    try:
        row = db.get_note(note_id)
        if row is None:
            raise HTTPException(status_code=404, detail="note not found")
        return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])  # type: ignore[index]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="failed to get note")


@router.delete("/{note_id}", response_model=Dict[str, Any])
def delete_note_endpoint(note_id: int) -> Dict[str, Any]:
    try:
        # Ensure it exists first for a 404 if not
        row = db.get_note(note_id)
        if row is None:
            raise HTTPException(status_code=404, detail="note not found")
        db.delete_note(note_id)
        return {"deleted": True, "id": note_id}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="failed to delete note")

