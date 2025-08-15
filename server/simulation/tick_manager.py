import asyncio
import time
from typing import Callable, Awaitable, List
from ..config import TICK_INTERVAL_SEC

class TickManager:
    def __init__(self):
        self._tasks: List[Callable[[int, float], Awaitable[None] | None]] = []
        self._running = False
        self._tick = 0

    def add_task(self, fn: Callable[[int, float], Awaitable[None] | None]):
        self._tasks.append(fn)

    async def start(self):
        self._running = True
        last = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            dt = now - last
            last = now
            tick_index = self._tick
            for task in self._tasks:
                result = task(tick_index, dt)
                if asyncio.iscoroutine(result):
                    await result
            self._tick += 1
            elapsed = time.perf_counter() - now
            sleep_for = TICK_INTERVAL_SEC - elapsed
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)

    def stop(self):
        self._running = False