using Unity.Entities;
using Unity.Mathematics;

namespace FrostbornRealms.ECS.Components {
    public struct Movement : IComponentData {
        public float3 Target;
        public float Speed;
    }
}