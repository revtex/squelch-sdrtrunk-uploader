# squelch-sdrtrunk-uploader

First-party SDRTrunk uploader for [Squelch](https://github.com/revtex/squelch) (currently developed as [revtex/OpenScanner](https://github.com/revtex/OpenScanner)). Uploads completed calls to Squelch's native `/api/v1/calls` endpoint with `Authorization: Bearer <api-key>`.

> **Status:** Scaffolding. The plugin and shim are skeletons; not yet feature-complete.

This repository ships **two** delivery formats:

| Format | Location | When to use |
|---|---|---|
| **Java SDRTrunk plugin** (`squelch-sdrtrunk-X.Y.Z.jar`) | [plugin/](plugin/) | Recommended once shipped. Loads inside SDRTrunk via its plugin SPI; integrates with the call-decoding lifecycle. |
| **Python filesystem shim** (`watch.py`) | [shim/](shim/) | Available now. Watches SDRTrunk's recordings directory and uploads completed calls. No SDRTrunk modification required. |

Both target the same wire contract: the multipart shape documented in [Squelch's native-API plan §5](https://github.com/revtex/OpenScanner/blob/dev/docs/plans/native-api-design-plan.md#5-multipart-call-upload-field-map).

## Quick install

### Filesystem shim (available now)

```bash
cd shim
pip install -e ".[dev]"

squelch-sdrtrunk-watch \
  --watch ~/SDRTrunk/recordings \
  --server https://squelch.example.com \
  --api-key 'sdr-1.<key-secret>'
```

See [shim/README.md](shim/README.md) for the systemd unit and config-file form.

### Java plugin (TBD)

```bash
cd plugin
./gradlew build
```

See [plugin/README.md](plugin/README.md).

## Compatibility

| squelch-sdrtrunk-uploader | Squelch / OpenScanner | SDRTrunk |
|---|---|---|
| `0.x` | ≥ 1.3.0 (native `/api/v1/calls`) | ≥ 0.6 (TBD, depends on SPI stability) |

## License

GPL-3.0 — matches SDRTrunk and Squelch.
