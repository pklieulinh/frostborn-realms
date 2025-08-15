import { GameLoop } from './core/loop/GameLoop';

const sharedLoop = new GameLoop();

export function startLoop(update: (dt: number) => void) {
  sharedLoop.add(update);
  if (!sharedLoop.isRunning()) sharedLoop.start();
  return sharedLoop;
}

// Backwards compatibility alias found in some logs (frame())
export function frame() {
  // no-op placeholder; real loop uses requestAnimationFrame
}

export { GameLoop };