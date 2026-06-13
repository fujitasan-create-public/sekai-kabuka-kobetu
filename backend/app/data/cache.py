"""In-memory cache for latest ticker snapshots."""
from typing import Any

# ticker -> snapshot dict
_store: dict[str, dict[str, Any]] = {}


def set_snapshot(ticker: str, snapshot: dict[str, Any]) -> None:
    _store[ticker] = snapshot


def get_snapshot(ticker: str) -> dict[str, Any] | None:
    return _store.get(ticker)


def get_all_snapshots() -> dict[str, dict[str, Any]]:
    return dict(_store)
