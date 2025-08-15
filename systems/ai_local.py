import math

class AILocalSystem:
    def __init__(self):
        self.t = 0.0
    def update(self, ctx, dt: float):
        self.t += dt
        # Example: horizontal oscillation for all positions (mild)
        pos_store = ctx.store("position")
        for eid, pos in pos_store.items():
            pos.x += math.sin(self.t + eid * 0.2) * 0.3