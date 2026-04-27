# squelch-sdrtrunk-uploader — Copilot Instructions

## Project Overview

`squelch-sdrtrunk-uploader` is the first-party SDRTrunk uploader for **Squelch** (currently developed at [revtex/OpenScanner](https://github.com/revtex/OpenScanner) — pending rename). It ships **two** delivery formats targeting Squelch's native `/api/v1/calls` endpoint:

| Format | Path | When to use |
|---|---|---|
| Java SDRTrunk plugin | [plugin/](../plugin/) | Recommended. Loads inside SDRTrunk via its plugin SPI, integrates natively into the audio pipeline. |
| Python file-watch shim | [shim/](../shim/) | Fallback. Watches SDRTrunk's recording directory and uploads completed files. Useful when the plugin SPI isn't accessible. |

Both must produce **byte-identical multipart bodies** for the same input — the field-mapping rules live in [Squelch's native-API plan §5](https://github.com/revtex/OpenScanner/blob/dev/docs/plans/native-api-design-plan.md#5-multipart-call-upload-field-map).

## Tech Stack

- **Java plugin:** JDK 21 (Temurin), Gradle (Kotlin DSL), JUnit 5.10.2, OkHttp (or Java 11 `HttpClient`) for upload.
- **Python shim:** Python 3.10+, `requests`, `watchdog` (filesystem events), ruff, mypy `--strict`, pytest, responses.
- **Dev container:** Debian bookworm with Java 21 base + Python toolchain (see [.devcontainer/Dockerfile](../.devcontainer/Dockerfile)).
- **CI:** GitHub Actions, two parallel jobs (`plugin-build`, `shim-lint`).

## Project Structure

```
plugin/                    ← Java SDRTrunk plugin (Gradle Kotlin DSL)
  build.gradle.kts
  settings.gradle.kts
  src/main/java/io/squelch/sdrtrunk/
  src/test/java/io/squelch/sdrtrunk/
shim/                      ← Python file-watch shim
  pyproject.toml
  watch.py
  tests/
docs/
  plans/                   ← committed planning docs (build-out plan, etc.)
.devcontainer/
.github/
  agents/
  workflows/ci.yml
```

## Subagent Usage — Default Behavior

**Always delegate domain work to the matching expert agent** via `runSubagent`.

| Task | Agent |
|---|---|
| Java plugin (SDRTrunk SPI, Gradle, JUnit) | **Java Expert** |
| Python shim (watchdog, mapping, CLI, tests) | **Python Expert** |
| Field-mapping correctness vs. Squelch's API | **Wire Contract Expert** |
| Read-only investigation across the codebase | **Explore** |

When a request touches both plugin and shim (e.g. "add a new field"), run **Java Expert** and **Python Expert** in parallel. Then run **Wire Contract Expert** to verify both outputs against Squelch's native upload contract.

## Coding Conventions

### Java (plugin/)

- JDK 21 — use modern features (records, pattern matching, `var`, text blocks) where they aid clarity.
- All classes in `io.squelch.sdrtrunk` package tree. SDRTrunk SPI integration in `io.squelch.sdrtrunk.spi`. Wire layer in `io.squelch.sdrtrunk.wire`. Pure value types in `io.squelch.sdrtrunk.model`.
- `final` by default. Mutability is a deliberate choice, called out with a comment.
- Records for value objects. No Lombok.
- No checked-exception abuse — wrap I/O failures in a domain exception (`UploadFailedException`) before crossing public-method boundaries.
- HTTP via Java 11+ `HttpClient` (preferred — no extra dep) or OkHttp (acceptable if SDRTrunk already ships it).
- Logging: SLF4J only. SDRTrunk uses Logback at runtime; we don't ship a binding.
- Format: Google Java Format (gradle plugin TBD). Line length 100.

### Python (shim/)

- Python 3.10+, type-hint everything, **`mypy --strict` must pass**.
- Standard library + `requests` + `watchdog` only at runtime.
- Single `requests.Session` with timeouts, retries, connection pooling.
- `ruff check .` clean; selected rules: `E, F, W, I, B, UP, SIM, TCH`.
- Tests use `responses` to mock HTTP and `tmp_path` for filesystem; no live network or absolute paths.

### Wire contract (BOTH)

- Field names: `systemId`, `talkgroupId`, `startedAt` (RFC 3339, UTC `Z`), `frequencyHz`, `durationMs`, `unitId`, `audio` (file part), and the optional set documented in the [native-API plan §5](https://github.com/revtex/OpenScanner/blob/dev/docs/plans/native-api-design-plan.md#5-multipart-call-upload-field-map).
- **Never accept unix-timestamp `startedAt`** — Squelch v1 rejects it. Convert from SDRTrunk's `ZonedDateTime` (Java) / filename timestamp (Python) to RFC 3339 `Z`.
- Auth: `Authorization: Bearer <api-key>`. Never legacy variants.
- Multipart, not JSON.
- Size limit: 50 MiB on Squelch's v1 upload route. Caller must validate before sending.

## Security Rules

1. API key is a secret. Never log it. Never echo it. Never put it in error messages, JVM properties, or process arguments.
2. Read the API key from environment variables (`SQUELCH_API_KEY`) by default — SDRTrunk plugin config and shim config files should reference the env var, not contain the key.
3. TLS verification on by default. The shim may expose `--insecure` for self-signed dev servers, with a startup warning. The Java plugin must default to `HttpClient` with the platform default trust store; never call `setSSLContext(insecure)`.
4. Bound the upload size; reject local files >50 MiB before opening a connection.
5. Bound retry budget — exponential backoff with a per-call ceiling; never retry indefinitely.
6. The plugin runs in SDRTrunk's JVM. An uncaught exception kills SDRTrunk. Wrap every external state crossing in try/catch with a logging sink; never let an exception escape into SDRTrunk's audio pipeline thread.

## Tooling Conventions

- Search: VS Code `grep_search`. In the terminal, `rg` (ripgrep). Never plain `grep`.
- File listing: `list_dir` or `file_search`.
- Validation after change: `cd plugin && ./gradlew test` for Java; `cd shim && ruff check . && mypy --strict watch.py && pytest -q` for Python.
- Do not commit or push unless the user asks.
- Version-pinning: Gradle dependency catalogs (`libs.versions.toml`) for Java once the dep set grows past 3 entries; `pyproject.toml` for Python.

## Planning docs (`docs/plans/`)

- Planning docs live under `docs/plans/` and are **committed** to the repo so contributors can follow the build-out roadmap.
- `CHANGELOG.md` bullets still describe **what changed in the product**, not which plan phase shipped — link to the plan only when it adds operator-relevant context.

## Changelog & Releases

- User-visible changes (new features, fixes, security) **must** add a bullet under `[Unreleased]` in `CHANGELOG.md`. Pure refactor / CI tweaks may skip with a `skip-changelog` PR label.
- Bullets describe **what changed in the product**, never **what plan was followed**.
- Releases are tagged `vX.Y.Z` and ship a JAR + Python sdist via GitHub Releases:
  - `squelch-sdrtrunk-uploader-X.Y.Z.jar` (Java plugin, single fat JAR)
  - `squelch-sdrtrunk-watch-X.Y.Z.tar.gz` (Python shim source dist)
- Compatibility table in `README.md` must be updated when the matching Squelch / SDRTrunk version changes.
