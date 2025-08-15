from typing import Dict, Any, List
from .components import COMPONENT_TYPES, serialize_component

class EntityManager:
    def __init__(self):
        self._alive: List[int] = []
        self._components: Dict[str, Dict[int, Any]] = {name: {} for name in COMPONENT_TYPES.keys()}

    def create(self, eid: int):
        if eid in self._alive:
            raise ValueError(f"Entity {eid} exists")
        self._alive.append(eid)
        return eid

    def destroy(self, eid: int):
        if eid in self._alive:
            self._alive.remove(eid)
        for store in self._components.values():
            store.pop(eid, None)

    def add_component(self, eid: int, comp_name: str, comp_obj: Any):
        if comp_name not in self._components:
            raise KeyError(f"Unknown component {comp_name}")
        self._components[comp_name][eid] = comp_obj

    def get_component_store(self, comp_name: str) -> Dict[int, Any]:
        return self._components[comp_name]

    def serialize_entity(self, eid: int):
        comp_map = {}
        for cname, store in self._components.items():
            if eid in store:
                comp_map[cname] = serialize_component(store[eid])
        return comp_map

    @property
    def entities(self):
        return list(self._alive)