from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    save_note: Optional[bool] = False


class ActionItemResponse(BaseModel):
    id: int
    text: str


class ActionExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: List[ActionItemResponse]


class ActionItemListItem(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


