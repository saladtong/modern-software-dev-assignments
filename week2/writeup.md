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
TODO
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
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