from pydantic import BaseModel, Field
from typing import Dict, Any, List, Literal, Optional

class EntityPayload(BaseModel):
    id: int
    components: Dict[str, Any]

class WorldDiff(BaseModel):
    tick: int
    protocol: str
    seed: int
    added: List[EntityPayload] = Field(default_factory=list)
    updated: List[EntityPayload] = Field(default_factory=list)
    removed: List[int] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

class WorldSnapshot(BaseModel):
    tick: int
    protocol: str
    seed: int
    entities: List[EntityPayload]
    removed: List[int] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

class ServerHello(BaseModel):
    protocol: str
    title: str
    seed: int

class CommandEnvelope(BaseModel):
    cmd: str
    data: Dict[str, Any]

class Ack(BaseModel):
    status: Literal["ok", "error"]
    detail: str = ""

class DecisionFeedEntry(BaseModel):
    tick: int
    type: str
    options: List[Dict[str, Any]]
    chosen: str

class EventLogEntry(BaseModel):
    tick: int
    type: str
    detail: str

class ExpeditionLogEntry(BaseModel):
    tick: int
    id: int
    portal_seed: int
    status: str
    result: Optional[Dict[str, Any]] = None