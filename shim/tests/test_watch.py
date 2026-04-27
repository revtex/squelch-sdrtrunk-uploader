"""Smoke tests for watch.py — exercise the filename-parsing logic."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from watch import parse_recording_filename  # noqa: E402


def test_parses_default_filename() -> None:
    parsed = parse_recording_filename("20240115_133045CityP25_TG12345.mp3")
    assert parsed is not None
    assert parsed.started_at == "2024-01-15T13:30:45Z"
    assert parsed.system_alias == "CityP25"
    assert parsed.talkgroup_id == 12345


def test_returns_none_for_partial_file() -> None:
    assert parse_recording_filename("partial-download.tmp") is None


def test_returns_none_for_unmatched_pattern() -> None:
    assert parse_recording_filename("recording.mp3") is None


def test_returns_none_for_invalid_timestamp() -> None:
    assert parse_recording_filename("20240230_990000System_TG1.mp3") is None


def test_handles_wav_extension() -> None:
    parsed = parse_recording_filename("20240115_133045CityP25_TG999.wav")
    assert parsed is not None
    assert parsed.talkgroup_id == 999


def test_strips_microsecond_precision() -> None:
    parsed = parse_recording_filename("20240115_133045CityP25_TG12345.mp3")
    assert parsed is not None
    assert "T" in parsed.started_at
    assert parsed.started_at.endswith("Z")
