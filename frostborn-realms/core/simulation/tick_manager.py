import time

class TickManager:
    def __init__(self, interval_sec: float):
        self.interval = interval_sec
        self.accumulator = 0.0
        self.last_time = time.perf_counter()
        self.tick_index = 0
        self.tasks = []
        self.profile = {}
        self.speed_mult = 1.0
        self._ema = {}
        self._ema_alpha = 0.2
        self._tps_window_start = time.perf_counter()
        self._ticks_in_window = 0
        self.tps_real = 0.0
    def add_task(self, fn):
        self.tasks.append(fn)
    def set_speed_mult(self, mult: float):
        if mult < 0.1: mult = 0.1
        if mult > 50: mult = 50
        self.speed_mult = mult
    def step(self):
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now
        self.accumulator += dt * self.speed_mult
        while self.accumulator >= self.interval:
            self.accumulator -= self.interval
            self._run_tick(self.interval)
        # TPS calc
        if now - self._tps_window_start >= 1.0:
            self.tps_real = self._ticks_in_window / (now - self._tps_window_start)
            self._ticks_in_window = 0
            self._tps_window_start = now
    def _run_tick(self, dt: float):
        idx = self.tick_index
        for fn in self.tasks:
            name = getattr(fn, "__name__", "task")
            t0 = time.perf_counter()
            fn(idx, dt)
            t1 = time.perf_counter()
            elapsed = (t1 - t0)*1000.0
            ema_prev = self._ema.get(name, elapsed)
            self._ema[name] = ema_prev + self._ema_alpha*(elapsed - ema_prev)
        self.tick_index += 1
        self._ticks_in_window += 1
    def get_profile_snapshot(self):
        return {"ema_ms": dict(self._ema)}