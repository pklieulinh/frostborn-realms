export interface MonsterDef {
  id: string;
  title: string;
  tier: number;
  hp: number;
  damage: number;
  traits: string[];
  loot: { resource: string; min: number; max: number; chance: number }[];
  description: string;
}
export const MONSTER_DEFS: MonsterDef[] = [
  {
    id: 'frost_wolf',
    title: 'Sói Băng',
    tier: 1,
    hp: 40,
    damage: 6,
    traits: ['fast', 'pack'],
    loot: [{ resource: 'food_frozen', min: 2, max: 5, chance: 0.9 }],
    description: 'Thú săn theo bầy, xuất hiện khi thiếu phòng thủ.'
  },
  {
    id: 'shardling',
    title: 'Tinh Thể Dị Sinh',
    tier: 2,
    hp: 60,
    damage: 9,
    traits: ['crystal'],
    loot: [{ resource: 'crystal_chill', min: 1, max: 3, chance: 0.7 }],
    description: 'Sinh vật kết tinh từ năng lượng portal.'
  },
  {
    id: 'void_ice_serpent',
    title: 'Hàn Xà Hư Không',
    tier: 3,
    hp: 120,
    damage: 18,
    traits: ['elite', 'cold_aura'],
    loot: [
      { resource: 'essence_frost', min: 1, max: 2, chance: 0.5 },
      { resource: 'crystal_chill', min: 2, max: 5, chance: 1.0 }
    ],
    description: 'Quái vật cổng nguy hiểm, hiếm gặp.'
  }
];