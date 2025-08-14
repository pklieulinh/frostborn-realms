using Unity.Entities;

namespace FrostbornRealms.Heat {
    public struct HeatSource : IComponentData {
        public float Intensity;
        public float Radius;
    }

    public struct Temperature : IComponentData {
        public float Value;
    }
}