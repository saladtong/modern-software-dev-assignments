from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# Request Schemas
class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="The content of the note")


class ActionExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to extract action items from")
    save_note: Optional[bool] = Field(False, description="Whether to save the input text as a note")


# Response Schemas
class NoteResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the note")
    content: str = Field(..., description="The content of the note")
    created_at: str = Field(..., description="ISO timestamp when the note was created")


class ActionItemResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the action item")
    text: str = Field(..., description="The text of the action item")


class ActionItemListItem(BaseModel):
    id: int = Field(..., description="Unique identifier for the action item")
    note_id: Optional[int] = Field(None, description="ID of the associated note, if any")
    text: str = Field(..., description="The text of the action item")
    done: bool = Field(..., description="Whether the action item is completed")
    created_at: str = Field(..., description="ISO timestamp when the action item was created")


class ActionExtractResponse(BaseModel):
    note_id: Optional[int] = Field(None, description="ID of the created note, if save_note was True")
    items: List[ActionItemResponse] = Field(..., description="List of extracted action items")


class ActionItemUpdateResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the action item")
    done: bool = Field(..., description="Whether the action item is completed")


class NoteDeleteResponse(BaseModel):
    deleted: bool = Field(..., description="Whether the note was successfully deleted")
    id: int = Field(..., description="ID of the deleted note")


# Error Response Schema
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    status_code: int = Field(..., description="HTTP status code")


