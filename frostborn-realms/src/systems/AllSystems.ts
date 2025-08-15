import { System } from '../core/ecs/Systems';
import { TimeSystem } from './TimeSystem';
import { TaskAllocationSystem } from './TaskAllocationSystem';
import { AIStrategicSystem } from './AIStrategicSystem';
import { AILocalSystem } from './AILocalSystem';
import { ResourceSystem } from './ResourceSystem';
import { ConstructionSystem } from './ConstructionSystem';
import { ExpeditionSystem } from './ExpeditionSystem';
import { PortalSpawnSystem } from './PortalSpawnSystem';
import { EventSystem } from './EventSystem';
import { PathfindingSystem } from './PathfindingSystem';
import { TemperatureSystem } from './TemperatureSystem';
import { RenderingSystem } from './RenderingSystem';
import { CameraSystem } from './CameraSystem';
import { UISystem } from './UISystem';
import { Application } from 'pixi.js';
import { EntityManager } from '../core/ecs/EntityManager';
import { EventBus } from '../core/events/EventBus';
import { World, registerEMPositionGetter } from '../world/World';
import { DataRegistry } from '../data/registry';
import { MoraleSystem } from './MoraleSystem';
import { CombatSystem } from './CombatSystem';
import { MonsterAISystem } from './MonsterAISystem';
import { TechSystem } from './TechSystem';
import { ExpeditionRealtimeSystem } from './ExpeditionRealtimeSystem';
import { WeatherSystem } from './WeatherSystem';
import { SpectatorSystem } from './SpectatorSystem';
import { ModSystem } from './ModSystem';
import { ProductionSystem } from './ProductionSystem';
import { LogisticsMetricsSystem } from './LogisticsMetricsSystem';
import { AutomationSchedulerSystem } from './AutomationSchedulerSystem';
import { EventWeightSystem } from './EventWeightSystem';
import { AnalyticsSystem } from './AnalyticsSystem';

export interface AllSystems {
  time: TimeSystem;
  taskAlloc: TaskAllocationSystem;
  aiStrategic: AIStrategicSystem;
  aiLocal: AILocalSystem;
  resource: ResourceSystem;
  construction: ConstructionSystem;
  expeditionSystem: ExpeditionSystem;
  portalSystem: PortalSpawnSystem;
  eventSystem: EventSystem;
  pathSystem: PathfindingSystem;
  temperatureSystem: TemperatureSystem;
  morale: MoraleSystem;
  combat: CombatSystem;
  monsterAI: MonsterAISystem;
  tech: TechSystem;
  expRealtime: ExpeditionRealtimeSystem;
  weather: WeatherSystem;
  spectator: SpectatorSystem;
  mod: ModSystem;
  production: ProductionSystem;
  logisticsMetrics: LogisticsMetricsSystem;
  automationScheduler: AutomationSchedulerSystem;
  eventWeight: EventWeightSystem;
  analytics: AnalyticsSystem;
  render: RenderingSystem;
  camera: CameraSystem;
  ui: UISystem;
  order: System[];
  reloadData: (data: DataRegistry) => void;
}

export function createAllSystems(ctx: { app: Application; em: EntityManager; bus: EventBus; world: World; data: DataRegistry }): AllSystems {
  registerEMPositionGetter((id)=>ctx.em.position.get(id));
  const render = new RenderingSystem(ctx.app, ctx.world, ctx.em);
  const expedition = new ExpeditionSystem(ctx.em, ctx.world, ctx.data);
  const spectator = new SpectatorSystem(ctx.em, ctx.world);
  const tech = new TechSystem(ctx.em, ctx.world, ctx.data);
  const aiStrategic = new AIStrategicSystem(ctx.em, ctx.world, ctx.data, null as any);
  const eventWeight = new EventWeightSystem(ctx.em, ctx.world, ctx.data);
  const analytics = new AnalyticsSystem(ctx.em, ctx.world);
  const ui = new UISystem(ctx.world, ctx.em, render, aiStrategic, expedition, tech, spectator, ctx.data);
  (aiStrategic as any).ui = ui;

  const logisticsMetrics = new LogisticsMetricsSystem(ctx.em, ctx.world);
  const production = new ProductionSystem(ctx.em, ctx.world, ctx.data, () => composite());
  const automationScheduler = new AutomationSchedulerSystem(ctx.em, ctx.world, () => ({ automationLevel: composite().automationLevel, logisticsModifier: composite().logisticsModifier }));
  const systems: AllSystems = {
    time: new TimeSystem(),
    taskAlloc: new TaskAllocationSystem(ctx.em, ctx.world),
    aiStrategic,
    aiLocal: new AILocalSystem(ctx.em, ctx.world),
    resource: new ResourceSystem(ctx.world),
    construction: new ConstructionSystem(ctx.em),
    expeditionSystem: expedition,
    portalSystem: new PortalSpawnSystem(ctx.world, ctx.data),
    eventSystem: new EventSystem(ctx.data, ctx.world, ui, eventWeight, ctx.em),
    pathSystem: new PathfindingSystem(),
    temperatureSystem: new TemperatureSystem(ctx.world, ctx.em),
    morale: new MoraleSystem(ctx.em, ctx.world),
    combat: new CombatSystem(ctx.em, ctx.world),
    monsterAI: new MonsterAISystem(ctx.em, ctx.world),
    tech,
    expRealtime: new ExpeditionRealtimeSystem(ctx.em),
    weather: new WeatherSystem(ctx.em, ctx.world),
    spectator,
    mod: new ModSystem(ctx.data),
    production,
    logisticsMetrics,
    automationScheduler,
    eventWeight,
    analytics,
    render,
    camera: new CameraSystem(),
    ui,
    order: [] as System[],
    reloadData: (data: DataRegistry) => {
      ctx.world.setData(data);
      systems.portalSystem = new PortalSpawnSystem(ctx.world, data);
      systems.eventSystem = new EventSystem(data, ctx.world, ui, eventWeight, ctx.em);
      systems.tech.reloadData(data);
      systems.mod.setData(data);
      ui.setData(data);
    }
  };

  systems.order = [
    systems.time,
    systems.eventWeight,
    systems.eventSystem,
    systems.weather,
    systems.portalSystem,
    systems.taskAlloc,
    systems.aiStrategic,
    systems.automationScheduler,
    systems.aiLocal,
    systems.monsterAI,
    systems.morale,
    systems.production,
    systems.tech,
    systems.expRealtime,
    systems.resource,
    systems.construction,
    systems.expeditionSystem,
    systems.combat,
    systems.temperatureSystem,
    systems.pathSystem,
    systems.render,
    systems.spectator,
    systems.analytics,
    systems.ui
  ];

  // Hook task creation for logistics metrics
  ctx.bus.on('taskCreated', ({ task }) => {
    systems.logisticsMetrics.logTask(task.type, task.data);
  });

  function composite() {
    const a = ctx.em.analytics || {};
    const moodVals = Array.from(ctx.em.mood.values());
    let morale = 60, sanity = 60;
    if (moodVals.length) {
      morale = moodVals.reduce((s,m)=>s+m.morale,0)/moodVals.length;
      sanity = moodVals.reduce((s,m)=>s+m.sanity,0)/moodVals.length;
    }
    const automationLevel = computeEffect('automation');
    const globalSpeed = computeEffect('global_speed');
    const prodBonus = computeEffect('prod_speed');
    const logisticsModifier = systems.logisticsMetrics.pathEfficiency;
    const compositeObj = { automationLevel, logisticsModifier, morale, sanity, globalSpeed, prodBonus };
    systems.analytics.setPathEfficiency(logisticsModifier);
    systems.analytics.setAutomation(automationLevel);
    systems.analytics.setLogistics(logisticsModifier);
    return compositeObj;
  }

  function computeEffect(effectKey: string): number {
    // Simplified: aggregate from buildings effects + items not fully implemented (future)
    let sum = 0;
    for (const tile of ctx.world.tiles) {
      if (!tile.building) continue;
      const b = ctx.data.map.buildingById[tile.building.id];
      if (b?.effects && b.effects[effectKey]) sum += b.effects[effectKey];
    }
    return sum;
  }

  return systems;
}