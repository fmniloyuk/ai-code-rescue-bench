from __future__ import annotations

import os
import time

import httpx

from ..models import PatchProposal, ProviderUsage
from .base import PatchProvider, ProviderContext, build_prompt
from .openai_compat import _estimate_cost


class AnthropicProvider(PatchProvider):
    name = "anthropic"

    def propose(self, context: ProviderContext, model: str | None = None) -> PatchProposal:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required")
        selected_model = model or os.environ.get("ANTHROPIC_MODEL")
        if not selected_model:
            raise RuntimeError("model is required via --model or ANTHROPIC_MODEL")
        started = time.perf_counter()
        with httpx.Client(timeout=120) as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": selected_model,
                    "max_tokens": 4096,
                    "temperature": 0,
                    "messages": [{"role": "user", "content": build_prompt(context)}],
                },
            )
            response.raise_for_status()
            data = response.json()
        text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        usage = data.get("usage") or {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        return PatchProposal(
            provider=self.name,
            model=selected_model,
            patch=text,
            prompt_id=context.prompt_id,
            usage=ProviderUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=_estimate_cost(input_tokens, output_tokens),
            ),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
