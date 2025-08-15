// Patch: added guards to prevent undefined path node / position errors.
import { EntityManager } from '../core/ecs/EntityManager';

interface MoveTaskState {
  path: { x: number; y: number }[];
  index: number;
  done?: boolean;
}

export class LocalAI {
  constructor(private em: EntityManager) {}

  updateAgent(id: number, dt: number) {
    const task = this.getOrInitTask(id);
    if (task.done) return;
    this.executeTask(id, task, dt);
  }

  private getOrInitTask(id: number): MoveTaskState {
    let state = (this as any)._state?.[id] as MoveTaskState | undefined;
    if (!this._state) (this as any)._state = {};
    if (!state) {
      state = {
        path: this.buildRandomPath(id),
        index: 0
      };
      (this as any)._state[id] = state;
    }
    return state;
  }

  private buildRandomPath(id: number): { x: number; y: number }[] {
    const pos = this.em.position.get(id);
    if (!pos) return [];
    const path: { x: number; y: number }[] = [];
    const steps = 6;
    for (let i = 0; i < steps; i++) {
      path.push({
        x: pos.x + Math.floor((Math.random() - 0.5) * 10),
        y: pos.y + Math.floor((Math.random() - 0.5) * 10)
      });
    }
    return path;
  }

  private executeTask(id: number, task: MoveTaskState, dt: number) {
    const pos = this.em.position.get(id);
    if (!pos) {
      task.done = true;
      return;
    }
    if (!task.path || task.index >= task.path.length) {
      task.done = true;
      return;
    }
    const node = task.path[task.index];
    if (!node) {
      task.done = true;
      return;
    }
    this.moveToward(pos, node, dt);
    const dist = Math.hypot(pos.x - node.x, pos.y - node.y);
    if (dist < 0.3) {
      task.index++;
      if (task.index >= task.path.length) task.done = true;
    }
  }

  private moveToward(pos: { x: number; y: number }, target: { x: number; y: number }, dt: number) {
    const speed = 2 * dt;
    const dx = target.x - pos.x;
    const dy = target.y - pos.y;
    const len = Math.hypot(dx, dy) || 1;
    pos.x += (dx / len) * speed;
    pos.y += (dy / len) * speed;
  }
}