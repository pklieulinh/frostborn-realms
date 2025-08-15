import { Application, Container, Sprite, Texture } from 'pixi.js';
import { World } from '../world/World';
import { EntityManager } from '../core/ecs/EntityManager';
import { AssetLoader } from '../assets/AssetLoader';

export class RenderingSystem {
  private stage: Container;
  private sprites = new Map<number, Sprite>();
  constructor(app: Application, private world: World, private em: EntityManager, private loader: AssetLoader) {
    this.stage = app.stage;
  }
  attach(id: number, texId: string) {
    if (this.sprites.has(id)) return;
    const tex = this.loader.resolve(texId) as Texture;
    const sp = new Sprite(tex);
    sp.anchor.set(0.5);
    this.stage.addChild(sp);
    this.sprites.set(id, sp);
  }
  update() {
    // Example ECS linking; adjust to your components
    const positionStore = (this.em as any).position;
    if (!positionStore) return;
    for (const [id, sp] of this.sprites) {
      const pos = positionStore.get(id);
      if (!pos) continue;
      sp.x = pos.x * 16;
      sp.y = pos.y * 16;
    }
  }
}