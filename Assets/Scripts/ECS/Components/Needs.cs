using Unity.Entities;

namespace FrostbornRealms.ECS.Components {
    public struct Needs : IComponentData {
        public float Hunger;
        public float Warmth;
        public float Morale;
        public float Fatigue;
    }
}