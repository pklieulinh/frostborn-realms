import { DataRegistry } from '../data/registry';
import { RNG } from '../core/math/Random';

export function randomPortalBiome(rng: RNG, data: DataRegistry) {
  return rng.pick(data.portalBiomes);
}