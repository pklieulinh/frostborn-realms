import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';

export class ExpeditionRealtimeSystem implements System {
  id = 'expRealtime';
  constructor(private em: EntityManager) {}
  update(dt: number): void {
    for (const exp of this.em.expeditions) {
      if (!exp.realtime) continue;
      if (exp.status !== 'ongoing') continue;
      const map = exp.realtime;
      map.timer += dt;
      if (map.timer > 0.5) {
        map.timer = 0;
        // Move party
        if (map.party.x < map.goal.x) map.party.x++;
        if (map.party.y < map.goal.y) map.party.y++;
        if (map.party.x === map.goal.x && map.party.y === map.goal.y) {
          map.done = true;
        }
        // Random encounter
        if (Math.random() < 0.15) {
          map.encounters.push({ id: 'hostile', options: ['Aggressive', 'Cautious', 'Retreat'], resolved: false });
        }
      }
    }
  }
}