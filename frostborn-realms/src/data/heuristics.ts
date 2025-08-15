export interface HeuristicRule {
  id: string;
  check: (metrics: any) => number;
  rationale: (metrics: any) => string | null;
}
export const HEURISTICS: HeuristicRule[] = [
  {
    id: 'need_housing',
    check: m => m.population / Math.max(1, m.housingCapacity) > 0.85 ? 0.9 : 0,
    rationale: m => m.population / Math.max(1, m.housingCapacity) > 0.85 ? 'Thiếu chỗ ở' : null
  },
  {
    id: 'need_food',
    check: m => m.foodDays < 2 ? 1 : (m.foodDays < 4 ? 0.4 : 0),
    rationale: m => m.foodDays < 2 ? 'Lương thực cạn kiệt' : (m.foodDays < 4 ? 'Dự trữ thấp' : null)
  },
  {
    id: 'need_storage',
    check: m => m.storageUsed / Math.max(1, m.storageCapacity) > 0.8 ? 0.7 : 0,
    rationale: m => m.storageUsed / Math.max(1, m.storageCapacity) > 0.8 ? 'Kho sắp đầy' : null
  },
  {
    id: 'need_heat',
    check: m => m.avgTemp < -15 ? 0.8 : (m.avgTemp < -10 ? 0.4 : 0),
    rationale: m => m.avgTemp < -15 ? 'Quá lạnh' : (m.avgTemp < -10 ? 'Thiếu nhiệt' : null)
  },
  {
    id: 'expedition_push',
    check: m => m.rareStock < 10 && m.threatIndex < 0.3 ? 0.6 : 0,
    rationale: m => (m.rareStock < 10 && m.threatIndex < 0.3) ? 'Cần tài nguyên hiếm' : null
  }
];