import { EntityManager } from '../core/ecs/EntityManager';
import { World } from '../world/World';

export interface BlackboardMetrics {
  population: number;
  housingCapacity: number;
  storageCapacity: number;
  storageUsed: number;
  foodDays: number;
  rareStock: number;
  avgTemp: number;
  threatIndex: number;
}

export function computeMetrics(em: EntityManager, world: World): BlackboardMetrics {
  const population = em.role.size;
  const housingCapacity = world.housingCapacity;
  let foodQty = world.resourceStock['food_frozen'] || 0;
  const dailyNeed = population * 2;
  const foodDays = dailyNeed > 0 ? foodQty / dailyNeed : 0;
  return {
    population,
    housingCapacity,
    storageCapacity: world.storageCapacity,
    storageUsed: world.storageUsed,
    foodDays,
    rareStock: world.rareStock,
    avgTemp: world.avgTemp,
    threatIndex: world.threatIndex
  };
}