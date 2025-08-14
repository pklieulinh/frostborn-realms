using Unity.Entities;

namespace FrostbornRealms.ECS.Components {
    public struct ActionRequest : IComponentData {
        public byte Type;
        public float TimeRemaining;
    }
}