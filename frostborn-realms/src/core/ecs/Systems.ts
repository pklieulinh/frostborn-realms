export interface System {
  id: string;
  update(dt: number, elapsed: number): void;
  lateUpdate?(): void;
  dispose?(): void;
}