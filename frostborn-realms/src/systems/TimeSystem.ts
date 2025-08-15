import { System } from '../core/ecs/Systems';

export class TimeSystem implements System {
  id = 'time';
  elapsed = 0;
  update(dt: number) { this.elapsed += dt; }
}