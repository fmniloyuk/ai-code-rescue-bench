from pathlib import Path

from rescuebench.models import SandboxSpec
from rescuebench.sandbox import DockerSandbox, Mount


def test_docker_command_has_mandatory_isolation_controls(tmp_path: Path) -> None:
    spec = SandboxSpec(image="python:3.13-slim", cpus=0.5, memory="256m", pids=64)
    command = DockerSandbox()._docker_command(
        spec,
        ["python", "-V"],
        [Mount(tmp_path, "/workspace", read_only=False)],
    )
    joined = " ".join(command)
    assert "--network none" in joined
    assert "--cap-drop ALL" in joined
    assert "no-new-privileges:true" in joined
    assert "--pids-limit 64" in joined
    assert "--memory 256m" in joined
    assert "--read-only" in joined
