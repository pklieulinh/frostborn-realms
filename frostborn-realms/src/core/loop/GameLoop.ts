export type LoopCallback = (dt: number) => void;

interface LoopStats {
  fps: number;
  rawFps: number;
  frameTime: number;
  frames: number;
  lastFpsSample: number;
}

export class GameLoop {
  private callbacks: Set<LoopCallback> = new Set();
  private running = false;
  private rafId: number | null = null;
  private lastTime = 0;
  private speed = 1;
  private paused = false;
  private pauseAccum = 0;
  private stats: LoopStats = {
    fps: 0,
    rawFps: 0,
    frameTime: 0,
    frames: 0,
    lastFpsSample: 0
  };
  private maxDelta = 0.25; // seconds clamp

  add(cb: LoopCallback) {
    this.callbacks.add(cb);
    return () => this.remove(cb);
  }

  onTick(cb: LoopCallback) {
    return this.add(cb);
  }

  remove(cb: LoopCallback) {
    this.callbacks.delete(cb);
  }

  clear() {
    this.callbacks.clear();
  }

  setSpeed(multiplier: number) {
    this.speed = Math.max(0, multiplier || 0);
  }

  getSpeed() {
    return this.speed;
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.lastTime = performance.now();
    this.stats.lastFpsSample = this.lastTime;
    const step = (t: number) => {
      if (!this.running) return;
      if (this.paused) {
        this.lastTime = t;
        this.rafId = requestAnimationFrame(step);
        return;
      }
      const rawDtMs = t - this.lastTime;
      this.lastTime = t;
      let dt = (rawDtMs / 1000) * this.speed;
      if (dt > this.maxDelta) dt = this.maxDelta;
      this.tick(dt);
      this.rafId = requestAnimationFrame(step);
    };
    this.rafId = requestAnimationFrame(step);
  }

  stop() {
    if (!this.running) return;
    this.running = false;
    if (this.rafId != null) cancelAnimationFrame(this.rafId);
    this.rafId = null;
  }

  pause() {
    this.paused = true;
  }

  resume() {
    this.paused = false;
  }

  isPaused() {
    return this.paused;
  }

  isRunning() {
    return this.running;
  }

  private tick(dt: number) {
    const before = performance.now();
    for (const cb of this.callbacks) {
      try {
        cb(dt);
      } catch (e) {
        // Log once per frame per callback; simple console for now.
        console.error('[GameLoop] callback error', e);
      }
    }
    const after = performance.now();
    const frameMs = after - before;
    this.updateStats(frameMs);
  }

  private updateStats(frameTime: number) {
    const now = performance.now();
    this.stats.frames++;
    this.stats.rawFps = 1000 / Math.max(0.0001, frameTime);
    // Simple moving average over 0.5s
    if (now - this.stats.lastFpsSample >= 500) {
      const elapsed = (now - this.stats.lastFpsSample) / 1000;
      const fps = this.stats.frames / elapsed;
      // Smooth
      this.stats.fps = this.stats.fps === 0 ? fps : this.stats.fps * 0.6 + fps * 0.4;
      this.stats.frameTime = frameTime;
      this.stats.frames = 0;
      this.stats.lastFpsSample = now;
    }
  }

  getFPS() {
    return this.stats.fps;
  }

  getRawFPS() {
    return this.stats.rawFps;
  }

  getAverageFrameTime() {
    return this.stats.frameTime;
  }
}