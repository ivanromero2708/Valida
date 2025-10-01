"""Utilities for normalising document and image paths."""

from __future__ import annotations

import logging
import os
from pathlib import Path, PureWindowsPath
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PRIMARY_DEFAULT_DATA_ROOT = Path("/deps/outer-Valida/Valida/src/input")
_FALLBACK_DATA_ROOT = _REPO_ROOT / "input"



def _resolve_root(env_var: str, primary: Path, fallback: Path) -> Path:
    """Resolve a root directory honouring environment overrides."""
    raw_value = os.getenv(env_var)
    if raw_value:
        candidate = Path(raw_value).expanduser()
        try:
            candidate.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.debug("Could not ensure directory for %s override '%s'", env_var, candidate)
        if not candidate.exists():
            logger.warning("%s override '%s' does not exist.", env_var, candidate)
        return candidate

    if primary.exists():
        return primary

    try:
        fallback.mkdir(parents=True, exist_ok=True)
        logger.info("Using fallback %s for %s", fallback, env_var)
        return fallback
    except Exception as exc:
        logger.warning(
            "Failed to prepare fallback path '%s' for %s: %s",
            fallback,
            env_var,
            exc,
        )
        return fallback


def _parts_without_drive(raw_path: str) -> Iterable[str]:
    """Return path parts without drive letters or leading separators."""
    pure = PureWindowsPath(raw_path)
    parts: Iterable[str] = pure.parts
    if pure.drive:
        parts = parts[1:]
    return [p for p in parts if p not in ("", "/", "\\")]


_DATA_ROOT = _resolve_root("DATA_ROOT", _PRIMARY_DEFAULT_DATA_ROOT, _FALLBACK_DATA_ROOT)
_IMAGES_ROOT = _resolve_root("IMAGES_ROOT", _DATA_ROOT / "images", _FALLBACK_DATA_ROOT / "images")


def get_data_root() -> Path:
    """Return the configured data root."""
    return _DATA_ROOT


def get_images_root() -> Path:
    """Return the configured images root."""
    return _IMAGES_ROOT


def resolve_input_path(raw: Optional[str | Path], *, data_root: Optional[Path] = None) -> Optional[Path]:
    """Normalise an incoming path against the configured data root."""
    if raw is None:
        return None

    raw_str = str(raw).strip().strip('"').strip("'")
    if not raw_str:
        return None

    candidate = Path(raw_str).expanduser()
    if candidate.exists():
        return candidate

    root = data_root or get_data_root()
    parts = list(_parts_without_drive(raw_str.replace("\\", "/")))

    if parts:
        resolved = root.joinpath(*parts)
    else:
        resolved = root / Path(raw_str).name

    if resolved.exists():
        return resolved

    basename_candidate = root / Path(raw_str).name
    if basename_candidate.exists():
        return basename_candidate

    return resolved
