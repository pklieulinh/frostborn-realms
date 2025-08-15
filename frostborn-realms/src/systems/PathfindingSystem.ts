import { System } from '../core/ecs/Systems';

export class PathfindingSystem implements System {
  id = 'path';
  update(): void {
    // Path handled ad-hoc per agent to simplify MVP
  }
}