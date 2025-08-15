import { System } from '../core/ecs/Systems';
import { DataRegistry } from '../data/registry';
import { World } from '../world/World';
import { UISystem } from './UISystem';
import { EventWeightSystem } from './EventWeightSystem';
import { EntityManager } from '../core/ecs/EntityManager';

interface ActiveEvent {
  id: string;
  remaining: number;
  effects: any;
}

export class EventSystem implements System {
  id = 'event';
  cooldowns: Record<string, number> = {};
  active: ActiveEvent[] = [];
  elapsed = 0;
  constructor(private data: DataRegistry, private world: World, private ui: UISystem,
              private weightSys: EventWeightSystem, private em: EntityManager) {}
  update(dt: number): void {
    this.elapsed += dt;
    for (const ev of this.active) ev.remaining -= dt;
    this.active = this.active.filter(a => a.remaining > 0);

    for (const e of this.data.events) {
      this.cooldowns[e.id] = Math.max(0, (this.cooldowns[e.id] || 0) - dt);
      if (this.cooldowns[e.id] <= 0) {
        const mult = this.weightSys.multipliers[e.id] ?? 1;
        const chance = e.baseChance * mult * dt;
        if (Math.random() < chance) {
          this.trigger(e.id);
          this.cooldowns[e.id] = e.cooldown;
        }
      }
    }

    // Aggregate effects
    let tempDelta = 0;
    let portalBoost = 0;
    for (const ev of this.active) {
      if (ev.effects.temperatureDelta) tempDelta += ev.effects.temperatureDelta;
      if (ev.effects.portalBoost) portalBoost += ev.effects.portalBoost;
    }
    this.world.portalBoost = portalBoost;
    this.world.ambientTemp = -12 + tempDelta;
  }

  trigger(id: string) {
    const def = this.data.map.eventById[id];
    if (!def) return;
    this.active.push({ id, remaining: def.effects.duration || 10, effects: def.effects });
    this.ui.pushEventFeed(`Sự kiện: ${def.title}`);
    if (this.em.analytics) {
      this.em.analytics.eventsCount[id] = (this.em.analytics.eventsCount[id] || 0) + 1;
    }
    // Spawn monsters if spawn effect
    if (def.effects.spawn) {
      const count = def.effects.count || 1;
      for (let i = 0; i < count; i++) {
        const e = this.spawnMonster(def.effects.spawn);
        if (!e) break;
      }
    }
  }

  spawnMonster(monsterId: string): number | null {
    const mDef = this.data.map.monsterById[monsterId];
    if (!mDef) return null;
    const e = this.em.createEntity();
    const angle = Math.random() * Math.PI * 2;
    const dist = 25 + Math.random() * 10;
    const x = this.world.spawnX + Math.cos(angle) * dist;
    const y = this.world.spawnY + Math.sin(angle) * dist;
    this.em.position.set(e, { x, y });
    this.em.role.set(e, { role: 'Monster' });
    this.em.stats.set(e, { hp: mDef.hp, maxHp: mDef.hp, fatigue: 0, cold: 0, attack: mDef.attack, defense: mDef.defense });
    this.em.monster.set(e, { monsterId, hostile: true });
    return e;
  }

  serialize() {
    return { cooldowns: this.cooldowns, active: this.active, elapsed: this.elapsed };
  }
  deserialize(json: any) {
    this.cooldowns = json.cooldowns;
    this.active = json.active;
    this.elapsed = json.elapsed;
  }
}