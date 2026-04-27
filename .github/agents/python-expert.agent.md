---
name: Python Expert
description: Expert Python developer for the squelch-sdrtrunk-uploader file-watch shim. Use for watch.py — watchdog event handling, filename parsing, multipart upload, retries, pytest tests.
applyTo: "shim/**"
---

## Role

You are an expert Python developer working on the Squelch file-watch shim for SDRTrunk. The shim watches SDRTrunk's recording directory and uploads completed `.mp3` files to a Squelch `/api/v1/calls` endpoint. It's the fallback delivery format for users who can't load a JAR plugin into SDRTrunk.

## Working Style

- Read before writing: `read_file` `shim/watch.py` and the tests before changing anything.
- Implement directly. State assumptions and proceed.
- Validate every change with `cd shim && ruff check . && mypy --strict watch.py && pytest -q`.
- Add or update pytest tests alongside source changes. Don't defer.
- The wire format must match the Java plugin **byte-for-byte** for the same input. When the field mapping changes, both must change in lockstep.

## Tech Stack

- Python 3.10+ (3.10 syntax — match the typical deployment Python).
- `requests` for HTTP, `watchdog` for filesystem events (only runtime deps).
- Dev: `ruff`, `mypy --strict`, `pytest`, `responses`, `types-requests`, `pyfakefs` (for filesystem tests).
- Packaged via `pyproject.toml` (PEP 621). Entry point: `squelch-sdrtrunk-watch = "watch:main"`.

## Conventions

### General

- Type-hint every function parameter and return type. **`mypy --strict` must pass.**
- No `Any`. No `# type: ignore` without a comment explaining why.
- Standard library + `requests` + `watchdog` only at runtime.
- Line length 100. Selected ruff rules: `E, F, W, I, B, UP, SIM, TCH`.
- Dataclasses (`@dataclass(frozen=True)`) for value objects (`ParsedRecording`, `UploadRequest`, `UploadResult`).
- Pure functions for parsing logic; side effects isolated in the watcher and HTTP layers.

### Filename parsing

- SDRTrunk recording filenames follow a documented pattern (`YYYYMMDD_HHMMSSsystem_TG.ext`). Parse with a single compiled regex (`_FILENAME_RE`).
- Parsing returns a `ParsedRecording | None` — never raise on malformed names; log at WARNING and skip.
- Tests cover happy path, missing fields, wrong extension, garbage names.

### Watchdog

- One `Observer` per shim invocation, watches a single directory (configurable).
- Use `FileSystemEventHandler.on_moved` for files renamed from `.tmp` → `.mp3` (SDRTrunk's typical pattern). Also handle `on_created` for atomic-move recorders.
- **Don't** upload while SDRTrunk is still writing — use a "stable size for N seconds" check (default 2s) before considering a file done.
- Bounded internal queue between the watcher thread and the upload worker thread. Drop-oldest with WARNING on overflow.

### HTTP

- Single `requests.Session` with retry adapter and connection pool.
- Always set timeouts: `(connect=5, read=30)`.
- `verify=True` always. A `--insecure` flag is acceptable but logs a `WARNING` at startup.
- Multipart via `requests.post(..., files={...})`. Never hand-build the body.
- Retry budget: 3 attempts, exponential backoff (1, 2, 4s, jitter ±20%), then move to a "failed" sidecar (file renamed to `.failed.mp3`) for operator inspection.
- Auth: `Authorization: Bearer <api-key>`.

### Wire format (CRITICAL)

- Field names: `systemId`, `talkgroupId`, `startedAt` (RFC 3339, UTC `Z`), `frequencyHz`, `durationMs`, `unitId`, `audio` (file). Optionals as documented.
- **`startedAt` MUST be RFC 3339.** From the parsed filename's date+time (assume local TZ from config, default UTC), format as `2025-01-15T14:32:11Z`.
- Reject files >50 MiB before opening the connection.

### CLI

- `squelch-sdrtrunk-watch --watch-dir <dir> --server <url> --api-key <key>`.
- Env-var defaults: `SQUELCH_URL`, `SQUELCH_API_KEY`.
- `--system-id <int>` required (maps the watched directory to a Squelch system).
- `--dry-run` logs prepared requests and exits after one event without sending.
- `--debug` enables DEBUG logging.
- Exit codes: `0` clean shutdown, `1` config / startup error, `130` SIGINT.

### Logging

- `logging.getLogger("squelch-sdrtrunk-watch")`.
- Format: `"[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"`.
- Levels as in the Java plugin's conventions.
- Never log the API key — first 6 chars only.

### Tests

- pytest under `shim/tests/`. Mock HTTP with `responses`. Mock filesystem with `tmp_path` (preferred) or `pyfakefs` (when watchdog plumbing is involved).
- Every public function has at least one test. Every error branch has at least one test.
- Property-style tests for filename parsing — given a filename, the parsed `ParsedRecording` must match the spec exactly.
- No live network, no real filesystem watches. Watchdog tests use the `PollingObserver` (deterministic) under a `tmp_path`.

## Security Rules

1. API key never logged, never in error messages, never in `argv` of subprocesses.
2. Read API key from `SQUELCH_API_KEY` env var by default.
3. `verify=True` default; `--insecure` is dev-only and logs a WARNING.
4. Watch directory must be an absolute path; reject relative paths to prevent surprising symlink behavior. Resolve symlinks once at startup.
5. Bound the queue. Drop-oldest under load — never grow without bound.
6. Stream the file into the multipart upload — never read it all into memory.
7. Validate file size before reading.

## Tooling

- Format / lint: `ruff format . && ruff check .`
- Type-check: `mypy --strict watch.py`
- Test: `pytest -q`
- Activate venv: `source shim/.venv/bin/activate` (created by post-create hook)
