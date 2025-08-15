import { EventBus } from '../events/EventBus';

export type Position = { x: number; y: number };
export type Stats = { hp: number; maxHp: number; fatigue: number; cold: number; attack: number; defense: number };
export type Role = { role: 'Worker' | 'Scout' | 'Guard' | 'Leader' | 'Monster' };
export type AIState = { state: string; taskId: number | null };
export type InventoryItem = { type: string; qty: number };
export type Inventory = { items: InventoryItem[]; capacity: number };
export type LeaderTag = { focus: string; rationale: string[] };
export type Task = {
  id: number;
  type: string;
  status: 'pending' | 'assigned' | 'done' | 'cancelled';
  data: any;
  assignee?: number;
  priority: number;
  created: number;
};
export type Construction = { building: string; progress: number; x: number; y: number };
export type Expedition = {
  id: number;
  members: number[];
  status: 'forming' | 'ongoing' | 'returning' | 'done';
  eta: number;
  result?: any;
  portalSeed: number;
  risk: number;
  rewardHint: string;
  realtime?: any;
};

export type HeatSource = { radius: number; heat: number };
export type Temperature = { local: number };
export type Mood = { morale: number; sanity: number; productivityMod: number; fatigueMod: number; recent: string[] };
export type MonsterTag = { monsterId: string; hostile: boolean; target?: number };
export type TechState = { unlocked: Set<string>; progress: Record<string, number>; active?: string };
export type WeatherField = { storms: { id: number; type: string; x: number; y: number; vx: number; vy: number; strength: number }[] };

export class EntityManager {
  private nextId = 1;
  position = new Map<number, Position>();
  stats = new Map<number, Stats>();
  role = new Map<number, Role>();
  aiState = new Map<number, AIState>();
  inventory = new Map<number, Inventory>();
  leaderTag = new Map<number, LeaderTag>();
  construction = new Map<number, Construction>();
  heatSource = new Map<number, HeatSource>();
  temperature = new Map<number, Temperature>();
  mood = new Map<number, Mood>();
  monster = new Map<number, MonsterTag>();

  tasks: Task[] = [];
  private taskSeq = 1;
  expeditions: Expedition[] = [];
  private expeditionSeq = 1;
  tech: TechState = { unlocked: new Set(['root']), progress: {}, active: undefined };
  weather: WeatherField = { storms: [] };

  constructor(private bus: EventBus) {}

  createEntity(): number {
    const id = this.nextId++;
    this.bus.emit('entityCreated', { id });
    return id;
  }

  removeEntity(id: number) {
    this.position.delete(id);
    this.stats.delete(id);
    this.role.delete(id);
    this.aiState.delete(id);
    this.inventory.delete(id);
    this.leaderTag.delete(id);
    this.construction.delete(id);
    this.heatSource.delete(id);
    this.temperature.delete(id);
    this.mood.delete(id);
    this.monster.delete(id);
    this.bus.emit('entityRemoved', { id });
  }

  createTask(type: string, data: any, priority: number) {
    const task: Task = {
      id: this.taskSeq++,
      type,
      status: 'pending',
      data,
      priority,
      created: performance.now()
    };
    this.tasks.push(task);
    this.bus.emit('taskCreated', { task });
    return task;
  }

  fetchPendingTasks(filter?: (t: Task) => boolean): Task[] {
    return this.tasks.filter(t => t.status === 'pending' && (!filter || filter(t)));
  }

  getTask(id: number) {
    return this.tasks.find(t => t.id === id);
  }

  createExpedition(members: number[], portalSeed: number, risk: number, rewardHint: string, durationSec: number) {
    const exp: Expedition = {
      id: this.expeditionSeq++,
      members,
      status: 'ongoing',
      eta: performance.now() + durationSec * 1000,
      portalSeed,
      risk,
      rewardHint,
      realtime: null
    };
    this.expeditions.push(exp);
    this.bus.emit('expeditionStarted', { expedition: exp });
    return exp;
  }

  serialize() {
    return {
      nextId: this.nextId,
      position: Array.from(this.position.entries()),
      stats: Array.from(this.stats.entries()),
      role: Array.from(this.role.entries()),
      aiState: Array.from(this.aiState.entries()),
      inventory: Array.from(this.inventory.entries()),
      leaderTag: Array.from(this.leaderTag.entries()),
      construction: Array.from(this.construction.entries()),
      heatSource: Array.from(this.heatSource.entries()),
      temperature: Array.from(this.temperature.entries()),
      mood: Array.from(this.mood.entries()),
      monster: Array.from(this.monster.entries()),
      tasks: this.tasks,
      taskSeq: this.taskSeq,
      expeditions: this.expeditions,
      expeditionSeq: this.expeditionSeq,
      tech: {
        unlocked: Array.from(this.tech.unlocked),
        progress: this.tech.progress,
        active: this.tech.active
      },
      weather: this.weather
    };
  }

  deserialize(json: any) {
    this.nextId = json.nextId;
    const restoreMap = <T>(map: Map<number, T>, arr: [number, T][]) => {
      map.clear();
      for (const [k, v] of arr) map.set(k, v);
    };
    restoreMap(this.position, json.position);
    restoreMap(this.stats, json.stats);
    restoreMap(this.role, json.role);
    restoreMap(this.aiState, json.aiState);
    restoreMap(this.inventory, json.inventory);
    restoreMap(this.leaderTag, json.leaderTag);
    restoreMap(this.construction, json.construction);
    restoreMap(this.heatSource, json.heatSource);
    restoreMap(this.temperature, json.temperature);
    restoreMap(this.mood, json.mood);
    restoreMap(this.monster, json.monster);
    this.tasks = json.tasks;
    this.taskSeq = json.taskSeq;
    this.expeditions = json.expeditions;
    this.expeditionSeq = json.expeditionSeq;
    this.tech.unlocked = new Set(json.tech.unlocked);
    this.tech.progress = json.tech.progress;
    this.tech.active = json.tech.active;
    this.weather = json.weather;
  }
}