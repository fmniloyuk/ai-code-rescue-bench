from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .models import SandboxSpec


@dataclass(frozen=True)
class Mount:
    source: Path
    target: str
    read_only: bool = True


@dataclass(frozen=True)
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool


class DockerSandbox:
    """Runs untrusted benchmark commands only behind a constrained Docker boundary."""

    def _docker_command(
        self,
        spec: SandboxSpec,
        command: list[str],
        mounts: list[Mount],
        *,
        image: str | None = None,
    ) -> list[str]:
        uid = os.getuid() if hasattr(os, "getuid") else 65534
        gid = os.getgid() if hasattr(os, "getgid") else 65534
        argv = [
            "docker",
            "run",
            "--rm",
            "--init",
            "--network",
            "none",
            "--cpus",
            str(spec.cpus),
            "--memory",
            spec.memory,
            "--pids-limit",
            str(spec.pids),
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--user",
            f"{uid}:{gid}",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,nodev,size=64m",
            "--tmpfs",
            "/run:rw,noexec,nosuid,nodev,size=16m",
            "--workdir",
            "/workspace",
            "--env",
            "HOME=/tmp",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
            "--env",
            "NO_COLOR=1",
        ]
        for mount in mounts:
            mount_arg = f"type=bind,src={mount.source.resolve()},dst={mount.target}"
            if mount.read_only:
                mount_arg += ",readonly"
            argv.extend(["--mount", mount_arg])
        argv.append(image or spec.image)
        argv.extend(command)
        return argv

    def run(
        self,
        spec: SandboxSpec,
        command: list[str],
        mounts: list[Mount],
        *,
        image: str | None = None,
        timeout_seconds: int | None = None,
    ) -> SandboxResult:
        argv = self._docker_command(spec, command, mounts, image=image)
        started = time.perf_counter()
        timeout = timeout_seconds or spec.timeout_seconds
        try:
            completed = subprocess.run(
                argv,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            duration_ms = int((time.perf_counter() - started) * 1000)
            return SandboxResult(
                exit_code=completed.returncode,
                stdout=completed.stdout[-50_000:],
                stderr=completed.stderr[-50_000:],
                duration_ms=duration_ms,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            return SandboxResult(
                exit_code=124,
                stdout=(exc.stdout or "")[-50_000:] if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr or "")[-50_000:] if isinstance(exc.stderr, str) else "",
                duration_ms=duration_ms,
                timed_out=True,
            )
