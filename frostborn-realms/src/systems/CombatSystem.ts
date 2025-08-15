import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class CombatSystem implements System {
  id = 'combat';
  accum = 0;
  constructor(private em: EntityManager, private world: World) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 0.3) return;
    this.accum = 0;
    // Simple collision combat: Guards vs Monsters
    const guards: number[] = [];
    const monsters: number[] = [];
    for (const [id, role] of this.em.role.entries()) {
      if (role.role === 'Guard') guards.push(id);
      else if (role.role === 'Monster') monsters.push(id);
    }
    for (const gid of guards) {
      const gpos = this.em.position.get(gid);
      const gstats = this.em.stats.get(gid);
      if (!gpos || !gstats) continue;
      for (const mid of monsters) {
        const mpos = this.em.position.get(mid);
        const mstats = this.em.stats.get(mid);
        if (!mpos || !mstats) continue;
        const dist = Math.hypot(gpos.x - mpos.x, gpos.y - mpos.y);
        if (dist < 1.2) {
          const gDmg = Math.max(1, gstats.attack - mstats.defense);
            mstats.hp -= gDmg;
          const mDmg = Math.max(1, mstats.attack - gstats.defense);
            gstats.hp -= mDmg;
        }
      }
    }
    // Death & loot
    for (const [id, stats] of Array.from(this.em.stats.entries())) {
      if (stats.hp <= 0) {
        const role = this.em.role.get(id);
        if (role?.role === 'Monster') {
          const mtag = this.em.monster.get(id);
          if (mtag) {
            // Loot from monster def
            // (Loot distribution handled by MonsterAISystem on spawn maybe, simplified)
          }
        }
        this.em.removeEntity(id);
      }
    }
  }
}