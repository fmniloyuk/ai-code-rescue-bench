import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "/workspace")
import reader

mode = sys.argv[1]


class FakeFile:
    def __init__(self, parts=None):
        self.closed = False
        self.parts = iter(parts or [b"abcd", b""])

    def read(self, size):
        return next(self.parts)

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


async def hidden():
    fake = FakeFile([b"abcd", b"efgh", b""])
    reader.open = lambda *_args, **_kwargs: fake
    started = asyncio.Event()

    async def sender(_chunk):
        started.set()
        await asyncio.sleep(10)

    task = asyncio.create_task(reader.stream_chunks(Path("unused"), sender))
    await started.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert fake.closed


async def security():
    fake = FakeFile()
    reader.open = lambda *_args, **_kwargs: fake

    async def sender(_chunk):
        return None

    await reader.stream_chunks(Path("unused"), sender)
    assert fake.closed


async def mutation():
    fake = FakeFile([b"a", b"b", b"c", b""])
    reader.open = lambda *_args, **_kwargs: fake
    calls = 0

    async def sender(_chunk):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError("boom")

    try:
        await reader.stream_chunks(Path("unused"), sender)
    except ValueError:
        pass
    assert fake.closed


async def regression():
    fake = FakeFile([b"abcd", b"ef", b""])
    reader.open = lambda *_args, **_kwargs: fake
    received = []

    async def sender(chunk):
        received.append(chunk)

    await reader.stream_chunks(Path("unused"), sender)
    assert received == [b"abcd", b"ef"]


asyncio.run({"hidden": hidden, "security": security, "mutation": mutation, "regression": regression}[mode]())
