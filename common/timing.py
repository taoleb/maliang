# encoding:utf-8
"""Cheap, always-on first-turn / run timing logs.

Lines are written at INFO with a ``[Timing]`` prefix so they land in run.log
without extra configuration.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from common.log import logger


def start() -> float:
    return time.perf_counter()


def elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def log(event: str, **fields: Any) -> None:
    parts = [f"[Timing] {event}"]
    for key, value in fields.items():
        if value is None:
            continue
        parts.append(f"{key}={value}")
    logger.info(" ".join(parts))
