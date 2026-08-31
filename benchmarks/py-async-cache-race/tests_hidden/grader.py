import asyncio
import sys

sys.path.insert(0, "/workspace")
from cache import AsyncCache

mode = sys.argv[1]


async def hidden() -> None:
    cache = AsyncCache()
    calls = 0

    async def loader(key: str) -> str:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.005)
        return key.upper()

    values = await asyncio.gather(*(cache.get_or_load("x", loader) for _ in range(30)))
    assert values == ["X"] * 30
    assert calls == 1


async def security() -> None:
    cache = AsyncCache()
    a_started = asyncio.Event()
    release_a = asyncio.Event()
    b_started = asyncio.Event()

    async def loader(key: str) -> str:
        if key == "a":
            a_started.set()
            await release_a.wait()
        else:
            b_started.set()
        return key

    task_a = asyncio.create_task(cache.get_or_load("a", loader))
    await a_started.wait()
    task_b = asyncio.create_task(cache.get_or_load("b", loader))
    await asyncio.wait_for(b_started.wait(), timeout=0.2)
    release_a.set()
    assert await task_a == "a"
    assert await task_b == "b"


async def mutation() -> None:
    cache = AsyncCache()
    calls = 0

    async def loader(key: str) -> str:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)
        return "ok"

    for _ in range(4):
        assert (await asyncio.gather(*(cache.get_or_load("m", loader) for _ in range(15)))) == ["ok"] * 15
    assert calls == 1


async def regression() -> None:
    cache = AsyncCache()
    calls = 0

    async def loader(key: str) -> str:
        nonlocal calls
        calls += 1
        return key

    assert await cache.get_or_load("cached", loader) == "cached"
    assert await cache.get_or_load("cached", loader) == "cached"
    assert calls == 1


asyncio.run({"hidden": hidden, "security": security, "mutation": mutation, "regression": regression}[mode]())
