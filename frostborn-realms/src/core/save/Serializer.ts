import { World } from '../../world/World';
import { EntityManager } from '../ecs/EntityManager';
import { AllSystems } from '../../systems/AllSystems';

export class Serializer {
  static save(world: World, em: EntityManager, systems: AllSystems) {
    return {
      version: 2,
      world: world.serialize(),
      entities: em.serialize(),
      systems: {
        events: systems.eventSystem.serialize(),
        portal: systems.portalSystem.serialize(),
        expedition: systems.expeditionSystem.serialize(),
        temperature: systems.temperatureSystem.serialize(),
        analytics: {
          expedition: {
            total: systems.analytics.expeditionTotal,
            success: systems.analytics.expeditionSuccess
          }
        }
      }
    };
  }
  static load(json: any, world: World, em: EntityManager, systems: AllSystems) {
    if (json.version < 1 || json.version > 2) throw new Error('Unsupported save version');
    world.deserialize(json.world);
    em.deserialize(json.entities);
    systems.eventSystem.deserialize(json.systems.events);
    systems.portalSystem.deserialize(json.systems.portal);
    systems.expeditionSystem.deserialize(json.systems.expedition);
    systems.temperatureSystem.deserialize(json.systems.temperature);
    if (json.systems.analytics) {
      systems.analytics.expeditionTotal = json.systems.analytics.expedition.expedition.total || 0;
      systems.analytics.expeditionSuccess = json.systems.analytics.expedition.expedition.success || 0;
    }
    systems.ui.pushEventFeed('Tải dữ liệu hệ thống');
  }
}