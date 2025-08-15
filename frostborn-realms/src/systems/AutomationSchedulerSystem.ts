import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class AutomationSchedulerSystem implements System {
  id = 'automationScheduler';
  private timer = 0;
  automationLevel = 0;
  constructor(private em: EntityManager, private world: World, private getComposite: () => { automationLevel: number; logisticsModifier: number }) {}

  update(dt: number): void {
    this.timer += dt;
    if (this.timer < 6) return;
    this.timer = 0;
    const comp = this.getComposite();
    this.automationLevel = comp.automationLevel;
    if (this.automationLevel <= 0.05) return;

    // Determine shortages
    const food = this.world.resourceStock['food_frozen'] || 0;
    const population = this.em.role.size;
    const dailyNeed = population * 2;
    if (food < dailyNeed * 2) {
      // spawn gather tasks with priority scaled
      for (let i = 0; i < Math.ceil(this.automationLevel * 3); i++) {
        const tile = this.world.tiles[Math.floor(Math.random() * this.world.tiles.length)];
        if (!tile || !tile.resource) continue;
        this.em.createTask('gather_resource', { x: tile.x, y: tile.y }, 0.5 + this.automationLevel * 0.3);
      }
    }

    // Ensure some scout tasks if high automation
    if (this.automationLevel > 0.2) {
      for (let i = 0; i < 2; i++) {
        const rx = Math.floor(this.world.spawnX + (Math.random() * 120 - 60));
        const ry = Math.floor(this.world.spawnY + (Math.random() * 120 - 60));
        if (this.world.getTile(rx, ry)) {
          this.em.createTask('scout_area', { x: rx, y: ry }, 0.2);
        }
      }
    }
  }
}