using Unity.Entities;
using FrostbornRealms.Crafting;
using FrostbornRealms.Inventory;
using FrostbornRealms.Data;
using FrostbornRealms.Core;

namespace FrostbornRealms.ECS.Systems {
    public partial struct CraftingSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}

        public void OnUpdate(ref SystemState state) {
            var cfg = ServiceLocator.Get<SimulationConfig>();
            int active = 0;

            foreach(var (order, entity) in SystemAPI.Query<RefRW<CraftOrder>>().WithEntityAccess()){
                active++;
                if(!RecipeLookup.TryGet(order.ValueRO.RecipeId, out var def)){
                    state.EntityManager.DestroyEntity(entity);
                    continue;
                }
                var o = order.ValueRO;
                o.TimeRemaining -= SystemAPI.Time.DeltaTime;
                if(o.TimeRemaining <=0){
                    foreach(var output in def.Outputs){
                        var it = ItemRegistry.All.Find(x=>x.Name == output.Item);
                        if(it!=null) GlobalInventoryAPI.Add(it.Id, output.Count);
                    }
                    state.EntityManager.DestroyEntity(entity);
                } else {
                    order.ValueRW = o;
                }
            }

            if(active >= cfg.MaxParallelCrafts) return;
            // Future: pull new CraftOrders from a queue
        }
    }
}