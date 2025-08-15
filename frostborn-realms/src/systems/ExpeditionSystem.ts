import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';
import { DataRegistry } from '../data/registry';

export class ExpeditionSystem implements System {
  id = 'expedition';
  update(): void {
    const now = performance.now();
    for (const exp of this.em.expeditions) {
      if (exp.status === 'ongoing' && now >= exp.eta) {
        this.resolveAbstract(exp);
      }
    }
  }
  resolveAbstract(exp: any) {
    const biome = this.data.portalBiomes[Math.floor(Math.random() * this.data.portalBiomes.length)];
    const riskFactor = exp.risk;
    const success = Math.random() > riskFactor * 0.5;
    if (success) {
      const lootRolls = 3 + Math.floor(Math.random() * 2);
      const loot: { resource: string; qty: number }[] = [];
      const totalWeight = biome.lootTable.reduce((a, b) => a + b.weight, 0);
      for (let i = 0; i < lootRolls; i++) {
        let r = Math.random() * totalWeight;
        for (const l of biome.lootTable) {
          if (r < l.weight) {
            const qty = l.min + Math.floor(Math.random() * (l.max - l.min + 1));
            loot.push({ resource: l.resource, qty });
            break;
          }
          r -= l.weight;
        }
      }
      exp.result = { success: true, loot, biome: biome.id };
      for (const l of loot) this.world.addResource(l.resource, l.qty);
    } else {
      exp.result = { success: false, casualties: Math.random() < 0.3 };
      if (exp.result.casualties) {
        if (exp.members.length) {
          const lost = exp.members.pop();
          if (lost) this.em.removeEntity(lost);
        }
      }
    }
    exp.status = 'done';
  }
  createRealtimeExpedition(members: number[]) {
    const exp = this.em.createExpedition(members, Math.floor(Math.random()*1e9), 0.4, 'mixed', 99999);
    exp.realtime = this.generateRealtimeMap();
    return exp;
  }
  generateRealtimeMap() {
    const size = 16;
    const terrain = [];
    for (let y=0;y<size;y++){
      const row = [];
      for (let x=0;x<size;x++){
        row.push(Math.random()<0.15?1:0);
      }
      terrain.push(row);
    }
    return {
      size,
      terrain,
      party: { x:0, y:0 },
      goal: { x:size-1, y:size-1 },
      encounters: [],
      done: false,
      timer: 0,
      canvas: null
    };
  }
  serialize() {
    return { expeditions: this.em.expeditions };
  }
  deserialize(json: any) {
    this.em.expeditions = json.expeditions;
  }
  constructor(private em: EntityManager, private world: World, private data: DataRegistry) {}
}