import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

interface EMA {
  value: number;
  alpha: number;
}

export class AnalyticsSystem implements System {
  id = 'analytics';
  alpha = 0.2;
  lastExpeditionSuccess = 0;
  expeditionTotal = 0;
  expeditionSuccess = 0;
  accum = 0;
  constructor(private em: EntityManager, private world: World) {
    if (!this.em.analytics) {
      (this.em as any).analytics = {
        production: {},
        consumption: {},
        eventsCount: {},
        activeRecipes: {},
        ema: {} as Record<string, EMA>,
        pathEfficiency: 1,
        morale: 0,
        sanity: 0,
        automation: 0,
        logistics: 1
      };
    }
  }

  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 2) return;
    this.accum = 0;
    const a = this.em.analytics;
    // Update morale/sanity
    let sumMor = 0; let sumSan = 0; let n = 0;
    for (const m of this.em.mood.values()) { sumMor += m.morale; sumSan += m.sanity; n++; }
    a.morale = n ? sumMor / n : 0;
    a.sanity = n ? sumSan / n : 0;
    // Smooth production & consumption to r/min
    const keys = new Set([...Object.keys(a.production), ...Object.keys(a.consumption)]);
    for (const k of keys) {
      const prod = (a.production[k] || 0);
      const cons = (a.consumption[k] || 0);
      this.updateEMA('prod:' + k, prod);
      this.updateEMA('cons:' + k, cons);
      a.production[k] = 0;
      a.consumption[k] = 0;
    }
  }

  recordEvent(id: string) {
    this.em.analytics.eventsCount[id] = (this.em.analytics.eventsCount[id] || 0) + 1;
  }

  expeditionResult(success: boolean) {
    this.expeditionTotal++;
    if (success) this.expeditionSuccess++;
    this.lastExpeditionSuccess = this.expeditionSuccess / Math.max(1, this.expeditionTotal);
    this.em.analytics.expeditionSuccess = this.lastExpeditionSuccess;
  }

  setPathEfficiency(v: number) { this.em.analytics.pathEfficiency = v; }
  setAutomation(v: number) { this.em.analytics.automation = v; }
  setLogistics(v: number) { this.em.analytics.logistics = v; }

  private updateEMA(key: string, deltaQty: number) {
    const a = this.em.analytics;
    if (!a.ema[key]) a.ema[key] = { value: 0, alpha: this.alpha };
    const perMin = deltaQty / (2 / 60); // since sample every 2s approximate => scale
    a.ema[key].value = a.ema[key].value * (1 - this.alpha) + perMin * this.alpha;
  }
}