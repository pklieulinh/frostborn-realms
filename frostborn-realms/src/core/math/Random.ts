export class RNG {
  constructor(public seed = Math.floor(Math.random() * 1e9)) {}
  next() {
    // LCG
    this.seed = (this.seed * 1664525 + 1013904223) % 0xffffffff;
    return this.seed / 0xffffffff;
  }
  range(min: number, max: number) { return min + (max - min) * this.next(); }
  int(min: number, max: number) { return Math.floor(this.range(min, max + 1)); }
  pick<T>(arr: T[]) { return arr[Math.floor(this.next() * arr.length)]; }
  chance(p: number) { return this.next() < p; }
}