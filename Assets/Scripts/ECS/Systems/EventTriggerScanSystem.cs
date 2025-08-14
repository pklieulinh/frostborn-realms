using Unity.Burst;
using Unity.Entities;
using FrostbornRealms.Core;
using FrostbornRealms.Data;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct EventTriggerScanSystem : ISystem {
        private float _accum;
        public void OnCreate(ref SystemState state) {
            _accum = 0f;
        }
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            var cfg = ServiceLocator.Get<SimulationConfig>();
            var time = ServiceLocator.Get<TimeService>();
            var rng  = ServiceLocator.Get<RandomService>();
            _accum += time.DeltaTime;
            if (_accum < cfg.EventCheckInterval) return;
            _accum = 0f;

            if (EventRegistry.All.Count == 0) return;
            if (!rng.Chance(cfg.EventProbability)) return;

            // Spawn a "global event entity" with EventPendingTag.
            var e = state.EntityManager.CreateEntity();
            state.EntityManager.AddComponent<EventPendingTag>(e);
        }
    }
}