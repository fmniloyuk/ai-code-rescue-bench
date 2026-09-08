from __future__ import annotations

import os
import time

import httpx

from ..models import PatchProposal, ProviderUsage
from .base import PatchProvider, ProviderContext, build_prompt


class OpenAICompatibleProvider(PatchProvider):
    name = "openai-compatible"

    def propose(self, context: ProviderContext, model: str | None = None) -> PatchProposal:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required")
        selected_model = model or os.environ.get("OPENAI_MODEL")
        if not selected_model:
            raise RuntimeError("model is required via --model or OPENAI_MODEL")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        started = time.perf_counter()
        with httpx.Client(timeout=120) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": selected_model,
                    "temperature": 0,
                    "messages": [{"role": "user", "content": build_prompt(context)}],
                },
            )
            response.raise_for_status()
            data = response.json()
        usage = data.get("usage") or {}
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        estimated = _estimate_cost(input_tokens, output_tokens)
        return PatchProposal(
            provider=self.name,
            model=selected_model,
            patch=data["choices"][0]["message"]["content"],
            prompt_id=context.prompt_id,
            usage=ProviderUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=estimated,
            ),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )


def _estimate_cost(input_tokens: int | None, output_tokens: int | None) -> float | None:
    in_rate = os.environ.get("RESCUEBENCH_INPUT_USD_PER_MILLION")
    out_rate = os.environ.get("RESCUEBENCH_OUTPUT_USD_PER_MILLION")
    if in_rate is None or out_rate is None or input_tokens is None or output_tokens is None:
        return None
    return round((input_tokens * float(in_rate) + output_tokens * float(out_rate)) / 1_000_000, 8)
