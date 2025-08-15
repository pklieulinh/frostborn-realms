import { RESOURCE_DEFS_V2 } from './base_pack_v2/resources';
import { BASE_RECIPES, RecipeDef } from './recipes';

export interface ResourceDef { id: string; title: string; rarity: string; stack: number; baseValue: number; tags: string[]; description: string; }
export interface ItemDef { id: string; title: string; type: string; rarity: string; description: string; effects?: Record<string, number>; }
export interface BuildingDef { id: string; title: string; category: string; cost: { resource: string; qty: number }[]; buildTime: number; provides?: Record<string, number>; unlock?: string[]; aiWeight?: Record<string, number>; description: string; tier?: number; upkeep?: { resource: string; qty: number }[]; effects?: Record<string, number>; }
export interface MonsterDef { id: string; title: string; tier: number; hp: number; attack: number; defense: number; speed: number; traits: string[]; loot: { resource: string; min: number; max: number; chance: number }[]; description: string; }
export interface EventDef { id: string; title: string; type: string; baseChance: number; cooldown: number; description: string; effects: Record<string, any>; severity?: number; }
export interface PortalBiome { id: string; title: string; difficulty: number; resourceBias: Record<string, number>; monsterPool: { monster: string; weight: number }[]; lootTable: { resource: string; min: number; max: number; weight: number }[]; description: string; }
export interface TechDef { id: string; title: string; tier: number; cost: { resource: string; qty: number }[]; time: number; requires: string[]; unlocks: { buildings?: string[]; items?: string[]; events?: string[]; monsters?: string[]; passive?: string[] }; description: string; }

export interface DataRegistry {
  resources: ResourceDef[];
  items: ItemDef[];
  buildings: BuildingDef[];
  monsters: MonsterDef[];
  events: EventDef[];
  portalBiomes: PortalBiome[];
  techs: TechDef[];
  recipes: RecipeDef[];
  map: {
    resourceById: Record<string, ResourceDef>;
    itemById: Record<string, ItemDef>;
    buildingById: Record<string, BuildingDef>;
    monsterById: Record<string, MonsterDef>;
    eventById: Record<string, EventDef>;
    techById: Record<string, TechDef>;
    recipeById: Record<string, RecipeDef>;
    portalBiomeById: Record<string, PortalBiome>;
    recipesByCategory: Record<string, RecipeDef[]>;
  };
}

export function loadDataRegistry(): DataRegistry {
  const base: DataRegistry = {
    resources: [...RESOURCE_DEFS_V2],
    items: [],
    buildings: [],
    monsters: [],
    events: [],
    portalBiomes: [
      {
        id: 'glacier_field',
        title: 'Trường Băng Nứt',
        difficulty: 1,
        resourceBias: { wood_frost: 0.6, ore_ice: 1, food_frozen: 0.8, crystal_chill: 0.2 },
        monsterPool: [{ monster: 'frost_wolf', weight: 8 }, { monster: 'shardling', weight: 2 }],
        lootTable: [
          { resource: 'wood_frost', min: 15, max: 40, weight: 6 },
            { resource: 'ore_ice', min: 10, max: 30, weight: 6 },
            { resource: 'food_frozen', min: 20, max: 50, weight: 4 },
            { resource: 'crystal_chill', min: 2, max: 6, weight: 1 }
        ],
        description: 'Khu băng vỡ.'
      }
    ],
    techs: [],
    recipes: [...BASE_RECIPES],
    map: {
      resourceById: {},
      itemById: {},
      buildingById: {},
      monsterById: {},
      eventById: {},
      techById: {},
      recipeById: {},
      portalBiomeById: {},
      recipesByCategory: {}
    }
  };
  indexMaps(base);
  return base;
}

function indexMaps(reg: DataRegistry) {
  reg.map.resourceById = {}; reg.resources.forEach(r => reg.map.resourceById[r.id] = r);
  reg.map.itemById = {}; reg.items.forEach(r => reg.map.itemById[r.id] = r);
  reg.map.buildingById = {}; reg.buildings.forEach(r => reg.map.buildingById[r.id] = r);
  reg.map.monsterById = {}; reg.monsters.forEach(r => reg.map.monsterById[r.id] = r);
  reg.map.eventById = {}; reg.events.forEach(r => reg.map.eventById[r.id] = r);
  reg.map.techById = {}; reg.techs.forEach(r => reg.map.techById[r.id] = r);
  reg.map.recipeById = {}; reg.recipes.forEach(r => reg.map.recipeById[r.id] = r);
  reg.map.portalBiomeById = {}; reg.portalBiomes.forEach(r => reg.map.portalBiomeById[r.id] = r);
  reg.map.recipesByCategory = {};
  for (const rec of reg.recipes) {
    const cats = new Set<string>();
    if (rec.buildingCategories) for (const c of rec.buildingCategories) cats.add(c);
    if (rec.buildingIds) for (const bid of rec.buildingIds) cats.add('id:' + bid);
    for (const c of cats) {
      if (!reg.map.recipesByCategory[c]) reg.map.recipesByCategory[c] = [];
      reg.map.recipesByCategory[c].push(rec);
    }
  }
}

const MOD_FILES = ['base_pack_v2.json', 'base_pack_v3.json', 'base_pack_v4.json'];

export async function loadAndMergeMods(base: DataRegistry): Promise<DataRegistry> {
  const merged: DataRegistry = {
    ...base,
    resources: [...base.resources],
    items: [...base.items],
    buildings: [...base.buildings],
    monsters: [...base.monsters],
    events: [...base.events],
    portalBiomes: [...base.portalBiomes],
    techs: [...base.techs],
    recipes: [...base.recipes],
    map: { ...base.map }
  };
  for (const file of MOD_FILES) {
    try {
      const res = await fetch(`/mods/${file}`);
      if (!res.ok) continue;
      const json = await res.json();
      mergeCategory(merged.resources, json.resources || []);
      mergeCategory(merged.items, json.items || []);
      mergeCategory(merged.buildings, json.buildings || []);
      mergeCategory(merged.monsters, json.monsters || []);
      mergeCategory(merged.events, json.events || []);
      mergeCategory(merged.portalBiomes, json.portalBiomes || []);
      mergeCategory(merged.techs, json.techs || []);
      mergeCategory(merged.recipes, json.recipes || []);
    } catch (e) {
      console.warn('Mod load failed', file, e);
    }
  }
  indexMaps(merged);
  (window as any).gameData = merged;
  return merged;
}

function mergeCategory(arr: any[], incoming: any[]) {
  for (const elem of incoming) {
    const idx = arr.findIndex(e => e.id === elem.id);
    if (idx >= 0) arr[idx] = elem; else arr.push(elem);
  }
}