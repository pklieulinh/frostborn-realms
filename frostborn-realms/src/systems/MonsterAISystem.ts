import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class MonsterAISystem implements System {
  id = 'monsterAI';
  accum = 0;
  constructor(private em: EntityManager, private world: World) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 0.2) return;
    this.accum = 0;
    for (const [id, role] of this.em.role.entries()) {
      if (role.role !== 'Monster') continue;
      const pos = this.em.position.get(id);
      const stats = this.em.stats.get(id);
      if (!pos || !stats) continue;
      // Acquire nearest non-monster
      let nearest: number | null = null;
      let best = 999;
      for (const [oid, orole] of this.em.role.entries()) {
        if (orole.role === 'Monster') continue;
        const opos = this.em.position.get(oid);
        if (!opos) continue;
        const dist = Math.hypot(opos.x - pos.x, opos.y - pos.y);
        if (dist < best) {
          best = dist;
          nearest = oid;
        }
      }
      if (nearest != null) {
        const tpos = this.em.position.get(nearest)!;
        const speed = 2.2;
        const dx = tpos.x - pos.x;
        const dy = tpos.y - pos.y;
        const d = Math.hypot(dx, dy);
        if (d > 0.1) {
          pos.x += (dx / d) * speed * 0.2;
          pos.y += (dy / d) * speed * 0.2;
        }
      }
    }
  }
}