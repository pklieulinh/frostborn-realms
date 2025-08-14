using Unity.Burst;
using Unity.Entities;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct JobAssignmentSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            // Placeholder: In future, scan idle citizens & assign gather/craft tasks.
        }
    }
}