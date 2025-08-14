using Unity.Entities;

namespace FrostbornRealms.ECS.Components {
    public struct InventoryRef : IComponentData {
        public Entity InventoryEntity;
    }
}