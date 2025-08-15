from typing import Dict, TypeVar, Generic, Optional, Iterator, Any

T = TypeVar('T')

class ComponentStore(Generic[T]):
    def __init__(self):
        self._data: Dict[int, T] = {}
    def add(self, ent: int, comp: T):
        self._data[ent] = comp
    def get(self, ent: int) -> Optional[T]:
        return self._data.get(ent)
    def remove(self, ent: int):
        self._data.pop(ent, None)
    def items(self):
        return self._data.items()
    def __contains__(self, ent: int):
        return ent in self._data
    def __iter__(self) -> Iterator[int]:
        return iter(self._data.keys())

class EntityManager:
    def __init__(self):
        self._next_id = 1
        self.alive: Dict[int, bool] = {}
    def create(self) -> int:
        eid = self._next_id
        self._next_id += 1
        self.alive[eid] = True
        return eid
    def destroy(self, ent: int):
        self.alive.pop(ent, None)
    def is_alive(self, ent: int) -> bool:
        return ent in self.alive

class WorldContext:
    def __init__(self, em: EntityManager):
        self.em = em
        self.components: Dict[str, Any] = {}
    def register_store(self, name: str, store: Any):
        self.components[name] = store
    def store(self, name: str):
        return self.components[name]