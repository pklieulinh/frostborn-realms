import { DataRegistry } from '../data/registry';
import { World } from '../world/World';
import { EntityManager } from '../core/ecs/EntityManager';
import { computeMetrics } from './Blackboard';

export interface StrategicDecision {
  id: string;
  priority: number;
  rationale: string[];
  action: () => void;
}

export class StrategicPlanner {
  lastDecisions: StrategicDecision[] = [];
  constructor(private data: DataRegistry, private world: World, private em: EntityManager) {}

  evaluate(intervention: boolean, uiAsk: (q: { title: string; options: { id: string; label: string; cb: () => void }[] }) => void) {
    const metrics = computeMetrics(this.em, this.world);
    const decisionPool: StrategicDecision[] = [];
    const rationaleMap: string[] = [];
    for (const h of this.data.heuristics) {
      const weight = h.check(metrics);
      if (weight > 0) {
        const r = h.rationale(metrics);
        if (r) rationaleMap.push(r);
      }
    }
    // Build Housing
    const housingNeed = metrics.population / Math.max(1, metrics.housingCapacity) > 0.85;
    if (housingNeed) {
      decisionPool.push({
        id: 'build_housing',
        priority: 0.8,
        rationale: ['Thiếu chỗ ở'],
        action: () => this.queueBuilding('tent')
      });
    }
    // Storage
    if (metrics.storageUsed / Math.max(1, metrics.storageCapacity) > 0.8) {
      decisionPool.push({
        id: 'build_storage',
        priority: 0.7,
        rationale: ['Kho đầy'],
        action: () => this.queueBuilding('storehouse')
      });
    }
    // Heat
    if (metrics.avgTemp < -15) {
      decisionPool.push({
        id: 'build_heat',
        priority: 0.75,
        rationale: ['Rất lạnh'],
        action: () => this.queueBuilding('heat_tower')
      });
    }
    // Expedition
    if (metrics.rareStock < 10 && metrics.threatIndex < 0.3) {
      decisionPool.push({
        id: 'send_expedition',
        priority: 0.55,
        rationale: ['Cần nguyên liệu hiếm', 'Thấp nguy cơ'],
        action: () => this.planExpedition()
      });
    }
    // Research building mid stage
    if (this.world.rareStock > 5 && !this.anyBuilt('research_node')) {
      decisionPool.push({
        id: 'build_research',
        priority: 0.6,
        rationale: ['Có tinh thể đủ mở nghiên cứu'],
        action: () => this.queueBuilding('research_node')
      });
    }
    decisionPool.sort((a, b) => b.priority - a.priority);
    this.lastDecisions = decisionPool.slice(0, 3);
    if (this.lastDecisions.length) {
      const top = this.lastDecisions[0];
      if (intervention) {
        uiAsk({
          title: 'Quyết định chiến lược',
            options: [
              {
                id: 'accept',
                label: 'Thực hiện: ' + top.id,
                cb: () => top.action()
              },
              {
                id: 'skip',
                label: 'Bỏ qua',
                cb: () => {}
              }
            ]
        });
      } else {
        top.action();
      }
    }
  }

  queueBuilding(id: string) {
    const def = this.data.map.buildingById[id];
    if (!def) return;
    // Check cost
    for (const c of def.cost) {
      if ((this.world.resourceStock[c.resource] || 0) < c.qty) return;
    }
    for (const c of def.cost) this.world.consumeResource(c.resource, c.qty);
    // Spawn entity with construction
    const e = this.em.createEntity();
    // Pick free tile near hub
    const hx = this.world.spawnX;
    const hy = this.world.spawnY;
    let px = hx, py = hy;
    for (let r = 2; r < 30; r++) {
      let placed = false;
      for (let tries = 0; tries < 20; tries++) {
        const tx = hx + Math.floor(Math.random() * r * 2 - r);
        const ty = hy + Math.floor(Math.random() * r * 2 - r);
        const tile = this.world.getTile(tx, ty);
        if (!tile || tile.building) continue;
        px = tx; py = ty; placed = true; break;
      }
      if (placed) break;
    }
    this.em.position.set(e, { x: px, y: py });
    this.em.construction.set(e, { building: id, progress: 0, x: px, y: py });
  }

  planExpedition() {
    // pick some scouts / guards
    const candidates: number[] = [];
    for (const [id, role] of this.em.role.entries()) {
      if (role.role === 'Scout' || role.role === 'Guard') candidates.push(id);
    }
    if (candidates.length < 2) return;
    const members = candidates.slice(0, 3);
    // Create a pseudo task letting Expedition System pick up
    this.em.createTask('expedition_form', { members }, 0.5);
  }

  anyBuilt(id: string) {
    // Heuristic: check World tiles
    return !!this.world.tiles.find(t => t.building?.id === id);
  }
}