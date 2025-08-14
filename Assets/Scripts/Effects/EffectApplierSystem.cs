using Unity.Entities;
using FrostbornRealms.Effects;
using FrostbornRealms.ECS.Components;
using FrostbornRealms.Inventory;
using FrostbornRealms.Doctrine;
using Unity.Mathematics;

namespace FrostbornRealms.ECS.Systems {
    // Applies parsed effect actions (currently inline parse from tokens each cycle)
    public partial struct EffectApplierSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}

        public void OnUpdate(ref SystemState state) {
            Entity queue = SystemAPI.GetSingletonEntity<EffectQueueTag>();
            var tokenBuffer = state.EntityManager.GetBuffer<EffectToken>(queue);
            if(tokenBuffer.Length == 0) return;

            var raw = new System.Collections.Generic.List<string>(tokenBuffer.Length);
            for(int i=0;i<tokenBuffer.Length;i++) raw.Add(tokenBuffer[i].Value.ToString());

            var actions = EffectParser.ParseTokens(raw);
            tokenBuffer.Clear();

            foreach(var act in actions){
                switch(act.Op){
                    case EffectOp.AdjustNeed:
                        foreach(var needs in SystemAPI.Query<RefRW<Needs>>()){
                            ref var n = ref needs.ValueRW;
                            switch(act.Need){
                                case NeedType.Morale: n.Morale = math.clamp(n.Morale + act.NeedDelta,0,100); break;
                                case NeedType.Warmth: n.Warmth = math.clamp(n.Warmth + act.NeedDelta,0,100); break;
                                case NeedType.Hunger: n.Hunger = math.clamp(n.Hunger + act.NeedDelta,0,100); break;
                                case NeedType.Fatigue: n.Fatigue = math.clamp(n.Fatigue + act.NeedDelta,0,100); break;
                            }
                        }
                        break;
                    case EffectOp.AddItem:
                        GlobalInventoryAPI.Add(act.ItemId, act.ItemCount);
                        break;
                    case EffectOp.RemoveItem:
                        GlobalInventoryAPI.Remove(act.ItemId, act.ItemCount);
                        break;
                    case EffectOp.AdjustCategory:
                        GlobalInventoryAPI.AdjustCategory(act.CategoryKey, act.ItemCount);
                        break;
                    case EffectOp.DoctrineProgress:
                        DoctrineProgressAPI.AddProgress(act.DoctrineKey, act.DoctrineAmount);
                        break;
                }
            }
        }
    }
}