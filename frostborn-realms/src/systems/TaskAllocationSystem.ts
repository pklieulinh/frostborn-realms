import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class TaskAllocationSystem implements System {
  id = 'taskAlloc';
  constructor(private em: EntityManager, private world: World) {}
  update(): void {
    // Auto generate gather tasks if resources exist but few tasks
    const pending = this.em.fetchPendingTasks(t => t.type === 'gather_resource');
    if (pending.length < 6) {
      for (let i = 0; i < 3; i++) {
        const tile = this.world.tiles[Math.floor(Math.random() * this.world.tiles.length)];
        if (!tile.discovered || !tile.resource || tile.resource.qty <= 0) continue;
        if (!this.em.tasks.find(t => t.type === 'gather_resource' && t.data.x === tile.x && t.data.y === tile.y && t.status === 'pending')) {
          this.em.createTask('gather_resource', { x: tile.x, y: tile.y }, 0.3);
        }
      }
    }
    // Random scout tasks
    const scoutPending = this.em.fetchPendingTasks(t => t.type === 'scout_area');
    if (scoutPending.length < 2) {
      const rx = Math.floor(this.world.spawnX + (Math.random() * 60 - 30));
      const ry = Math.floor(this.world.spawnY + (Math.random() * 60 - 30));
      if (this.world.getTile(rx, ry)) {
        this.em.createTask('scout_area', { x: rx, y: ry }, 0.1);
      }
    }
    // Construction tasks auto from construction components
    for (const [id, c] of this.em.construction.entries()) {
      const existing = this.em.tasks.find(t => t.type === 'construct' && t.data.entity === id && t.status !== 'done');
      if (!existing) {
        const def = c.building; // will be replaced with actual def retrieval later
        this.em.createTask('construct', { entity: id, def: { id: c.building, buildTime: 20, provides: {} } }, 0.6);
      }
    }
  }
}