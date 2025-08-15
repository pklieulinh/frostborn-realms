export interface RecipeDef {
  id: string;
  label: string;
  time: number;
  inputs: { resource: string; qty: number }[];
  outputs: { resource: string; qty: number }[];
  buildingIds?: string[];
  buildingCategories?: string[];
  tier: number;
  flags?: string[];
  description: string;
  basePower?: number;
}

export const BASE_RECIPES: RecipeDef[] = [
  {
    id: 'wood_refine_planks_basic',
    label: 'Tinh Chế Gỗ Lạnh (Planks)',
    time: 12,
    inputs: [{ resource: 'wood_frost', qty: 20 }],
    outputs: [{ resource: 'wood_resin', qty: 10 }],
    buildingCategories: ['production'],
    tier: 1,
    description: 'Chuyển đổi gỗ lạnh sang gỗ nhựa.',
    flags: ['refine']
  },
  {
    id: 'ore_smelting_iron',
    label: 'Luyện Sắt Hàn',
    time: 16,
    inputs: [{ resource: 'ore_iron_frost', qty: 14 }, { resource: 'core_heat', qty: 2 }],
    outputs: [{ resource: 'alloy_froststeel', qty: 6 }],
    buildingCategories: ['production'],
    tier: 2,
    description: 'Tạo hợp kim băng thép.',
    flags: ['smelt']
  },
  {
    id: 'alloy_mythril_forge',
    label: 'Luyện Mythril Băng',
    time: 28,
    inputs: [{ resource: 'ore_mythril_frost', qty: 6 }, { resource: 'core_heat_dense', qty: 2 }],
    outputs: [{ resource: 'alloy_cobalt_mythril', qty: 4 }],
    buildingIds: ['forge_void', 'final_forge'],
    tier: 3,
    description: 'Tạo hợp kim cobalt-mythril.',
    flags: ['smelt', 'advanced']
  },
  {
    id: 'crystal_focus_growth',
    label: 'Nuôi Tinh Thể Hàn',
    time: 30,
    inputs: [{ resource: 'crystal_chill', qty: 4 }, { resource: 'liquid_glacier', qty: 2 }],
    outputs: [{ resource: 'crystal_echo', qty: 2 }],
    buildingCategories: ['research','arcane'],
    tier: 3,
    description: 'Tăng trưởng tinh thể cộng hưởng.',
    flags: ['crystal']
  },
  {
    id: 'bio_enzyme_synthesis',
    label: 'Tổng Hợp Enzyme',
    time: 18,
    inputs: [{ resource: 'fungus_ice', qty: 8 }, { resource: 'liquid_brine', qty: 4 }],
    outputs: [{ resource: 'r_bio_enzyme', qty: 4 }],
    buildingCategories: ['bio'],
    tier: 2,
    description: 'Tạo enzyme sinh học.',
    flags: ['bio']
  },
  {
    id: 'portal_stabilizer_matrix',
    label: 'Ma Trận Ổn Định Cổng',
    time: 40,
    inputs: [{ resource: 'r_portal_membrane', qty: 4 }, { resource: 'r_portal_node', qty: 2 }, { resource: 'essence_frost', qty: 2 }],
    outputs: [{ resource: 'r_portal_brace', qty: 1 }],
    buildingCategories: ['portal','void'],
    tier: 4,
    description: 'Gia cường ổn định cổng dịch chuyển.',
    flags: ['portal']
  },
  {
    id: 'weather_matrix_assembly',
    label: 'Lắp Ma Trận Thời Tiết',
    time: 34,
    inputs: [{ resource: 'r_weather_core', qty: 3 }, { resource: 'r_weather_shard', qty: 6 }],
    outputs: [{ resource: 'r_weather_matrix', qty: 1 }],
    buildingCategories: ['weather'],
    tier: 4,
    description: 'Tăng cường kiểm soát khí hậu.',
    flags: ['weather']
  },
  {
    id: 'psy_conduit_fabrication',
    label: 'Chế Tạo Ống Dẫn Tâm',
    time: 42,
    inputs: [{ resource: 'crystal_psy', qty: 2 }, { resource: 'r_psy_catalyst', qty: 2 }],
    outputs: [{ resource: 'r_psy_conduit', qty: 1 }],
    buildingCategories: ['psy','sanity'],
    tier: 4,
    description: 'Vật liệu khuếch đại tâm lực.',
    flags: ['psy']
  },
  {
    id: 'apex_core_housing',
    label: 'Tổng Hợp Lõi Đỉnh',
    time: 60,
    inputs: [{ resource: 'r_energy_field', qty: 2 }, { resource: 'r_void_resin', qty: 2 }, { resource: 'core_stasis', qty: 1 }],
    outputs: [{ resource: 'r_apex_core', qty: 1 }],
    buildingIds: ['final_forge','apex_lab'],
    tier: 6,
    description: 'Chế tạo lõi tối thượng cho kết cấu đỉnh.',
    flags: ['apex','legend'],
    basePower: 2
  }
];