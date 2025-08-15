import json
import hashlib
from ..ecs.world import World
from ..schemas import WorldSnapshot, WorldDiff, EntityPayload
from ..config import PROTOCOL_VERSION, NETWORK_CONFIG

def _entity_hash(components_dict):
    h = hashlib.sha256()
    h.update(json.dumps(components_dict, sort_keys=True).encode())
    return h.hexdigest()

class StateSerializer:
    def __init__(self, world: World):
        self.world = world
        self.last_hashes = {}
        self.last_full_sent_tick = -1

    def full_snapshot(self) -> WorldSnapshot:
        payload = []
        for eid in self.world.entities.entities:
            comp_map = self.world.entities.serialize_entity(eid)
            h = _entity_hash(comp_map)
            self.last_hashes[eid] = h
            payload.append(EntityPayload(id=eid, components=comp_map))
        return WorldSnapshot(
            tick=self.world.state.tick,
            protocol=PROTOCOL_VERSION,
            seed=self.world.state.seed,
            entities=payload,
            meta=self._meta()
        )

    def diff(self) -> WorldDiff:
        added = []
        updated = []
        current_ids = set(self.world.entities.entities)
        previous_ids = set(self.last_hashes.keys())
        removed = list(previous_ids - current_ids)
        for eid in current_ids:
            comp_map = self.world.entities.serialize_entity(eid)
            h = _entity_hash(comp_map)
            if eid not in self.last_hashes:
                self.last_hashes[eid] = h
                added.append(EntityPayload(id=eid, components=comp_map))
            else:
                if self.last_hashes[eid] != h:
                    self.last_hashes[eid] = h
                    updated.append(EntityPayload(id=eid, components=comp_map))
        for r in removed:
            del self.last_hashes[r]
        return WorldDiff(
            tick=self.world.state.tick,
            protocol=PROTOCOL_VERSION,
            seed=self.world.state.seed,
            added=added,
            updated=updated,
            removed=removed,
            meta=self._meta()
        )

    def _meta(self):
        return {
            "decision_feed": self.world.state.decision_feed,
            "event_feed": self.world.state.event_feed,
            "expedition_feed": self.world.state.expedition_feed,
            "intervention_mode": self.world.state.intervention_mode,
            "portal_count": self.world.state.portal_count
        }