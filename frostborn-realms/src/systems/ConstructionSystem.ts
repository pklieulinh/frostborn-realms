import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';

export class ConstructionSystem implements System {
  id = 'construction';
  update(): void {
    // handled in local AI task execution
  }
  constructor(private em: EntityManager) {}
}