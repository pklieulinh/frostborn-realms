using Unity.Entities;

namespace FrostbornRealms.Crafting {
    public struct CraftOrder : IComponentData {
        public int RecipeId;
        public float TimeRemaining;
    }

    public struct CraftingQueueTag : IComponentData {}
}