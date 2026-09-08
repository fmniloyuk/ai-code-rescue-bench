import asyncio

from cache import AsyncCache


async def main() -> None:
    cache = AsyncCache()
    calls = 0

    async def loader(key: str) -> str:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)
        return f"value:{key}"

    values = await asyncio.gather(*(cache.get_or_load("same", loader) for _ in range(12)))
    assert values == ["value:same"] * 12
    assert calls == 1


asyncio.run(main())
