from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..exceptions import (
    handle_database_error,
    handle_not_found_error,
    handle_validation_error,
)
from ..schemas import NoteCreate, NoteResponse, NoteDeleteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreate) -> NoteResponse:
    """
    Create a new note.
    
    - **content**: The content of the note (required, minimum 1 character)
    
    Returns the created note with its ID and timestamp.
    """
    content = payload.content.strip()
    if not content:
        handle_validation_error("content", "is required and cannot be empty")
    
    try:
        note_id = db.insert_note(content)
        note = db.get_note(note_id)
        if note is None:
            handle_database_error("fetch created note", Exception("Note not found after creation"))
        return NoteResponse(
            id=note["id"], 
            content=note["content"], 
            created_at=note["created_at"]
        )  # type: ignore[index]
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error("create note", e)


@router.get("", response_model=List[NoteResponse])
def list_notes() -> List[NoteResponse]:
    """
    List all notes in reverse chronological order.
    
    Returns a list of all notes sorted by creation date (newest first).
    """
    try:
        rows = db.list_notes()
        return [
            NoteResponse(
                id=r["id"], 
                content=r["content"], 
                created_at=r["created_at"]
            )  # type: ignore[index]
            for r in rows
        ]
    except Exception as e:
        handle_database_error("list notes", e)


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """
    Get a single note by ID.
    
    - **note_id**: The ID of the note to retrieve
    
    Returns the note if found, 404 if not found.
    """
    try:
        row = db.get_note(note_id)
        if row is None:
            handle_not_found_error("Note", str(note_id))
        return NoteResponse(
            id=row["id"], 
            content=row["content"], 
            created_at=row["created_at"]
        )  # type: ignore[index]
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error("get note", e)


@router.delete("/{note_id}", response_model=NoteDeleteResponse)
def delete_note_endpoint(note_id: int) -> NoteDeleteResponse:
    """
    Delete a note and all its associated action items.
    
    - **note_id**: The ID of the note to delete
    
    Returns confirmation of deletion. Also deletes all action items linked to this note.
    """
    try:
        # Ensure it exists first for a 404 if not
        row = db.get_note(note_id)
        if row is None:
            handle_not_found_error("Note", str(note_id))
        db.delete_note(note_id)
        return NoteDeleteResponse(deleted=True, id=note_id)
    except HTTPException:
        raise
    except Exception as e:
        handle_database_error("delete note", e)

