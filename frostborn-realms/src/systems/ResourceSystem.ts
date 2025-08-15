import { System } from '../core/ecs/Systems';
import { World } from '../world/World';

export class ResourceSystem implements System {
  id = 'resource';
  timer = 0;
  update(dt: number, elapsed: number): void {
    this.timer += dt;
    if (this.timer > 15) {
      this.timer = 0;
      // Regenerate little resource
      // Could add advanced logic later
    }
  }
  constructor(private world: World) {}
}