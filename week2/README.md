# Action Item Extractor (Week 2)

Minimal FastAPI + SQLite app that converts free‑form notes into enumerated action items. Includes a raw HTML UI, a heuristic extractor, and an optional LLM‑powered extractor.

## Stack
- Backend: FastAPI (sync), Uvicorn
- Storage: SQLite (`week2/data/app.db`)
- Frontend: Raw HTML/JS (`week2/frontend/index.html`)

## Quickstart
1) Install deps (project root):
```bash
poetry install
```
2) Run the server:
```bash
poetry run uvicorn week2.app.main:app --reload
```
3) Open the UI: `http://127.0.0.1:8000/`

Optional (LLM): set `OPENAI_API_KEY` in your environment or `.env` at project root.

## API Overview

Base URL: `http://127.0.0.1:8000`

### Frontpage
- `GET /` → serves `frontend/index.html` (raw UI)

### Notes
- `POST /notes`
  - Body: `{ "content": string }`
  - Returns: `{ id, content, created_at }`
- `GET /notes`
  - Returns: `[{ id, content, created_at }]`
- `GET /notes/{note_id}`
  - Returns: `{ id, content, created_at }`

### Action Items (heuristic)
- `POST /action-items/extract`
  - Body: `{ "text": string, "save_note"?: boolean }`
  - Extracts items using heuristic rules; optionally saves the note and items.
  - Returns: `{ note_id?: number, items: [{ id, text }] }`
- `GET /action-items`
  - Query: `?note_id=number` (optional filter)
  - Returns: `[{ id, note_id, text, done, created_at }]`
- `POST /action-items/{id}/done`
  - Body: `{ "done": boolean }`
  - Returns: `{ id, done }`

### Action Items (LLM)
- `POST /action-items/extract-llm`
  - Body: `{ "text": string, "save_note"?: boolean }`
  - Uses OpenAI with structured outputs to produce items; optionally persists the note and items.
  - Returns: `{ note_id?: number, items: [{ id, text }] }`

## Data Model
- `notes(id, content, created_at)`
- `action_items(id, note_id, text, done, created_at)`

## Frontend
- Paste notes into the textarea and click:
  - "Extract" → heuristic extractor (`/action-items/extract`)
  - "Extract with LLM" → LLM extractor (`/action-items/extract-llm`)
  - "List Notes" → fetches all notes (`/notes`)
- Each extracted item renders with a checkbox; toggling calls `POST /action-items/{id}/done`.

## Tests
Run all tests from project root:
```bash
poetry run pytest -q
```
Notes:
- LLM tests are skipped if `OPENAI_API_KEY` is not set.
- Heuristic extractor tests always run.

## Configuration
- `OPENAI_API_KEY` (optional) for LLM extraction. `.env` supported at project root.
