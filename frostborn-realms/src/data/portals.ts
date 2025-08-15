export interface PortalBiome {
  id: string;
  title: string;
  difficulty: number;
  resourceBias: { [res: string]: number };
  monsterPool: { monster: string; weight: number }[];
  lootTable: { resource: string; min: number; max: number; weight: number }[];
  description: string;
}
export const PORTAL_BIOMES: PortalBiome[] = [
  {
    id: 'glacier_field',
    title: 'Trường Băng Nứt',
    difficulty: 1,
    resourceBias: { wood_frost: 0.6, ore_ice: 1.0, food_frozen: 0.8, crystal_chill: 0.2 },
    monsterPool: [
      { monster: 'frost_wolf', weight: 8 },
      { monster: 'shardling', weight: 2 }
    ],
    lootTable: [
      { resource: 'wood_frost', min: 15, max: 40, weight: 6 },
      { resource: 'ore_ice', min: 10, max: 30, weight: 6 },
      { resource: 'food_frozen', min: 20, max: 50, weight: 4 },
      { resource: 'crystal_chill', min: 2, max: 6, weight: 1 }
    ],
    description: 'Khu băng vỡ, độ nguy hiểm thấp.'
  },
  {
    id: 'crystal_cavern',
    title: 'Hang Tinh Thể',
    difficulty: 2,
    resourceBias: { wood_frost: 0.2, ore_ice: 0.8, crystal_chill: 1.0, essence_frost: 0.1 },
    monsterPool: [
      { monster: 'shardling', weight: 7 },
      { monster: 'frost_wolf', weight: 3 }
    ],
    lootTable: [
      { resource: 'ore_ice', min: 20, max: 40, weight: 4 },
      { resource: 'crystal_chill', min: 4, max: 12, weight: 5 },
      { resource: 'essence_frost', min: 1, max: 2, weight: 1 }
    ],
    description: 'Hang động rực ánh tinh thể.'
  },
  {
    id: 'void_frost_rift',
    title: 'Khe Hàn Hư Không',
    difficulty: 3,
    resourceBias: { crystal_chill: 0.8, essence_frost: 1.0 },
    monsterPool: [
      { monster: 'void_ice_serpent', weight: 5 },
      { monster: 'shardling', weight: 4 }
    ],
    lootTable: [
      { resource: 'crystal_chill', min: 6, max: 18, weight: 6 },
      { resource: 'essence_frost', min: 1, max: 3, weight: 3 },
      { resource: 'core_heat', min: 2, max: 5, weight: 2 }
    ],
    description: 'Vùng vỡ cấu trúc không gian, nguy hiểm cao.'
  }
];