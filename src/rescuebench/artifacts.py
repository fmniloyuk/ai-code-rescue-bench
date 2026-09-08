from __future__ import annotations

import json
from pathlib import Path

from .models import EvaluationResult


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, result: EvaluationResult) -> Path:
        run_dir = self.root / result.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "result.json").write_text(
            json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (run_dir / "attempt.patch").write_text(result.patch, encoding="utf-8")
        return run_dir

    def list(self) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        for path in sorted(self.root.glob("*/result.json"), reverse=True):
            try:
                results.append(EvaluationResult.model_validate_json(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return results

    def get(self, run_id: str) -> EvaluationResult:
        if "/" in run_id or ".." in run_id:
            raise KeyError(run_id)
        path = self.root / run_id / "result.json"
        if not path.exists():
            raise KeyError(run_id)
        return EvaluationResult.model_validate_json(path.read_text(encoding="utf-8"))
