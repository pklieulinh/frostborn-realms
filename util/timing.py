class RateLimiter:
    def __init__(self, max_fps: int):
        self.delay = 1.0 / max_fps
        self.accum = 0.0
    def should_step(self, dt: float) -> bool:
        self.accum += dt
        if self.accum >= self.delay:
            self.accum -= self.delay
            return True
        return False