import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';
import { DataRegistry } from '../data/registry';
import { StrategicPlanner } from '../ai/StrategicPlanner';
import { UISystem } from './UISystem';

export class AIStrategicSystem implements System {
  id = 'aiStrategic';
  planner: StrategicPlanner;
  timer = 0;
  interval = 5;
  intervention = false;
  constructor(private em: EntityManager, private world: World, private data: DataRegistry, private ui: UISystem) {
    this.planner = new StrategicPlanner(data, world, em);
  }
  update(dt: number): void {
    this.timer += dt;
    if (this.timer >= this.interval) {
      this.timer = 0;
      this.planner.evaluate(this.intervention, (q) => this.ui.promptDecision(q));
      this.ui.setStrategicDecisions(this.planner.lastDecisions);
    }
  }
  toggleIntervention(v: boolean) { this.intervention = v; }
}