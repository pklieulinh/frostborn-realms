import { AssetLoader } from './AssetLoader';
import { Texture } from 'pixi.js';

export class TextureResolver {
  private missCache = new Set<string>();
  constructor(private loader: AssetLoader) {}

  resolve(id: string): Texture {
    if (this.loader.has(id)) return this.loader.getTexture(id)!;
    if (!this.missCache.has(id)) {
      console.warn('[TextureResolver] missing id -> placeholder', id);
      this.missCache.add(id);
    }
    return this.loader.resolve(id);
  }
}