import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export class SpectatorSystem implements System {
  id = 'spectator';
  ws: WebSocket | null = null;
  enabled = false;
  accum = 0;
  constructor(private em: EntityManager, private world: World) {}
  connect(url: string) {
    if (this.ws) this.ws.close();
    this.ws = new WebSocket(url);
    this.ws.onopen = () => {};
    this.ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'snapshot' && this.enabled) {
        // Read-only mode could apply some view transform later
      }
    };
  }
  setEnabled(v: boolean) { this.enabled = v; }
  update(dt: number): void {
    if (!this.enabled || !this.ws || this.ws.readyState !== 1) return;
    this.accum += dt;
    if (this.accum > 4) {
      this.accum = 0;
      const snapshot = {
        world: { resources: this.world.resourceStock, temp: this.world.avgTemp, entities: this.em.role.size },
        time: Date.now()
      };
      this.ws.send(JSON.stringify({ type: 'injectSnapshot', payload: snapshot }));
    }
  }
}