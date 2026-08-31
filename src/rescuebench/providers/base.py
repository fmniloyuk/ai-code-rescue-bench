from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..models import CaseManifest, PatchProposal


@dataclass(frozen=True)
class ProviderContext:
    manifest: CaseManifest
    case_dir: Path
    issue: str
    repository_snapshot: str
    prompt_id: str = "default"


class PatchProvider(ABC):
    name: str

    @abstractmethod
    def propose(self, context: ProviderContext, model: str | None = None) -> PatchProposal:
        raise NotImplementedError


def build_prompt(context: ProviderContext) -> str:
    contract = "\n".join(f"- {item}" for item in context.manifest.expected_behavior)
    return f"""You are repairing benchmark case {context.manifest.id}.
Return ONLY a unified git diff. Do not include Markdown fences or commentary.
Make the smallest correct patch. Do not modify tests or benchmark control files.

ISSUE
{context.issue}

EXPECTED BEHAVIOR
{contract}

VISIBLE REPOSITORY
{context.repository_snapshot}
"""
