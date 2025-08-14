using Unity.Burst;
using Unity.Entities;
using Unity.Mathematics;
using FrostbornRealms.Core;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct NeedsDecaySystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            var time = ServiceLocator.Get<TimeService>();
            var cfg = ServiceLocator.Get<SimulationConfig>();
            float dt = time.DeltaTime;
            foreach (var needs in SystemAPI.Query<RefRW<Needs>>()) {
                ref var n = ref needs.ValueRW;
                float moraleDecay = cfg.MoraleDecay;
                // Doctrine influence (quick check)
                foreach (var doctrine in SystemAPI.Query<RefRO<DoctrineState>>()) {
                    // If stoicism active -> reduce morale decay
                    // (Soft placeholder: doctrine id 1 reserved for stoicism)
                    if (doctrine.ValueRO.ActiveDoctrineA == 1 || doctrine.ValueRO.ActiveDoctrineB == 1) {
                        moraleDecay *= cfg.StoicismMoraleDecayMultiplier;
                    }
                }
                n.Hunger = math.max(0, n.Hunger - cfg.HungerDecay * dt);
                n.Warmth = math.max(0, n.Warmth - cfg.WarmthDecay * dt);
                n.Morale = math.max(0, n.Morale - moraleDecay * dt);
                n.Fatigue = math.min(100, n.Fatigue + cfg.FatigueGain * dt);
            }
        }
    }
}