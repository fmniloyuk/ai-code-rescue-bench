from __future__ import annotations

import time
import uuid
from pathlib import Path

from .artifacts import ArtifactStore
from .models import CheckResult, EvaluationResult, PatchProposal
from .patches import apply_patch_in_sandbox, changed_lines, normalize_patch, validate_patch_paths
from .sandbox import DockerSandbox, Mount
from .scoring import score_attempt
from .workspace import create_workspace


class Evaluator:
    def __init__(self, repo_root: Path, sandbox: DockerSandbox | None = None) -> None:
        self.repo_root = repo_root
        self.sandbox = sandbox or DockerSandbox()
        self.store = ArtifactStore(repo_root / "artifacts" / "runs")

    def evaluate(
        self,
        manifest,
        case_dir: Path,
        patch: str,
        *,
        mode: str,
        proposal: PatchProposal | None = None,
    ) -> EvaluationResult:
        started = time.perf_counter()
        normalized = normalize_patch(patch)
        validate_patch_paths(normalized)
        workspace = create_workspace(case_dir, normalized)
        try:
            apply_patch_in_sandbox(self.sandbox, manifest.sandbox, workspace.root, workspace.patch_file)
            checks: list[CheckResult] = []
            grader_dir = case_dir / "tests_hidden"
            mounts = [Mount(workspace.root, "/workspace", read_only=False)]
            if grader_dir.exists():
                mounts.append(Mount(grader_dir, "/grader", read_only=True))
            for check in manifest.checks:
                outcome = self.sandbox.run(
                    manifest.sandbox,
                    check.command,
                    mounts,
                    image=check.image,
                    timeout_seconds=check.timeout_seconds,
                )
                checks.append(
                    CheckResult(
                        name=check.name,
                        stage=check.stage,
                        passed=outcome.exit_code == 0,
                        exit_code=outcome.exit_code,
                        duration_ms=outcome.duration_ms,
                        stdout=outcome.stdout,
                        stderr=outcome.stderr,
                        weight=check.weight,
                        timed_out=outcome.timed_out,
                    )
                )
            line_count = changed_lines(normalized)
            score = score_attempt(checks, line_count, manifest.changed_lines_budget)
            run_id = f"{manifest.id}-{uuid.uuid4().hex[:12]}"
            runtime_ms = int((time.perf_counter() - started) * 1000)
            result = EvaluationResult(
                run_id=run_id,
                case_id=manifest.id,
                mode=mode,
                provider=proposal.provider if proposal else None,
                model=proposal.model if proposal else None,
                prompt_id=proposal.prompt_id if proposal else None,
                usage=proposal.usage if proposal else None,
                patch=normalized,
                checks=checks,
                score=score,
                runtime_ms=runtime_ms,
                artifact_dir=str(self.repo_root / "artifacts" / "runs" / run_id),
            )
            self.store.save(result)
            return result
        finally:
            workspace.cleanup()
