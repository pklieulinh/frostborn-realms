export interface BuildingDef {
  id: string;
  title: string;
  category: string;
  cost: { resource: string; qty: number }[];
  buildTime: number;
  provides?: { housing?: number; storage?: number; heat?: number };
  unlock?: string[];
  aiWeight: { housing?: number; heat?: number; storage?: number; research?: number };
  description: string;
}
export const BUILDING_DEFS: BuildingDef[] = [
  {
    id: 'hub_core',
    title: 'Lõi Lãnh Địa',
    category: 'core',
    cost: [],
    buildTime: 0,
    provides: { storage: 100, heat: 5 },
    aiWeight: { storage: 1, heat: 0.5 },
    description: 'Trung tâm đầu tiên của lãnh địa, cung cấp nhiệt và lưu trữ ban đầu.'
  },
  {
    id: 'tent',
    title: 'Lều Trú',
    category: 'housing',
    cost: [{ resource: 'wood_frost', qty: 25 }],
    buildTime: 10,
    provides: { housing: 3 },
    aiWeight: { housing: 1 },
    description: 'Chỗ ở cơ bản cho cư dân.'
  },
  {
    id: 'storehouse',
    title: 'Kho Lạnh',
    category: 'storage',
    cost: [{ resource: 'wood_frost', qty: 35 }, { resource: 'ore_ice', qty: 10 }],
    buildTime: 16,
    provides: { storage: 150 },
    aiWeight: { storage: 1 },
    description: 'Kho bảo quản tài nguyên chống tan chảy.'
  },
  {
    id: 'forge_cold',
    title: 'Xưởng Luyện Hàn',
    category: 'production',
    cost: [{ resource: 'ore_ice', qty: 30 }, { resource: 'wood_frost', qty: 20 }],
    buildTime: 22,
    provides: {},
    aiWeight: { research: 0.2 },
    description: 'Xử lý quặng băng và tinh thể thành vật phẩm nâng cao.'
  },
  {
    id: 'research_node',
    title: 'Trạm Nghiên Cứu',
    category: 'research',
    cost: [{ resource: 'crystal_chill', qty: 8 }, { resource: 'wood_frost', qty: 20 }],
    buildTime: 30,
    aiWeight: { research: 1 },
    description: 'Mở đường công nghệ và phân tích portal loot.'
  },
  {
    id: 'heat_tower',
    title: 'Tháp Nhiệt',
    category: 'utility',
    cost: [{ resource: 'core_heat', qty: 5 }, { resource: 'ore_ice', qty: 25 }],
    buildTime: 28,
    provides: { heat: 15 },
    aiWeight: { heat: 1 },
    description: 'Phát tán nhiệt lượng giữ vùng an toàn.'
  },
  {
    id: 'portal_frame',
    title: 'Khung Cổng',
    category: 'portal',
    cost: [{ resource: 'crystal_chill', qty: 12 }, { resource: 'essence_frost', qty: 2 }],
    buildTime: 40,
    aiWeight: { research: 0.5 },
    description: 'Cấu trúc để ổn định cổng dịch chuyển.'
  }
];