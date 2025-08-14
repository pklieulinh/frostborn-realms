using Unity.Burst;
using Unity.Entities;
using Unity.Mathematics;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.ECS.Systems {
    // Placeholder system that could later adjust doctrine alignment metrics.
    [BurstCompile]
    public partial struct DoctrineDriftSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            // Future: accumulate drift counters & propose doctrine changes.
        }
    }
}