export interface EventDef {
  id: string;
  title: string;
  type: string;
  baseChance: number;
  cooldown: number;
  description: string;
  effects: { [k: string]: any };
}
export const EVENT_DEFS: EventDef[] = [
  {
    id: 'cold_snap',
    title: 'Đợt Lạnh Cực Độ',
    type: 'weather',
    baseChance: 0.04,
    cooldown: 120,
    description: 'Nhiệt độ tụt mạnh, tăng nguy cơ mất máu vì rét.',
    effects: { temperatureDelta: -8, duration: 25 }
  },
  {
    id: 'predator_attack',
    title: 'Thú Dữ Tập Kích',
    type: 'attack',
    baseChance: 0.03,
    cooldown: 150,
    description: 'Đàn sói băng xuất hiện uy hiếp cư dân.',
    effects: { threatLevel: 1, spawn: 'frost_wolf', duration: 20 }
  },
  {
    id: 'resource_shortage',
    title: 'Thiếu Hụt Lương Thực',
    type: 'economic',
    baseChance: 0.035,
    cooldown: 110,
    description: 'Kho thực phẩm xuống thấp tạo áp lực.',
    effects: { target: 'food_frozen', pressure: 1, duration: 30 }
  },
  {
    id: 'portal_surge',
    title: 'Dao Động Cổng',
    type: 'portal',
    baseChance: 0.02,
    cooldown: 200,
    description: 'Năng lượng cổng dao động làm tăng spawn portal.',
    effects: { portalBoost: 2, duration: 40 }
  }
];