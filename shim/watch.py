"""
SDRTrunk filesystem-watcher shim for Squelch.

Status: scaffolding. SDRTrunk writes completed calls to its ``recordings``
directory as ``YYYYMMDD_HHMMSSsystem_TG.mp3`` (or ``.wav``) plus an adjacent
metadata file. This shim watches that directory and uploads each completed
file to Squelch's ``/api/v1/calls`` endpoint.

The actual filesystem-watch loop and POST are not yet wired — :func:`parse_recording_filename`
is exercised by tests so the field-extraction logic is locked in before the
network plumbing is added.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("squelch-sdrtrunk-shim")

# SDRTrunk default filename: 20240115_133045System_TG12345.mp3
# (timestamp underscore SystemAlias underscore TGid extension)
_FILENAME_RE = re.compile(
    r"^(?P<ts>\d{8}_\d{6})(?P<system>[^_]+)_TG(?P<tg>\d+)\.[a-zA-Z0-9]+$"
)


@dataclass(frozen=True)
class ParsedRecording:
    """Fields extracted from an SDRTrunk recording filename."""

    started_at: str  # RFC 3339, UTC, ``Z`` suffix
    system_alias: str
    talkgroup_id: int


def parse_recording_filename(name: str) -> ParsedRecording | None:
    """Extract ``startedAt``/``systemAlias``/``talkgroupId`` from the filename.

    Returns ``None`` when the filename doesn't match SDRTrunk's default scheme,
    so the caller can skip non-recordings (logs, partial files, etc.).
    """
    m = _FILENAME_RE.match(name)
    if not m:
        return None

    raw_ts = m.group("ts")  # YYYYMMDD_HHMMSS
    try:
        dt = datetime.strptime(raw_ts, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None

    return ParsedRecording(
        started_at=dt.isoformat().replace("+00:00", "Z"),
        system_alias=m.group("system"),
        talkgroup_id=int(m.group("tg")),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Watch an SDRTrunk recordings directory and upload to Squelch",
    )
    parser.add_argument(
        "--watch",
        type=Path,
        required=True,
        help="Path to the SDRTrunk recordings directory",
    )
    parser.add_argument("--server", required=True, help="Squelch base URL")
    parser.add_argument("--api-key", required=True, help="Squelch API key")
    parser.add_argument(
        "--system-id",
        type=int,
        default=None,
        help="Squelch system ID to attach to every upload (overrides system alias parsing)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")

    if not args.watch.is_dir():
        logger.error("watch path is not a directory: %s", args.watch)
        return 1

    logger.error("filesystem watcher not yet implemented (scaffolding)")
    logger.info("would watch=%s server=%s system_id=%s", args.watch, args.server, args.system_id)
    return 2


if __name__ == "__main__":
    sys.exit(main())
