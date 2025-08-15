import { System } from '../core/ecs/Systems';
import { World } from '../world/World';
import { DataRegistry } from '../data/registry';

export class PortalSpawnSystem implements System {
  id = 'portal';
  timer = 0;
  interval = 40;
  constructor(private world: World, private data: DataRegistry) {}
  update(dt: number): void {
    this.timer += dt * (1 + this.world.portalBoost * 0.5);
    if (this.timer >= this.interval) {
      this.timer = 0;
      this.spawnPortal();
    }
  }
  spawnPortal() {
    // random tile far away
    for (let i = 0; i < 50; i++) {
      const tile = this.world.tiles[Math.floor(Math.random() * this.world.tiles.length)];
      const dist = Math.hypot(tile.x - this.world.spawnX, tile.y - this.world.spawnY);
      if (dist < 15) continue;
      if (!tile.portal) {
        const biome = this.data.portalBiomes[Math.floor(Math.random() * this.data.portalBiomes.length)];
        tile.portal = { seed: Math.floor(Math.random() * 1e9), biome: biome.id, active: true };
        break;
      }
    }
  }
  serialize() {
    return {};
  }
  deserialize(_: any) {}
}