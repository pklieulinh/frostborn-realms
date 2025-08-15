export interface ItemDef {
  id: string;
  title: string;
  type: string;
  rarity: string;
  description: string;
  effects?: { [k: string]: number };
}
export const ITEM_DEFS: ItemDef[] = [
  {
    id: 'tool_basic_pick',
    title: 'Cuốc Băng Thô',
    type: 'tool',
    rarity: 'common',
    description: 'Dụng cụ cơ bản giúp tăng tốc đào quặng lạnh.',
    effects: { gather_ore_ice_speed: 0.15 }
  },
  {
    id: 'tool_basic_axe',
    title: 'Rìu Lạnh',
    type: 'tool',
    rarity: 'common',
    description: 'Rìu nhẹ dễ dùng, tăng khai thác gỗ lạnh.',
    effects: { gather_wood_frost_speed: 0.15 }
  },
  {
    id: 'amulet_chill_focus',
    title: 'Bùa Tập Trung Băng',
    type: 'trinket',
    rarity: 'uncommon',
    description: 'Ổn định tinh thần, giảm mệt mỏi.',
    effects: { fatigue_rate: -0.1 }
  },
  {
    id: 'core_heat_condensor',
    title: 'Bộ Ngưng Tụ Nhiệt',
    type: 'device',
    rarity: 'uncommon',
    description: 'Tăng hiệu suất chuyển đổi nhiệt lượng.',
    effects: { heat_generation: 0.2 }
  },
  {
    id: 'sigil_frost_overmind',
    title: 'Ấn Băng Chủ Tể',
    type: 'artifact',
    rarity: 'rare',
    description: 'Tăng hiệu quả ra quyết định của Thủ Lĩnh.',
    effects: { leader_decision_quality: 0.25 }
  }
];