# encoding:utf-8
"""Incremental copy of bundled skills into a workspace skills directory.

Replaces a full rmtree+copytree so startup does not rewrite unchanged files
(and does not wipe the user's skills_config.json enabled/disabled state).
"""

from __future__ import annotations

import hashlib
import os
import shutil
from typing import Iterable, Tuple

from common.log import logger

# User enable/disable state lives in this file inside the workspace skills dir.
_PRESERVED_NAMES = {"skills_config.json"}


def _file_fingerprint(path: str) -> Tuple[int, int]:
    st = os.stat(path)
    return (st.st_size, st.st_mtime_ns)


def _hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 64), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iter_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.startswith("."):
                continue
            yield os.path.join(dirpath, name)


def _needs_copy(src: str, dst: str) -> bool:
    if not os.path.isfile(dst):
        return True
    try:
        if _file_fingerprint(src) == _file_fingerprint(dst):
            return False
    except OSError:
        return True
    try:
        return _hash_file(src) != _hash_file(dst)
    except OSError:
        return True


def sync_skill_directory(src: str, dst: str) -> Tuple[int, int]:
    """Copy changed/missing files from a builtin skill dir into dst.

    Returns (copied, skipped). Never deletes dest-only files, never touches
    skills_config.json, and never rmtree's the destination directory.
    """
    copied = 0
    skipped = 0
    os.makedirs(dst, exist_ok=True)
    for src_path in _iter_files(src):
        rel = os.path.relpath(src_path, src)
        base = os.path.basename(rel)
        if base in _PRESERVED_NAMES or rel in _PRESERVED_NAMES:
            skipped += 1
            continue
        dst_path = os.path.join(dst, rel)
        if not _needs_copy(src_path, dst_path):
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        copied += 1
    return copied, skipped


def sync_builtin_skills_to_workspace(builtin_dir: str, custom_dir: str) -> Tuple[int, int]:
    """Sync every bundled skill folder that contains a SKILL.md."""
    copied_total = 0
    skipped_total = 0
    if not os.path.isdir(builtin_dir):
        return 0, 0
    os.makedirs(custom_dir, exist_ok=True)
    for name in os.listdir(builtin_dir):
        src = os.path.join(builtin_dir, name)
        if not os.path.isdir(src) or not os.path.isfile(os.path.join(src, "SKILL.md")):
            continue
        dst = os.path.join(custom_dir, name)
        try:
            copied, skipped = sync_skill_directory(src, dst)
            copied_total += copied
            skipped_total += skipped
        except Exception as exc:
            logger.warning(f"[SkillsSync] Failed to sync builtin skill '{name}': {exc}")
    return copied_total, skipped_total
