from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AttemptWorkspace:
    root: Path
    patch_file: Path

    def cleanup(self) -> None:
        shutil.rmtree(self.root.parent, ignore_errors=True)


def _reject_symlinks(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"benchmark fixture contains forbidden symlink: {path}")


def create_workspace(case_dir: Path, patch: str) -> AttemptWorkspace:
    source = case_dir / "repo"
    if not source.is_dir():
        raise ValueError(f"case is missing broken repository fixture: {source}")
    _reject_symlinks(source)
    temp_root = Path(tempfile.mkdtemp(prefix="rescuebench-"))
    workspace = temp_root / "workspace"
    shutil.copytree(source, workspace)
    patch_file = temp_root / "attempt.patch"
    patch_file.write_text(patch, encoding="utf-8")
    if os.name != "nt":
        for path in [workspace, *workspace.rglob("*")]:
            try:
                path.chmod(path.stat().st_mode | 0o200)
            except OSError:
                pass
    return AttemptWorkspace(root=workspace, patch_file=patch_file)
