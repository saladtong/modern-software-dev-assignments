# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
@extract.py I'm trying to implement extract_action_items_llm and I want to use ollama to take in text and extract action items from it to form a todo list.
``` 

Generated Code Snippets:
```
def extract_action_items_llm(text: str) -> List[str]:
    text = text or ""
    if not text.strip():
        return []

    # Allow overriding the model via env; choose a lightweight default
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")

    # JSON schema for structured output. We ask for an object with a single
    # property `items` that is an array of strings.
    schema: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "items": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["items"],
    }

    system_prompt = (
        "You are an expert at extracting concrete, actionable TODO items from notes. "
        "Return only valid JSON that conforms to the provided schema. "
        "Items should be concise, imperative, and deduplicated."
    )
    user_prompt = (
        "Extract action items from the following notes. "
        "Ignore narrative text that is not an action item.\n\n"
        f"NOTES:\n{text}"
    )

    response_content: str | None = None
    try:
        # Prefer structured outputs if supported by the installed Ollama version
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # Ollama supports `format` for JSON/JSON Schema structured outputs.
            # See: https://ollama.com/blog/structured-outputs
            format={
                "type": "json_schema",
                "json_schema": {
                    "name": "action_items",
                    "schema": schema,
                },
            },
            options={"temperature": 0},
        )
        # Expected shape: { "message": { "content": "{...json...}" }, ... }
        response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
    except Exception:
        # Fallback: request plain JSON (array) without schema enforcement
        fallback_user_prompt = (
            "Extract action items from the following notes and return ONLY a JSON "
            "object with an `items` array of strings (no preface, no trailing text).\n\n"
            f"NOTES:\n{text}"
        )
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": fallback_user_prompt},
            ],
            options={"temperature": 0},
        )
        response_content = response.get("message", {}).get("content")  # type: ignore[assignment]

    items: List[str] = []
    if response_content:
        # Try parsing as an object with `items`, but also handle if the model
        # returns a bare array.
        # Processing the json
        try:
            parsed = json.loads(response_content)
            if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                items = [str(x).strip() for x in parsed["items"] if str(x).strip()]
            elif isinstance(parsed, list):
                items = [str(x).strip() for x in parsed if str(x).strip()]
        except json.JSONDecodeError:
            # Last resort: extract lines that look like list items
            for line in response_content.splitlines():
                candidate = BULLET_PREFIX_PATTERN.sub("", line).strip()
                if candidate:
                    items.append(candidate)

    # Normalize & deduplicate
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(cleaned)

    return unique
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in week2/tests/test_extract.py.
``` 

Generated Code Snippets:
```
4 from ..app.services.extract import extract_action_items, extract_action_items_llm

# starting at line 22
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

```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
Perform a refactor of the code and the tests in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling. Make sure nothing breaks in this step.
``` 

Generated/Modified Code Snippets:
```

#starting line 17 of main.py
@app.on_event("startup")
def on_startup() -> None:
    init_db()

#line 9 action_items.py
from ..schemas import (
    ActionExtractRequest,
    ActionExtractResponse,
    ActionItemListItem,
    ActionItemResponse,
)

#20
@router.post("/extract", response_model=ActionExtractResponse)
def extract(payload: ActionExtractRequest) -> ActionExtractResponse:
    text = payload.text.strip()

#26
    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = db.insert_note(text)

#31
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

#43
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

#61
    @router.post("/{action_item_id}/done", response_model=Dict[str, Any])

#63 
    try:
        done = bool(payload.get("done", True))
        db.mark_action_item_done(action_item_id, done)
        return {"id": action_item_id, "done": done}
    except Exception:
        raise HTTPException(status_code=500, detail="failed to mark done")            


# notes.py line 8
from ..schemas import NoteCreate, NoteResponse

#14
@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreate) -> NoteResponse:
    content = payload.content.strip()

#19
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

#31
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


# schemas starting at line 1
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




```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.

Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.

Leave comments as you go.
``` 

Generated Code Snippets:
```
# action_items.py line 8
from ..services.extract import extract_action_items, extract_action_items_llm

#44
@router.post("/extract-llm", response_model=ActionExtractResponse)
def extract_llm(payload: ActionExtractRequest) -> ActionExtractResponse:
    # LLM-powered extraction endpoint
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = db.insert_note(text)

        # Use LLM-based extractor
        items = extract_action_items_llm(text)
        ids = db.insert_action_items(items, note_id=note_id)
        return ActionExtractResponse(
            note_id=note_id,
            items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="failed to extract action items with LLM")


# notes.py line 44

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


# index.html line 27
      <button id="extract_llm">Extract LLM</button>
      <button id="list_notes">List Notes</button>

# line 37
      const btnLLM = $('#extract_llm');
      const btnListNotes = $('#list_notes');

      // Helper to render action items
      function renderItems(data) {
        if (!data.items || data.items.length === 0) {
          itemsEl.innerHTML = '<p class="muted">No action items found.</p>';
          return;
        }
        itemsEl.innerHTML = data.items.map(it => (
          `<div class="item"><input type="checkbox" data-id="${it.id}" /> <span>${it.text}</span></div>`
        )).join('');
        itemsEl.querySelectorAll('input[type="checkbox"]').forEach(cb => {
          cb.addEventListener('change', async (e) => {
            const id = e.target.getAttribute('data-id');
            await fetch(`/action-items/${id}/done`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ done: e.target.checked }),
            });
          });
        });
      }

      // Heuristic extract
      btn.addEventListener('click', async () => {
        const text = $('#text').value;
        const save = $('#save_note').checked;
        itemsEl.textContent = 'Extracting...';
        try {
          const res = await fetch('/action-items/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, save_note: save }),
          });
          if (!res.ok) throw new Error('Request failed');
          const data = await res.json();
          renderItems(data);

#81

      // LLM extract
      btnLLM.addEventListener('click', async () => {
        const text = $('#text').value;
        const save = $('#save_note').checked;
        itemsEl.textContent = 'Extracting with LLM...';
        try {
          const res = await fetch('/action-items/extract-llm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, save_note: save }),
          });
          if (!res.ok) throw new Error('Request failed');
          const data = await res.json();
          renderItems(data);
        } catch (err) {
          console.error(err);
          itemsEl.textContent = 'Error extracting items with LLM';
        }
      });

      // List notes
      btnListNotes.addEventListener('click', async () => {
        itemsEl.textContent = 'Loading notes...';
        try {
          const res = await fetch('/notes');
          if (!res.ok) throw new Error('Request failed');
          const data = await res.json();
          if (!Array.isArray(data) || data.length === 0) {
            itemsEl.innerHTML = '<p class="muted">No notes found.</p>';
            return;
          }
          itemsEl.innerHTML = data.map(n => (
            `<div class="item"><span class="muted">#${n.id}</span> <span>${n.content}</span></div>`
          )).join('');
        } catch (err) {
          console.error(err);
          itemsEl.textContent = 'Error loading notes';
        }
      });


# extract.py line 131
        try:
            response = chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": fallback_user_prompt},
                ],
                options={"temperature": 0},
            )
            response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
        except Exception:
            # If Ollama is unavailable or model pull fails, fall back to heuristic extractor
            return extract_action_items(text)

#176
    # If LLM returned nothing useful, fall back to heuristic extractor
    if not unique:
        return extract_action_items(text)

# extract.py 157
        # Strip code-fence wrappers like ```json ... ``` if present
        fenced = response_content.strip()
        if fenced.startswith("```") and fenced.endswith("```"):
            try:
                inner = fenced.strip("`")
                if inner.lower().startswith("json\n"):
                    inner = inner.split("\n", 1)[1]
                response_content = inner
            except Exception:
                pass

# line 91
    # Improved guidance with few-shot examples and candidate grounding
    system_prompt = (
        "You extract concrete TODO items from messy notes. "
        "Rules: return ONLY JSON per schema; write items in imperative mood; deduplicate; "
        "exclude dates, names, and narrative unless essential; keep each item concise (<= 15 words)."
    )
    candidate_items = extract_action_items(text)
    examples = (
        "Examples:\n"
        "Input: '- [ ] Set up database' -> 'Set up database'\n"
        "Input: 'todo: update docs' -> 'update docs'\n"
        "Input: 'Discuss architecture tradeoffs' -> (exclude)\n"
    )
    user_prompt = (
        "Extract action items from the notes below. Prefer cleaning from CANDIDATES; "
        "include additional items only if clearly implied.\n\n"
        f"{examples}\n"
        f"CANDIDATES: {json.dumps(candidate_items)}\n\n"
        f"NOTES:\n{text}"
    )                

#line 113
    # Strategy 1: simple JSON forcing (format="json") for maximum compatibility
    try:
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + "\n\nOutput as {\"items\": [\"...\"]} only."},
            ],
            format="json",
            options={"temperature": 0},
        )
        response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
    except Exception:
        response_content = None

    # Strategy 2: JSON Schema structured outputs (if supported)
    if not response_content:
        try:
            response = chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "action_items",
                        "schema": schema,
                    },
                },
                options={"temperature": 0},
            )
            response_content = response.get("message", {}).get("content")  # type: ignore[assignment]
        except Exception:
            response_content = None

    # Strategy 3: plain prompt with explicit JSON instruction
    if not response_content:
        fallback_user_prompt = (
            "Extract action items and return ONLY a JSON object: {\\"items\\": [\\"...\\"]}. "
            "No prose.\n\n" f"NOTES:\n{text}"

```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 