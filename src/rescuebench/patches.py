from __future__ import annotations

import re
from pathlib import Path

from .models import SandboxSpec
from .sandbox import DockerSandbox, Mount

_PATH_RE = re.compile(r"^(?:---|\+\+\+)\s+(?:[ab]/)?([^\t\n]+)", re.MULTILINE)


def normalize_patch(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    return stripped.rstrip() + "\n"


def validate_patch_paths(patch: str) -> None:
    if not patch.strip():
        raise ValueError("patch is empty")
    for raw in _PATH_RE.findall(patch):
        if raw == "/dev/null":
            continue
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"patch contains unsafe path: {raw}")
        if path.parts and path.parts[0] in {".git", ".github"}:
            raise ValueError(f"patch may not modify benchmark control path: {raw}")
        if "tests" in path.parts or any(part.startswith("test_") for part in path.parts):
            raise ValueError(f"patch may not modify benchmark tests: {raw}")


def changed_lines(patch: str) -> int:
    total = 0
    for line in patch.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith(("+", "-")):
            total += 1
    return total


def apply_patch_in_sandbox(
    sandbox: DockerSandbox,
    spec: SandboxSpec,
    workspace: Path,
    patch_file: Path,
) -> None:
    patcher_spec = spec.model_copy(update={"image": "alpine/git:2.47.2", "timeout_seconds": 30})
    mounts = [
        Mount(workspace, "/workspace", read_only=False),
        Mount(patch_file, "/attempt.patch", read_only=True),
    ]
    check = sandbox.run(patcher_spec, ["git", "apply", "--check", "/attempt.patch"], mounts)
    if check.exit_code != 0:
        raise ValueError(f"patch does not apply cleanly: {check.stderr or check.stdout}")
    applied = sandbox.run(patcher_spec, ["git", "apply", "/attempt.patch"], mounts)
    if applied.exit_code != 0:
        raise RuntimeError(f"failed to apply patch: {applied.stderr or applied.stdout}")
