import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
from ..schemas import ServerHello, CommandEnvelope, Ack
from ..config import PROTOCOL_VERSION, GAME_TITLE, WORLD_SEED, NETWORK_CONFIG
from ..simulation.state_serializer import StateSerializer
from ..ecs.world import World
from ..ai.leader import confirm_pending, reject_pending
from ..expedition.sim import launch_expedition

router = APIRouter()

class ConnectionHub:
    def __init__(self):
        self._clients: Set[WebSocket] = set()

    async def register(self, ws: WebSocket):
        await ws.accept()
        self._clients.add(ws)

    def unregister(self, ws: WebSocket):
        self._clients.discard(ws)

    async def broadcast_json(self, data):
        dead = []
        for ws in self._clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.unregister(ws)

hub = ConnectionHub()

def build_net_app(world: World):
    serializer = StateSerializer(world)

    @router.websocket("/ws")
    async def ws_endpoint(ws: WebSocket):
        await hub.register(ws)
        hello = ServerHello(protocol=PROTOCOL_VERSION, title=GAME_TITLE, seed=WORLD_SEED)
        await ws.send_json(hello.dict())
        try:
            while True:
                msg = await ws.receive_text()
                if msg.startswith("{"):
                    import json
                    try:
                        data = json.loads(msg)
                        cmd = CommandEnvelope(**data)
                        await handle_command(world, ws, cmd)
                    except Exception as e:
                        await ws.send_json(Ack(status="error", detail=str(e)).dict())
        except WebSocketDisconnect:
            hub.unregister(ws)

    async def tick_broadcast(tick: int, dt: float):
        if tick == 0 or tick % NETWORK_CONFIG.full_state_every_n_ticks == 0:
            snap = serializer.full_snapshot()
            await hub.broadcast_json({"type": "full", "payload": snap.dict()})
        else:
            diff = serializer.diff()
            if diff.added or diff.updated or diff.removed:
                await hub.broadcast_json({"type": "diff", "payload": diff.dict()})
            elif NETWORK_CONFIG.send_empty_ticks:
                await hub.broadcast_json({"type": "noop", "tick": diff.tick})

    return router, tick_broadcast

async def handle_command(world: World, ws: WebSocket, envelope: CommandEnvelope):
    if envelope.cmd == "toggle_intervention":
        world.state.intervention_mode = not world.state.intervention_mode
        await ws.send_json(Ack(status="ok", detail=f"intervention={world.state.intervention_mode}").dict())
    elif envelope.cmd == "confirm_decision":
        idx = envelope.data.get("index", 0)
        if confirm_pending(world, idx):
            await ws.send_json(Ack(status="ok", detail="confirmed").dict())
        else:
            await ws.send_json(Ack(status="error", detail="invalid index").dict())
    elif envelope.cmd == "reject_decision":
        idx = envelope.data.get("index", 0)
        if reject_pending(world, idx):
            await ws.send_json(Ack(status="ok", detail="rejected").dict())
        else:
            await ws.send_json(Ack(status="error", detail="invalid index").dict())
    elif envelope.cmd == "launch_expedition":
        portal_seed = envelope.data.get("seed")
        if portal_seed:
            launch_expedition(world, portal_seed)
            await ws.send_json(Ack(status="ok", detail="expedition launched").dict())
        else:
            await ws.send_json(Ack(status="error", detail="missing seed").dict())
    else:
        await ws.send_json(Ack(status="error", detail="unknown cmd").dict())