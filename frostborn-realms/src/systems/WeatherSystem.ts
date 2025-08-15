import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class WeatherSystem implements System {
  id = 'weather';
  accum = 0;
  constructor(private em: EntityManager, private world: World) {}
  update(dt: number): void {
    this.accum += dt;
    if (this.accum > 5) {
      this.accum = 0;
      if (this.em.weather.storms.length < 3 && Math.random() < 0.4) {
        this.em.weather.storms.push({
          id: Date.now() + Math.floor(Math.random() * 1000),
          type: Math.random() < 0.5 ? 'squall' : 'blizzard',
          x: Math.random() * this.world.width,
          y: Math.random() * this.world.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          strength: 5 + Math.random() * 8
        });
      }
    }
    for (const s of this.em.weather.storms) {
      s.x += s.vx;
      s.y += s.vy;
      if (s.x < 0 || s.y < 0 || s.x >= this.world.width || s.y >= this.world.height) {
        s.x = Math.random() * this.world.width;
        s.y = Math.random() * this.world.height;
      }
    }
  }
}