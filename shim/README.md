# Squelch filesystem-watcher shim for SDRTrunk

Status: **scaffolding**. Filename parsing is implemented and tested; the actual filesystem-watch loop and POST are TODO.

This shim watches an SDRTrunk recordings directory and uploads each completed file to Squelch. No SDRTrunk modification is required — runs as a separate process.

## Install

```bash
cd shim
pip install -e ".[dev]"
```

## Run (once the watch loop ships)

```bash
squelch-sdrtrunk-watch \
  --watch ~/SDRTrunk/recordings \
  --server https://squelch.example.com \
  --api-key 'sdr-1.<key-secret>' \
  --system-id 1
```

## systemd unit (sketch)

```ini
[Unit]
Description=Squelch SDRTrunk uploader
After=network-online.target

[Service]
Type=simple
EnvironmentFile=/etc/squelch-sdrtrunk.env
ExecStart=/usr/local/bin/squelch-sdrtrunk-watch \
  --watch %h/SDRTrunk/recordings \
  --server ${SQUELCH_URL} \
  --api-key ${SQUELCH_API_KEY} \
  --system-id ${SQUELCH_SYSTEM_ID}
Restart=on-failure

[Install]
WantedBy=default.target
```

## Roadmap

- [ ] Implement the watchdog-based filesystem watcher
- [ ] Implement the multipart POST with retry/backoff
- [ ] Honour SDRTrunk metadata sidecars (when present)
- [ ] Optional system-alias → systemId mapping file
