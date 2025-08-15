import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';
import { LocalAI } from '../ai/LocalAI';

export class AILocalSystem implements System {
  id = 'aiLocal';
  local: LocalAI;
  constructor(private em: EntityManager, private world: World) {
    this.local = new LocalAI(em, world);
  }
  update(dt: number): void {
    for (const id of this.em.role.keys()) {
      this.local.updateAgent(id, dt);
    }
  }
}