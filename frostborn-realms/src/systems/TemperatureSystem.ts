import { System } from '../core/ecs/Systems';
import { World } from '../world/World';
import { EntityManager } from '../core/ecs/EntityManager';

export class TemperatureSystem implements System {
  id = 'temp';
  accum = 0;
  constructor(private world: World, private em: EntityManager) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum > 2) {
      this.accum = 0;
      // Compute average
      let totalTemp = 0;
      let count = 0;
      for (const tile of this.world.tiles) {
        const base = this.world.ambientTemp;
        let local = base + tile.tempOffset;
        if (tile.building) {
          // heat building influences in Rendering system maybe
        }
        totalTemp += local;
        count++;
      }
      const avg = count ? totalTemp / count : this.world.ambientTemp;
      this.world.updateDerivedMetrics(avg, this.world.threatIndex);
    }
  }
  serialize() {
    return { ambient: this.world.ambientTemp };
  }
  deserialize(json: any) {
    this.world.ambientTemp = json.ambient;
  }
}