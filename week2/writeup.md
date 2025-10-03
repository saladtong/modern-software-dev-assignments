# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: Emily Saletan \
SUNet ID: esaletan \
Citations: Unsure, besides everything that Cursor has in its references

This assignment took me about 4 hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
@extract.py I'm trying to implement extract_action_items_llm and I want to use ollama to take in text and extract action items from it to form a todo list.
``` 

Generated Code Snippets:
```
### app/services/extract.py — LLM model default and prompt; robust parsing

```82:84:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/services/extract.py
# Allow overriding the model via env; choose a lightweight default
model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
```

```99:105:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/services/extract.py
system_prompt = (
    "You are an expert at extracting concrete, actionable TODO items from notes. "
    "Think step by step INTERNALLY to identify candidate action lines (bullets, numbered items, keyword prefixes like 'todo:'/'action:'/'next:', "
    "and sentences starting with imperative verbs such as add, create, implement, fix, update, write, check, verify, refactor, document, design, investigate). "
    "Convert phrasings like 'make sure to pay rent' to 'Pay rent'. Convert narrative like 'I have to figure out where a good study space is' to a concise action like 'Find a good study space'. "
    "OUTPUT REQUIREMENT: Return ONLY valid JSON conforming to the schema. Do not include any reasoning, commentary, or code fences."
)
```

```153:175:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/services/extract.py
# Strip code-fences like ```json ... ``` or ``` ... ``` if present
fenced = response_content.strip()
if fenced.startswith("```") and fenced.endswith("```"):
    try:
        inner = fenced.strip("`")
        if "\n" in inner:
            inner = inner.split("\n", 1)[1]
        response_content = inner
    except Exception:
        pass

# If the model mixed prose with JSON, try to isolate the first JSON object/array
content = response_content.strip()
start_obj = content.find("{"); end_obj = content.rfind("}")
start_arr = content.find("["); end_arr = content.rfind("]")
candidate_json = None
if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
    candidate_json = content[start_obj : end_obj + 1]
elif start_arr != -1 and end_arr != -1 and end_arr > start_arr:
    candidate_json = content[start_arr : end_arr + 1]
if candidate_json is None:
    candidate_json = content
```

```176:188:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/services/extract.py
# Try parsing as an object with `items`, but also handle a bare array
try:
    parsed = json.loads(candidate_json)
    if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
        items = [str(x).strip() for x in parsed["items"] if str(x).strip()]
    elif isinstance(parsed, list):
        items = [str(x).strip() for x in parsed if str(x).strip()]
except json.JSONDecodeError:
    # Last resort: extract lines that look like list items from the model output
    for line in response_content.splitlines():
        candidate = BULLET_PREFIX_PATTERN.sub("", line).strip()
        if candidate:
            items.append(candidate)
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


### app/routers/action_items.py — LLM extraction endpoint

```43:66:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/routers/action_items.py
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

        items = extract_action_items_llm(text)
        ids = db.insert_action_items(items, note_id=note_id)
        return ActionExtractResponse(
            note_id=note_id,
            items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
        )
    except HTTPException:
        raise
    except Exception as exc:
        # Surface the underlying LLM error for easier debugging
        raise HTTPException(status_code=502, detail=f"LLM extraction failed: {exc}")
```



### Exercise 2: Add Unit Tests
Prompt: 
```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in week2/tests/test_extract.py.


Add unit tests that contain lines starting with verbs, phrases like "make sure to," and content about various careers. Also add tests for lines that don't start with any bullet point, number, hyphen, or other indicators of lists



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
TODO
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint. Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.
``` 

Generated Code Snippets:
'''


### frontend/index.html — Buttons for LLM extract and list notes

```24:29:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/frontend/index.html
  <div class="row">
    <label class="row"><input id="save_note" type="checkbox" checked /> Save as note</label>
    <button id="extract">Extract</button>
    <button id="extract_llm">Extract LLM!</button>
    <button id="list_notes">List Notes</button>
  </div>
```

### frontend/index.html — LLM extract handler

```74:108:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/frontend/index.html
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
  } catch (err) {
    console.error(err);
    itemsEl.textContent = 'Error extracting items with LLM';
  }
});
```



### app/routers/notes.py — List notes endpoint

```31:41:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/routers/notes.py
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
```

### frontend/index.html — List notes (with delete and preserved formatting)

```110:147:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/frontend/index.html
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
      `<div class="item">
         <span class="muted">#${n.id}</span>
         <span style="flex:1; white-space: pre-wrap;">${n.content}</span>
         <button data-id="${n.id}" class="delete-note">Delete</button>
       </div>`
    )).join('');
    // Wire up delete buttons
    itemsEl.querySelectorAll('button.delete-note').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = e.target.getAttribute('data-id');
        try {
          const resp = await fetch(`/notes/${id}`, { method: 'DELETE' });
          if (!resp.ok) throw new Error('Delete failed');
          // Refresh list
          btnListNotes.click();
        } catch (err) {
          console.error(err);
          alert('Failed to delete note');
        }
      });
    });
  } catch (err) {
    console.error(err);
    itemsEl.textContent = 'Error loading notes';
  }
});
```


### app/routers/notes.py — Delete note endpoint

```57:69:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/routers/notes.py
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
```

### app/db.py — Delete note helper

```118:126:/Users/emilysaletan/Documents/GitHub/modern-software-dev-assignments/week2/app/db.py
def delete_note(note_id: int) -> None:
    """Delete a note and any related action items."""
    with get_connection() as connection:
        cursor = connection.cursor()
        # First remove action items linked to the note
        cursor.execute("DELETE FROM action_items WHERE note_id = ?", (note_id,))
        # Then remove the note itself
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        connection.commit()
```





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