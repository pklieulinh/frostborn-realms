using Unity.Burst;
using Unity.Entities;
using Unity.Mathematics;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct MovementSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            var dt = SystemAPI.Time.DeltaTime;
            foreach (var (pos, mov) in SystemAPI.Query<RefRW<Position>, RefRW<Movement>>()) {
                var dir = mov.ValueRO.Target - pos.ValueRO.Value;
                float dist = math.length(dir);
                if (dist > 0.01f) {
                    var step = math.min(dist, mov.ValueRO.Speed * dt);
                    pos.ValueRW.Value += math.normalize(dir) * step;
                }
            }
        }
    }
}