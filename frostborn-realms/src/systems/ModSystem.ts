import { System } from '../core/ecs/Systems';
import { DataRegistry } from '../data/registry';

export class ModSystem implements System {
  id = 'mod';
  constructor(private data: DataRegistry) {}
  update(): void {}
  setData(d: DataRegistry) { this.data = d; }
}