using Unity.Burst;
using Unity.Entities;
using UnityEngine;
using FrostbornRealms.Core;
using FrostbornRealms.Data;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.ECS.Systems {
    [BurstCompile]
    public partial struct EventResolutionSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}
        public void OnUpdate(ref SystemState state) {
            var rng = ServiceLocator.Get<RandomService>();

            foreach (var entity in SystemAPI.QueryBuilder().WithAll<EventPendingTag>().Build().ToEntityArray(Unity.Collections.Allocator.Temp)) {
                // Pick random event
                if (EventRegistry.All.Count == 0) {
                    state.EntityManager.DestroyEntity(entity);
                    continue;
                }
                var ev = EventRegistry.All[rng.NextInt(0, EventRegistry.All.Count)];
                if (ev.Choices.Count > 0) {
                    var choice = ev.Choices[0]; // placeholder auto-select
                    ApplyEffects(choice.Effects);
                    Debug.Log($"[Event] {ev.Key} -> auto-choice {choice.Key} applied.");
                } else {
                    Debug.Log($"[Event] {ev.Key} (no choices).");
                }
                state.EntityManager.DestroyEntity(entity);
            }
        }

        private void ApplyEffects(string[] effects) {
            // Placeholder: support simple tokens morale+/- / warmth+/- / hunger+/-
            if (effects == null) return;
            foreach (var eff in effects) {
                // In milestone 3 this will queue into an EffectProcessor.
                if (eff.StartsWith("morale")) {
                    // Implementation would search Entities with Needs and adjust Morale.
                }
            }
        }
    }
}