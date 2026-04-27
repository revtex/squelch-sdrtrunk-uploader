# Squelch Java plugin for SDRTrunk

Status: **scaffolding**. The Gradle project builds an empty JAR with the right identity; SDRTrunk SPI bindings come in a later release.

## Build

```bash
./gradlew build
```

Requires JDK 21.

## Roadmap

- [ ] Pin SDRTrunk SPI version (waiting on SDRTrunk to publish to Maven Central or a self-hosted Maven repo)
- [ ] Implement `Plugin` SPI bindings: register an audio-call listener
- [ ] Build a multipart POST against `/api/v1/calls`
- [ ] Bounded worker queue with retry/backoff
- [ ] Per-arch GitHub Releases (`squelch-sdrtrunk-X.Y.Z.jar`)

Until the Java plugin is ready, use the [filesystem watcher shim](../shim/) which provides equivalent functionality outside of SDRTrunk's process.
