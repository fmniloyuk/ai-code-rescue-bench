from collections.abc import Awaitable, Callable
from pathlib import Path


async def stream_chunks(path: Path, sender: Callable[[bytes], Awaitable[None]]) -> None:
    file = open(path, "rb")
    while chunk := file.read(4):
        await sender(chunk)
    file.close()
