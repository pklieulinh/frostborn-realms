using Unity.Burst;
using Unity.Entities;
using UnityEngine;
using FrostbornRealms.Core;
using FrostbornRealms.Data;
using FrostbornRealms.Effects;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct EventResolutionSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}

        public void OnUpdate(ref SystemState state) {
            var rng = ServiceLocator.Get<RandomService>();
            Entity effectQueue = SystemAPI.GetSingletonEntity<EffectQueueTag>();
            var effectBuffer = state.EntityManager.GetBuffer<EffectToken>(effectQueue);

            // Query entities tagged EventPendingTag (assumed defined elsewhere)
            var query = SystemAPI.QueryBuilder().WithAll<EventPendingTag>().Build();
            var entities = query.ToEntityArray(Unity.Collections.Allocator.Temp);
            if(entities.Length == 0) return;

            foreach (var entity in entities) {
                if (EventRegistry.All.Count == 0) {
                    state.EntityManager.DestroyEntity(entity);
                    continue;
                }
                var ev = EventRegistry.All[rng.NextInt(0, EventRegistry.All.Count)];
                if (ev.Choices.Count > 0) {
                    var choice = ev.Choices[0]; // placeholder auto-pick
                    foreach(var eff in choice.Effects){
                        effectBuffer.Add(new EffectToken{ Value = eff });
                    }
                    Debug.Log($"[Event] {ev.Key} -> {choice.Key} queued {choice.Effects.Count} effects.");
                } else {
                    Debug.Log($"[Event] {ev.Key} (no choices).");
                }
                state.EntityManager.DestroyEntity(entity);
            }
        }
    }
}