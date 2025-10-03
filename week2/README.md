<!-- generated with user guidance and a touch of editing -->
## Action Item Extractor (Week 2)

### Overview
This project is a minimal FastAPI application with a lightweight HTML frontend to extract actionable items from freeform notes.

- Heuristic extraction identifies bullets, checkboxes, keywords (e.g., `todo:`), and imperative lines.
- LLM-powered extraction uses an Ollama model to reason about candidate actions and returns structured items.
- Notes can be saved, listed, and deleted; rendering preserves original line breaks for legibility.

### Tech Stack
- Backend: FastAPI, SQLite
- Frontend: Static HTML/JS
- LLM: Ollama (configurable via `OLLAMA_MODEL`), I used llama3.1:8b to run the tests and the page
- Tests: pytest

### Setup
1) Clone and enter the project directory
```bash
gh repo clone saladtong/modern-software-dev-assignments
cd modern-software-dev-assignments/week2
```

2) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

3) Install Python dependencies
```bash
pip install fastapi uvicorn pydantic pytest python-dotenv ollama
```

4) (Optional) Configure environment
```bash
export OLLAMA_MODEL=llama3.1:8b
```

5) Start Ollama (for LLM endpoint)
```bash
ollama serve >/dev/null 2>&1 &
ollama pull ${OLLAMA_MODEL:-llama3.1:8b}
```

6) Run the app
```bash
uvicorn app.main:app --reload
# Visit http://localhost:8000/
```

### API

Base URL: `http://localhost:8000`

- Notes
  - `POST /notes` → Create note
    - Body: `{ "content": "<text>" }`
    - Returns: `{ id, content, created_at }`
  - `GET /notes` → List notes (reverse chronological)
    - Returns: `[{ id, content, created_at }, ...]`
  - `GET /notes/{note_id}` → Get single note
    - Returns: `{ id, content, created_at }`
  - `DELETE /notes/{note_id}` → Delete a note and related action items
    - Returns: `{ deleted: true, id }`

- Action Items
  - `POST /action-items/extract` → Heuristic extraction
    - Body: `{ "text": "<notes>", "save_note": bool }`
    - Returns: `{ note_id?: number, items: [{ id, text }] }`
  - `POST /action-items/extract-llm` → LLM-powered extraction
    - Requires Ollama running and a model available
    - Body: `{ "text": "<notes>", "save_note": bool }`
    - Returns: `{ note_id?: number, items: [{ id, text }] }`
  - `POST /action-items/{id}/done` → Mark an action item done/undone
    - Body: `{ "done": true|false }`
    - Returns: `{ id, done }`

### Frontend
- Open `http://localhost:8000/` to use the embedded UI.
- Buttons
  - Extract: heuristic extraction
  - Extract LLM!: LLM extraction (Ollama required)
  - List Notes: show saved notes with Delete buttons
- Notes render with preserved line breaks (`white-space: pre-wrap`).

### Running Tests
```bash
cd week2
pytest -q
# Run a single test
pytest -q tests/test_extract.py -k test_extract_imperative_lines_without_markers
```

### Troubleshooting
- LLM 404 (model not found): pull or set `OLLAMA_MODEL` and restart the app.
- Buttons not visible: hard-refresh (Cmd+Shift+R) to bypass cached HTML.
- SQLite file: stored in `data/app.db`; created automatically on startup.


