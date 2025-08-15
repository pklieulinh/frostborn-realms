import { EventBus } from '../core/events/EventBus';
import { RNG } from '../core/math/Random';
import { EntityManager } from '../core/ecs/EntityManager';
import { DataRegistry } from '../data/registry';

export interface Tile {
  biome: string;
  x: number;
  y: number;
  resource?: { id: string; qty: number };
  discovered: boolean;
  portal?: { seed: number; biome: string; active: boolean };
  tempOffset: number;
  building?: { id: string; entity: number };
  visibility?: number;
}

export class World {
  tiles: Tile[] = [];
  rng = new RNG();
  ambientTemp = -12;
  spawnX = 32;
  spawnY = 32;
  housingCapacity = 0;
  storageCapacity = 0;
  storageUsed = 0;
  resourceStock: Record<string, number> = {};
  rareStock = 0;
  avgTemp = -12;
  threatIndex = 0;
  portalBoost = 0;
  constructor(public width: number, public height: number, private data: DataRegistry, private bus: EventBus) {}
  setData(d: DataRegistry) { this.data = d; }
  generateInitial() {
    this.tiles.length = 0;
    for (let y = 0; y < this.height; y++)
      for (let x = 0; x < this.width; x++) {
        const biome = this.data.portalBiomes.length ? this.data.portalBiomes[0].id : 'glacier_field';
        this.tiles.push({ biome, x, y, discovered: Math.abs(x - this.spawnX) < 14 && Math.abs(y - this.spawnY) < 14, tempOffset: 0, visibility: 1 });
      }
    this.spawnResources();
  }
  spawnResources() {
    for (const t of this.tiles) {
      if (Math.random() < 0.04) {
        const pick = this.rng.pick(this.data.resources);
        t.resource = { id: pick.id, qty: 10 + Math.floor(Math.random() * 40) };
      }
    }
  }
  getTile(x: number, y: number): Tile | undefined {
    if (x < 0 || y < 0 || x >= this.width || y >= this.height) return;
    return this.tiles[x + y * this.width];
  }
  placeInitialHub(em: EntityManager) {
    const hubEntity = em.createEntity();
    em.position.set(hubEntity, { x: this.spawnX, y: this.spawnY });
    em.construction.set(hubEntity, { building: 'hub_core', progress: 0, x: this.spawnX, y: this.spawnY });
    this.finishConstruction(hubEntity, { id: 'hub_core', provides: { storage: 400, heat: 8 } });
  }
  finishConstruction(entity: number, def: any) {
    const pos = (emPosGetter && emPosGetter(entity)) || { x: this.spawnX, y: this.spawnY };
    const tile = this.getTile(Math.floor(pos.x), Math.floor(pos.y));
    if (tile) tile.building = { id: def.id, entity };
    if (def.provides?.housing) this.housingCapacity += def.provides.housing;
    if (def.provides?.storage) this.storageCapacity += def.provides.storage;
    this.bus.emit('buildingFinished', { entity, def });
  }
  addResource(id: string, qty: number) {
    this.resourceStock[id] = (this.resourceStock[id] || 0) + qty;
    const def = (this.data as any).map?.resourceById[id];
    if (def && (def.rarity === 'uncommon' || def.rarity === 'rare' || def.rarity === 'epic')) {
      if (def.rarity === 'rare' || def.rarity === 'epic') this.rareStock += qty;
    }
    this.recalculateStorageUsed();
  }
  consumeResource(id: string, qty: number): boolean {
    if ((this.resourceStock[id] || 0) >= qty) {
      this.resourceStock[id] -= qty;
      this.recalculateStorageUsed();
      return true;
    }
    return false;
  }
  recalculateStorageUsed() {
    this.storageUsed = Object.values(this.resourceStock).reduce((a, b) => a + b, 0);
  }
  updateDerivedMetrics(avgTemp: number, threat: number) {
    this.avgTemp = avgTemp;
    this.threatIndex = threat;
  }
  serialize() {
    return {
      width: this.width,
      height: this.height,
      tiles: this.tiles,
      ambientTemp: this.ambientTemp,
      spawnX: this.spawnX,
      spawnY: this.spawnY,
      housingCapacity: this.housingCapacity,
      storageCapacity: this.storageCapacity,
      storageUsed: this.storageUsed,
      resourceStock: this.resourceStock,
      rareStock: this.rareStock,
      avgTemp: this.avgTemp,
      threatIndex: this.threatIndex,
      portalBoost: this.portalBoost
    };
  }
  deserialize(json: any) {
    Object.assign(this, json);
  }
}

let emPosGetter: ((id: number) => { x: number; y: number } | undefined) | null = null;
export function registerEMPositionGetter(fn: (id: number) => { x: number; y: number } | undefined) {
  emPosGetter = fn;
}