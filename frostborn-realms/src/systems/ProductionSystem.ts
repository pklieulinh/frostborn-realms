import { System } from '../core/ecs/Systems';
import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';
import { DataRegistry, BuildingDef, RecipeDef } from '../data/registry';

interface ActiveProduction {
  entity: number;
  recipeId: string;
  progress: number;
  time: number;
}

export class ProductionSystem implements System {
  id = 'productionChains';
  private active = new Map<number, ActiveProduction>();
  private accum = 0;
  constructor(private em: EntityManager, private world: World, private data: DataRegistry,
              private getComposite: () => { automationLevel: number; logisticsModifier: number; morale: number; sanity: number; globalSpeed: number; prodBonus: number }) {}

  update(dt: number): void {
    this.accum += dt;
    if (this.accum < 0.5) return;
    const sliceDt = this.accum;
    this.accum = 0;

    const comp = this.getComposite();
    // Evaluate existing
    for (const [entity, prod] of this.active) {
      const recipe = this.data.map.recipeById[prod.recipeId];
      if (!recipe) { this.active.delete(entity); continue; }
      const speed = this.computeSpeedMultiplier(recipe, comp);
      prod.progress += sliceDt * speed;
      if (prod.progress >= prod.time) {
        // Complete
        for (const out of recipe.outputs) {
          this.world.addResource(out.resource, out.qty);
          this.em.analytics.production[out.resource] = (this.em.analytics.production[out.resource] || 0) + out.qty;
        }
        this.active.delete(entity);
      }
    }

    // Assign new productions
    for (const tile of this.world.tiles) {
      if (!tile.building) continue;
      const entity = tile.building.entity;
      if (this.active.has(entity)) continue;
      const bId = tile.building.id;
      const bDef = this.data.map.buildingById[bId] as BuildingDef | undefined;
      if (!bDef) continue;
      const candidate = this.pickRecipeForBuilding(bId, bDef);
      if (!candidate) continue;
      if (!this.hasInputs(candidate)) continue;
      this.consumeInputs(candidate);
      this.active.set(entity, {
        entity,
        recipeId: candidate.id,
        progress: 0,
        time: candidate.time
      });
      this.em.analytics.activeRecipes[candidate.id] = (this.em.analytics.activeRecipes[candidate.id] || 0) + 1;
    }
  }

  private pickRecipeForBuilding(buildingId: string, def: BuildingDef): RecipeDef | null {
    const list: RecipeDef[] = [];
    // category match
    if (def.category && this.data.map.recipesByCategory[def.category]) {
      list.push(...this.data.map.recipesByCategory[def.category]);
    }
    // id-specific
    const byId = this.data.map.recipesByCategory['id:' + buildingId];
    if (byId) list.push(...byId);
    if (!list.length) return null;
    // Simple heuristic: choose first whose inputs available and tier <= median stage
    for (const r of list) {
      if (this.hasInputs(r)) return r;
    }
    return null;
  }

  private hasInputs(recipe: RecipeDef): boolean {
    for (const i of recipe.inputs) {
      if ((this.world.resourceStock[i.resource] || 0) < i.qty) return false;
    }
    return true;
  }

  private consumeInputs(recipe: RecipeDef) {
    for (const i of recipe.inputs) {
      this.world.consumeResource(i.resource, i.qty);
      this.em.analytics.consumption[i.resource] = (this.em.analytics.consumption[i.resource] || 0) + i.qty;
    }
  }

  private computeSpeedMultiplier(recipe: RecipeDef, c: { automationLevel: number; logisticsModifier: number; morale: number; sanity: number; globalSpeed: number; prodBonus: number }): number {
    const moraleFactor = 0.5 + c.morale / 200;
    const sanityFactor = 0.5 + c.sanity / 200;
    const autoFactor = 1 + c.automationLevel * 0.3;
    const logisticFactor = c.logisticsModifier;
    const global = 1 + c.globalSpeed;
    const prod = 1 + c.prodBonus;
    let recipeTierAdj = 1;
    if (recipe.tier >= 5) recipeTierAdj = 0.9;
    return moraleFactor * sanityFactor * autoFactor * logisticFactor * global * prod * recipeTierAdj;
  }

  getActiveForAnalytics(): number { return this.active.size; }
}