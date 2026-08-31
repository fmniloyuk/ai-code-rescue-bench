from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class AsyncCache:
    def __init__(self) -> None:
        self._values: dict[str, object] = {}

    async def get_or_load(self, key: str, loader: Callable[[str], Awaitable[T]]) -> T:
        if key in self._values:
            return self._values[key]  # type: ignore[return-value]
        value = await loader(key)
        self._values[key] = value
        return value
