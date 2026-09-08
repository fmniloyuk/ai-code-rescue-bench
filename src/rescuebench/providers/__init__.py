from .anthropic import AnthropicProvider
from .base import PatchProvider, ProviderContext
from .mock import MockProvider
from .openai_compat import OpenAICompatibleProvider


def get_provider(name: str) -> PatchProvider:
    providers: dict[str, PatchProvider] = {
        "mock": MockProvider(),
        "openai": OpenAICompatibleProvider(),
        "openai-compatible": OpenAICompatibleProvider(),
        "anthropic": AnthropicProvider(),
    }
    try:
        return providers[name]
    except KeyError as exc:
        raise ValueError(f"unknown provider {name!r}; choose from {', '.join(sorted(providers))}") from exc


__all__ = [
    "AnthropicProvider",
    "MockProvider",
    "OpenAICompatibleProvider",
    "PatchProvider",
    "ProviderContext",
    "get_provider",
]
