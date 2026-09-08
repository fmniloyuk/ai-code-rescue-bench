from __future__ import annotations

from pathlib import Path

import yaml

from .models import CaseManifest, CaseSummary


class BenchmarkCatalog:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.cases_dir = self.root / "benchmarks"

    def case_dirs(self) -> list[Path]:
        if not self.cases_dir.exists():
            return []
        return sorted(path.parent for path in self.cases_dir.glob("*/case.yaml"))

    def load(self, case_id: str) -> tuple[CaseManifest, Path]:
        case_dir = (self.cases_dir / case_id).resolve()
        if self.cases_dir.resolve() not in case_dir.parents:
            raise ValueError("invalid case id")
        manifest_path = case_dir / "case.yaml"
        if not manifest_path.exists():
            raise KeyError(f"unknown benchmark case: {case_id}")
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest = CaseManifest.model_validate(data)
        if manifest.id != case_id:
            raise ValueError(f"manifest id {manifest.id!r} does not match directory {case_id!r}")
        return manifest, case_dir

    def summaries(self) -> list[CaseSummary]:
        result: list[CaseSummary] = []
        for case_dir in self.case_dirs():
            manifest, _ = self.load(case_dir.name)
            result.append(
                CaseSummary(
                    id=manifest.id,
                    title=manifest.title,
                    stack=manifest.stack,
                    defect_category=manifest.defect_category,
                    difficulty=manifest.difficulty,
                    security_implications=manifest.security_implications,
                    path=case_dir,
                )
            )
        return result


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "benchmarks").exists():
            return candidate
    raise RuntimeError("could not locate ai-code-rescue-bench repository root")
