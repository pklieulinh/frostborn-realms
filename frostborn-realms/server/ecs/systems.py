from typing import Protocol

class BaseSystem(Protocol):
    name: str
    def tick(self, dt: float, tick_index: int) -> None:
        ...

class SystemRegistry:
    def __init__(self):
        self._systems = []

    def add(self, system: BaseSystem):
        self._systems.append(system)

    def run(self, dt: float, tick_index: int):
        for sys in self._systems:
            sys.tick(dt, tick_index)