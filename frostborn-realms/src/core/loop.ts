export class GameLoop {
  private last = 0;
  private running = false;
  private accumulator = 0;
  private readonly fixed = 1000 / 30;
  constructor(private step: (dt: number, elapsed: number) => void, private rafPost?: () => void) {}
  start() {
    if (this.running) return;
    this.running = true;
    this.last = performance.now();
    const frame = (now: number) => {
      if (!this.running) return;
      const delta = now - this.last;
      this.last = now;
      this.accumulator += delta;
      const MAX_ACC = 1000;
      if (this.accumulator > MAX_ACC) this.accumulator = MAX_ACC;
      while (this.accumulator >= this.fixed) {
        this.step(this.fixed / 1000, now / 1000);
        this.accumulator -= this.fixed;
      }
      if (this.rafPost) this.rafPost();
      requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }
  stop() { this.running = false; }
}