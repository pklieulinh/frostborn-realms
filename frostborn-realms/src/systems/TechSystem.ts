import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';
import { DataRegistry, TechDef } from '../data/registry';

export class TechSystem implements System {
  id = 'tech';
  accum = 0;
  researchRate = 1;
  constructor(private em: EntityManager, private world: World, private data: DataRegistry) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 1) return;
    this.accum = 0;
    const active = this.em.tech.active;
    if (!active) return;
    const tech = this.data.map.techById[active];
    if (!tech) { this.em.tech.active = undefined; return; }
    if (!this.canAfford(tech)) return;
    this.em.tech.progress[active] = (this.em.tech.progress[active] || 0) + this.researchRate;
    if (this.em.tech.progress[active] >= tech.time) {
      this.payCost(tech);
      this.unlock(tech);
      this.em.tech.active = undefined;
    }
  }
  setActive(id: string) {
    if (this.em.tech.unlocked.has(id)) return;
    const tech = this.data.map.techById[id];
    if (!tech) return;
    if (!tech.requires.every(r => this.em.tech.unlocked.has(r))) return;
    this.em.tech.active = id;
  }
  unlock(tech: TechDef) {
    this.em.tech.unlocked.add(tech.id);
    const u = tech.unlocks;
    // Future: dynamic enabling
  }
  canAfford(tech: TechDef) {
    return tech.cost.every(c => (this.world.resourceStock[c.resource] || 0) >= c.qty);
  }
  payCost(tech: TechDef) {
    for (const c of tech.cost) this.world.consumeResource(c.resource, c.qty);
  }
  reloadData(data: DataRegistry) { this.data = data; }
}