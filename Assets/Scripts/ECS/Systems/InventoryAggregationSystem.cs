using Unity.Burst;
using Unity.Entities;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct InventoryAggregationSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            // Future: aggregate item counts from inventory entities -> global stock report.
        }
    }
}