"""
utils.py
--------
Shared utilities: logging configuration and small I/O helpers.
Addresses the non-functional 'logging/monitoring' and 'maintainability'
requirements by centralizing setup instead of repeating it per module.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "scanner.log", verbose: bool = False) -> None:
    """Configure root logger to write to both console and a log file."""
    level = logging.DEBUG if verbose else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


def is_supported_image(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS
