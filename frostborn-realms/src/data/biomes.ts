export interface SurfaceBiome {
  id: string;
  title: string;
  temperature: number;
  resourceSpawn: { resource: string; density: number }[];
  color: number;
  description: string;
}
export const SURFACE_BIOMES: SurfaceBiome[] = [
  {
    id: 'frozen_plain',
    title: 'Đồng Bằng Băng',
    temperature: -10,
    resourceSpawn: [
      { resource: 'wood_frost', density: 0.4 },
      { resource: 'food_frozen', density: 0.2 },
      { resource: 'ore_ice', density: 0.25 }
    ],
    color: 0x1d2f3a,
    description: 'Khu vực bằng phẳng phủ sương.'
  },
  {
    id: 'shard_field',
    title: 'Cánh Đồng Tinh Mảnh',
    temperature: -12,
    resourceSpawn: [
      { resource: 'crystal_chill', density: 0.12 },
      { resource: 'ore_ice', density: 0.3 }
    ],
    color: 0x24374b,
    description: 'Mặt băng lẫn tinh thể nhô lên.'
  },
  {
    id: 'frost_forest',
    title: 'Rừng Lạnh',
    temperature: -9,
    resourceSpawn: [
      { resource: 'wood_frost', density: 0.7 },
      { resource: 'food_frozen', density: 0.25 }
    ],
    color: 0x264657,
    description: 'Rừng đóng băng cho nguồn gỗ dồi dào.'
  }
];