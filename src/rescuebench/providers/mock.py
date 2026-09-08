from __future__ import annotations

from ..models import PatchProposal, ProviderUsage
from .base import PatchProvider, ProviderContext


class MockProvider(PatchProvider):
    name = "mock"

    def propose(self, context: ProviderContext, model: str | None = None) -> PatchProposal:
        patch = (context.case_dir / "mock.patch").read_text(encoding="utf-8")
        return PatchProposal(
            provider=self.name,
            model=model or "deterministic-mock-v1",
            patch=patch,
            prompt_id=context.prompt_id,
            usage=ProviderUsage(input_tokens=0, output_tokens=0, estimated_cost_usd=0.0),
            latency_ms=0,
        )
