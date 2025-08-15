import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class MoraleSystem implements System {
  id = 'morale';
  accum = 0;
  constructor(private em: EntityManager, private world: World) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 2) return;
    this.accum = 0;
    let totalMorale = 0;
    let count = 0;
    for (const [id, mood] of this.em.mood.entries()) {
      const stats = this.em.stats.get(id);
      if (!stats) continue;
      const coldPenalty = this.world.avgTemp < -15 ? 2 : (this.world.avgTemp < -12 ? 1 : 0);
      const fatiguePenalty = stats.fatigue > 80 ? 2 : (stats.fatigue > 60 ? 1 : 0);
      const baseDrift = -coldPenalty - fatiguePenalty;
      mood.morale += baseDrift;
      if (mood.morale < 0) mood.morale = 0;
      if (mood.morale > 120) mood.morale = 120;
      // Sanity drift
      const sanityPenalty = this.world.threatIndex > 0.5 ? 1 : 0;
      mood.sanity += -sanityPenalty;
      if (mood.sanity < 0) mood.sanity = 0;
      if (mood.sanity > 120) mood.sanity = 120;
      // Productivity mapping
      mood.productivityMod = (0.5 + mood.morale / 200) * (0.6 + mood.sanity / 200);
      mood.fatigueMod = 1 + (mood.morale < 40 ? 0.2 : 0);
      totalMorale += mood.morale;
      count++;
    }
    if (count > 0) {
      const avg = totalMorale / count;
      // Light influence on threat perception
      if (avg < 30) this.world.threatIndex = Math.min(1, this.world.threatIndex + 0.02);
    }
  }
}