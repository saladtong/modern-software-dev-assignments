# Tasks for Repo



## 1) Enable pre-commit and fix the repo
- Install hooks: `pre-commit install`
- Run: `pre-commit run --all-files`
- Fix any formatting/lint issues (black/ruff)

## 2) Add search endpoint for notes
- Add/extend `GET /notes/search?q=...` (case-insensitive) using SQLAlchemy filters
- Update `frontend/app.js` to use the search query
- Add tests in `backend/tests/test_notes.py`

## 3) Complete action item flow
- Implement `PUT /action-items/{id}/complete` (already scaffolded)
- Update UI to reflect completion (already wired) and extend test coverage

## 4) Improve extraction logic
- Extend `backend/app/services/extract.py` to parse tags like `#tag` and return them
- Add tests for the new parsing behavior
- (Optional) Expose `POST /notes/{id}/extract` that turns notes into action items

## 6) Coverage and local quality gates
- Add `pytest-cov` to deps and run with coverage threshold (e.g., 80%)
- Enforce via a Makefile target; later you can wire this into CI via Claude

## 7) Docs drift check (manual for now)
- Create/maintain a simple `API.md` describing endpoints and payloads

