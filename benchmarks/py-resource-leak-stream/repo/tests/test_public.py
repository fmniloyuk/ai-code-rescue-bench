import asyncio
from pathlib import Path

import reader


class FakeFile:
    def __init__(self) -> None:
        self.closed = False
        self.parts = iter([b"data", b""])

    def read(self, size: int) -> bytes:
        return next(self.parts)

    def close(self) -> None:
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


async def main() -> None:
    fake = FakeFile()
    reader.open = lambda *_args, **_kwargs: fake  # type: ignore[attr-defined]

    async def sender(_chunk: bytes) -> None:
        raise RuntimeError("client disconnected")

    try:
        await reader.stream_chunks(Path("unused"), sender)
    except RuntimeError:
        pass
    assert fake.closed


asyncio.run(main())
