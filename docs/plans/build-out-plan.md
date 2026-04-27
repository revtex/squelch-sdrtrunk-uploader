# squelch-sdrtrunk-uploader — Build-Out Plan

> Roadmap for taking the repo from scaffolding to v1.0.0. Updated as phases
> land. See `.github/copilot-instructions.md` for project conventions.

## Goal

Take the current scaffolding (CI-green, no real upload logic) to a v1.0.0
release: a working Java SDRTrunk plugin and a working Python file-watch shim,
both producing wire-identical multipart uploads to a Squelch
`/api/v1/calls` endpoint.

## Phase 0 — Scaffolding (DONE)

- ✅ Repo created, GPL-3.0, dev branch, CI green
- ✅ Java skeleton (Gradle Kotlin DSL, JDK 21, JUnit 5, plugin source stub + 2 tests)
- ✅ Python skeleton (pyproject + watch.py with filename parser + 6 pytest tests)
- ✅ Devcontainer, copilot-instructions, expert agents, this plan

## Phase J-1 — Pin SDRTrunk SPI

- Identify SDRTrunk's plugin SPI surface — read SDRTrunk source for the
  exact interfaces a third-party plugin loads against
- Pin to a SDRTrunk release tag
- Vendor / depend on the SPI artifact (Maven coordinates if SDRTrunk
  publishes; otherwise vendor under `plugin/src/main/java/io/squelch/sdrtrunk/spi/vendored/`)
- Add `THIRD_PARTY_NOTICES.md` listing SDRTrunk's license (GPL-3.0 — compatible)
- **Validation:** Gradle build resolves the SPI dep

## Phase J-2 — Plugin lifecycle & call listener

- Implement the SDRTrunk plugin entry point (`Plugin` interface or whatever
  SDRTrunk requires)
- Register an audio-segment listener that fires when SDRTrunk completes
  recording a call
- Read upload server URL + API key from the plugin config (plugin-specific
  preferences API; env-var fallback for `SQUELCH_API_KEY`)
- JUnit: a fake call event triggers the upload-build path

## Phase J-3 — Multipart upload

- On call-complete, build a multipart body matching the
  [native-API plan §5](https://github.com/revtex/OpenScanner/blob/dev/docs/plans/native-api-design-plan.md#5-multipart-call-upload-field-map)
- Use Java 11+ `HttpClient` with `HttpRequest.BodyPublishers` + a small
  `MultipartBodyBuilder` helper
- Convert SDRTrunk's `ZonedDateTime` → RFC 3339 `Z` (UTC, ISO_INSTANT format)
- Reject files >50 MiB before opening the connection
- JUnit with a fake `HttpUploader` asserts every field name + value

## Phase J-4 — Worker pool & retry

- `ExecutorService` (fixed thread pool, count from config, default 2)
- Bounded queue with drop-oldest policy on overflow (WARN log)
- Retry: 3 attempts, exp backoff (1s, 2s, 4s, jitter ±20%)
- Graceful shutdown on plugin unload
- The SPI thread (which calls our entry points) never blocks — all work
  goes onto the queue

## Phase J-5 — Release plumbing

- GitHub Actions release workflow on tag `v*`:
  - Build fat JAR via `./gradlew shadowJar`
  - Upload to GitHub Releases with checksum
- Release notes drawn from CHANGELOG.md `[Unreleased]` section
- Compatibility matrix in README.md updated by the release PR

## Phase S-1 — Watchdog event handler in shim

- Currently `parse_recording_filename()` exists but no actual file-watch
- Add a `Watcher` class wrapping `watchdog.Observer` that:
  - Watches a configurable directory
  - On `on_moved` / `on_created`, queues the file for upload
  - Implements "stable size for N seconds" check before triggering upload
- pytest with `PollingObserver` (deterministic) under `tmp_path`

## Phase S-2 — Real upload in shim

- Add `send_request(req: UploadRequest) -> UploadResult` that POSTs via
  `requests.Session` with timeouts and retries
- pytest with `responses` covers happy path + 4xx + 5xx + timeout

## Phase S-3 — Metadata sidecar support

- SDRTrunk can emit a `.json` sidecar alongside each `.mp3` with full call
  metadata (talkgroup, frequency, etc.) — preferred over filename parsing
- If a sidecar exists, prefer it. Fall back to filename parsing.
- pytest covers both paths

## Phase S-4 — Failed-file quarantine + systemd packaging

- On final retry failure, rename the file to `.failed.mp3` so the operator
  can inspect (rather than losing data)
- Document a systemd unit file template under `shim/contrib/systemd/`
- Document Docker recipe under `shim/contrib/docker/`

## Phase X — Wire-contract cross-check (CI)

- Once both formats render real multipart bodies:
  - Add `tools/diff_wire.py` that runs the Java plugin's JUnit dump output
    and the shim's pytest dump output through a normalizer
  - CI job `wire-contract-diff` fails on mismatch
- Use the **Wire Contract Expert** agent to audit before tagging v1.0.0

## v1.0.0 acceptance

- Java plugin successfully uploads a real recording from a SDRTrunk install
  to a Squelch dev server
- Python shim does the same, watching SDRTrunk's recording directory
- Both produce identical multipart bodies for the same fixture
- Compatibility matrix in README pinned to a tested SDRTrunk + Squelch combo
- Documentation in `plugin/README.md` and `shim/README.md` covers install,
  config, troubleshooting

## Out of scope for v1.x

- Live transcription (Squelch handles that server-side)
- Multi-server fan-out (one plugin → one Squelch server; users wanting
  multiple can use Squelch's downstream feature)
- SDRTrunk's PlaylistManager integration (we just upload, we don't manage
  SDRTrunk's playlists)
