import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';
import { DataRegistry } from '../data/registry';

export class EventWeightSystem implements System {
  id = 'eventWeight';
  multipliers: Record<string, number> = {};
  accum = 0;
  constructor(private em: EntityManager, private world: World, private data: DataRegistry) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 5) return;
    this.accum = 0;

    const moraleAvg = this.avgMorale();
    const sanityAvg = this.avgSanity();
    const food = this.world.resourceStock['food_frozen'] || 0;
    const population = this.em.role.size || 1;
    const scarcity = food / (population * 2);
    let scarcityFactor = scarcity < 1 ? (1 + (1 - scarcity)) : (scarcity > 3 ? 0.8 : 1);

    const monsterCount = Array.from(this.em.role.values()).filter(r => r.role === 'Monster').length;
    const threatProxy = monsterCount / (population || 1);

    const weatherVar = Math.abs(this.world.ambientTemp + 12) / 15;

    // Base multipliers by event type
    const typeFactor: Record<string, number> = {};

    typeFactor['morale'] = moraleAvg < 40 ? 1.6 : (moraleAvg > 80 ? 0.7 : 1);
    typeFactor['psy'] = sanityAvg < 45 ? 1.5 : (sanityAvg > 85 ? 0.6 : 1);
    typeFactor['economic'] = scarcityFactor > 1 ? 1.4 : 1;
    typeFactor['combat'] = threatProxy > 0.15 ? 1.3 : 0.9;
    typeFactor['weather'] = 0.9 + weatherVar * 0.4;
    typeFactor['portal'] = (this.world.portalBoost > 0 ? 1.2 : 0.95);
    typeFactor['plague'] = (sanityAvg < 50 || moraleAvg < 50) ? 1.25 : 0.85;
    typeFactor['expedition'] = (moraleAvg > 70 && threatProxy < 0.1) ? 1.3 : 0.9;
    typeFactor['arcane'] = (sanityAvg > 60 ? 1.1 : 0.95);

    this.multipliers = {};
    for (const ev of this.data.events) {
      const base = typeFactor[ev.type] ?? 1;
      // clamp
      this.multipliers[ev.id] = Math.min(2.5, Math.max(0.25, base));
    }
  }

  private avgMorale(): number {
    let sum = 0; let c = 0;
    for (const m of this.em.mood.values()) { sum += m.morale; c++; }
    return c ? sum / c : 60;
  }

  private avgSanity(): number {
    let sum = 0; let c = 0;
    for (const m of this.em.mood.values()) { sum += m.sanity; c++; }
    return c ? sum / c : 60;
  }
}