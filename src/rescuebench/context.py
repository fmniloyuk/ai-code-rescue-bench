from __future__ import annotations

from pathlib import Path

from .models import CaseManifest
from .providers.base import ProviderContext

_TEXT_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".sql", ".json", ".yaml", ".yml", ".toml", ".md", ".txt"}


def build_provider_context(manifest: CaseManifest, case_dir: Path, prompt_id: str = "default") -> ProviderContext:
    issue_path = case_dir / "issue.md"
    issue = issue_path.read_text(encoding="utf-8")
    repo = case_dir / "repo"
    chunks: list[str] = []
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or path.suffix not in _TEXT_SUFFIXES:
            continue
        relative = path.relative_to(repo)
        if any(part in {"node_modules", ".git", "dist", "coverage"} for part in relative.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > 40_000:
            text = text[:40_000] + "\n...<truncated>"
        chunks.append(f"\n--- FILE: {relative} ---\n{text}")
    return ProviderContext(
        manifest=manifest,
        case_dir=case_dir,
        issue=issue,
        repository_snapshot="".join(chunks),
        prompt_id=prompt_id,
    )
