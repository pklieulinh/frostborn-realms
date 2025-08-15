import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

interface TaskLogSample {
  dist: number;
}

export class LogisticsMetricsSystem implements System {
  id = 'logisticsMetrics';
  private samples: TaskLogSample[] = [];
  private accumulator = 0;
  pathEfficiency = 1;
  constructor(private em: EntityManager, private world: World) {}

  update(dt: number): void {
    this.accumulator += dt;
    if (this.accumulator > 5) {
      this.accumulator = 0;
      this.recalculate();
    }
  }

  logTask(type: string, data: any) {
    if (!data) return;
    if (typeof data.x === 'number' && typeof data.y === 'number') {
      const dist = Math.abs(data.x - this.world.spawnX) + Math.abs(data.y - this.world.spawnY);
      this.samples.push({ dist });
      if (this.samples.length > 300) this.samples.shift();
    }
  }

  private recalculate() {
    if (!this.samples.length) {
      this.pathEfficiency = 1;
      return;
    }
    const avg = this.samples.reduce((a, b) => a + b.dist, 0) / this.samples.length;
    const baseline = 18; // heuristic baseline distance
    this.pathEfficiency = Math.min(1.5, Math.max(0.4, baseline / (avg || baseline)));
  }
}