export interface ResourceDef {
  id: string;
  title: string;
  rarity: 'common' | 'uncommon' | 'rare';
  stack: number;
  baseValue: number;
  tags: string[];
  description: string;
}
export const RESOURCE_DEFS: ResourceDef[] = [
  {
    id: 'wood_frost',
    title: 'Gỗ Lạnh',
    rarity: 'common',
    stack: 200,
    baseValue: 1,
    tags: ['material', 'fuel'],
    description: 'Gỗ thu từ cây đóng băng, dùng xây dựng căn bản.'
  },
  {
    id: 'ore_ice',
    title: 'Quặng Băng',
    rarity: 'common',
    stack: 150,
    baseValue: 2,
    tags: ['material'],
    description: 'Quặng lạnh chứa khoáng chất hiếm ở mức cơ bản.'
  },
  {
    id: 'food_frozen',
    title: 'Thực Phẩm Đông',
    rarity: 'common',
    stack: 300,
    baseValue: 1,
    tags: ['food'],
    description: 'Nguồn dinh dưỡng chính, dễ hỏng nếu nhiệt độ tăng.'
  },
  {
    id: 'crystal_chill',
    title: 'Tinh Thể Hàn',
    rarity: 'uncommon',
    stack: 80,
    baseValue: 6,
    tags: ['rare', 'research'],
    description: 'Tinh thể phát ra năng lượng lạnh, dùng trong nghiên cứu.'
  },
  {
    id: 'core_heat',
    title: 'Nhiệt Lượng',
    rarity: 'uncommon',
    stack: 100,
    baseValue: 5,
    tags: ['energy'],
    description: 'Đơn vị năng lượng nhiệt ổn định duy trì sự sống.'
  },
  {
    id: 'essence_frost',
    title: 'Tinh Hoa Băng',
    rarity: 'rare',
    stack: 30,
    baseValue: 20,
    tags: ['legend', 'portal'],
    description: 'Nguồn năng lượng hiếm từ chiều không gian khác.'
  }
];