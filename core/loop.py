import time
from typing import Callable, List

class GameLoop:
    def __init__(self, max_delta: float = 0.25):
        self._callbacks: List[Callable[[float], None]] = []
        self._running = False
        self._speed = 1.0
        self._max_delta = max_delta
    def add(self, fn: Callable[[float], None]):
        self._callbacks.append(fn)
    def set_speed(self, s: float):
        self._speed = max(0.0, s)
    def run(self):
        self._running = True
        prev = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            dt = (now - prev) * self._speed
            prev = now
            if dt > self._max_delta:
                dt = self._max_delta
            for cb in self._callbacks:
                cb(dt)
    def stop(self):
        self._running = False