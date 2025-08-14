using Unity.Entities;

namespace FrostbornRealms.ECS.Components {
    public struct DoctrineState : IComponentData {
        public int ActiveDoctrineA;
        public int ActiveDoctrineB;
    }
}