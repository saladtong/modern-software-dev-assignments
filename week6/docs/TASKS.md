## Advanced Tasks

### 1) Optimistic concurrency control (OCC) with ETags/versions
- Add a `version` integer column to `Note` and `ActionItem` that auto-increments on update.
- Expose `ETag` headers on reads; require `If-Match` on `PUT/PATCH`, return 412 on version mismatch.
- Add tests simulating concurrent updates to ensure conflicts are detected.

### 2) Soft deletes with restore
- Add `deleted_at` timestamp to both entities; default queries exclude soft-deleted rows.
- Endpoints: `DELETE /notes/{id}` and `POST /notes/{id}/restore` (same for action items).
- Add tests ensuring soft-deleted rows don’t appear in lists, and can be restored.

### 3) Real-time updates over WebSocket
- Add `/ws` broadcasting create/update/delete events for notes and action items.
- Push minimal payloads `{ entity: 'note'|'action', op: 'create'|'update'|'delete', data: {...} }`.
- Frontend: subscribe and live-update lists. Add a lightweight test for the WS endpoint.

### 4) Background extraction pipeline
- On note creation, enqueue a background task that runs extraction and persists derived action items (flag to disable in tests).
- Add a `POST /notes/{id}/reprocess` endpoint to re-run the pipeline manually.
- Tests: verify background task behavior deterministically using dependency override.

### 5) API keys and rate limiting
- Add simple API key auth via header `X-API-Key` with keys stored in SQLite.
- Implement per-key rate limiting (sliding window) for write endpoints; return 429 on limit.
- Tests for allowed vs throttled scenarios and missing/invalid keys.

### 6) Full‑text search (FTS5) for notes
- Create an FTS5 virtual table mirroring notes content; maintain via triggers.
- Implement `GET /notes/search?q=...` using FTS with ranking (`bm25`) and snippet.
- Tests for ranking order, special characters, and empty queries.

### 7) Response caching and cache invalidation
- Add ETag-based caching to list endpoints and `Cache-Control` headers.
- Invalidate/rotate ETags on create/update/delete affecting each collection.
- Tests confirming cache hits/misses and invalidation paths.

### 8) Database migrations with Alembic
- Initialize Alembic and create migrations for new columns (`version`, `deleted_at`) and FTS objects.
- Document upgrade/downgrade workflow in `README.md`; add CI step to run migrations.
- Tests: migrate an existing DB forward/backward without data loss.

### 9) Observability and health
- Add structured request logging middleware and a `/healthz` endpoint.
- Expose Prometheus metrics (e.g., via `starlette_exporter`); include request latency and error counts.
- Tests validate health and that metrics endpoint returns expected series.

### 10) Data validation and sanitization
- Enforce stricter Pydantic constraints (min/max lengths, trimmed strings) and HTML sanitization for note content.
- Return consistent error envelopes and status codes.
- Tests for validation failures and sanitized output.

### 11) Multi‑tenant scoping
- Add `workspace_id` column to models and scope all queries by a required `X-Workspace-ID` header.
- Prevent cross-tenant access; ensure indexes include `workspace_id`.
- Tests proving isolation between tenants.

### 12) Idempotency for POST
- Support `Idempotency-Key` header for create endpoints; deduplicate within a window.
- Store request hash and response reference; return the same result on retries.
- Tests for duplicate submission scenarios.

### 13) Bulk export/import (NDJSON)
- Endpoints: `GET /export.ndjson` (streaming) and `POST /import?dry_run=true|false`.
- Validate records, report per-record errors on dry-run, and transactional import on apply.
- Tests for large datasets and partial failure cases.
