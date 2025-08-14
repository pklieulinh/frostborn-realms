using Unity.Entities;
using Unity.Mathematics;
using UnityEngine;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.Dev {
    public class DevSpawner : MonoBehaviour {
        [Range(1,200)] public int citizenCount = 10;
        public Vector2 spawnArea = new Vector2(20, 20);
        public Vector2 targetArea = new Vector2(40, 40);
        public float baseSpeed = 3f;

        void Start() {
            var world = World.DefaultGameObjectInjectionWorld;
            var em = world.EntityManager;

            for (int i = 0; i < citizenCount; i++) {
                var e = em.CreateEntity(
                    typeof(Position),
                    typeof(Needs),
                    typeof(Movement),
                    typeof(CitizenTag),
                    typeof(DoctrineState)
                );

                float3 startPos = new float3(
                    UnityEngine.Random.Range(-spawnArea.x * 0.5f, spawnArea.x * 0.5f),
                    0,
                    UnityEngine.Random.Range(-spawnArea.y * 0.5f, spawnArea.y * 0.5f)
                );
                float3 target = new float3(
                    UnityEngine.Random.Range(-targetArea.x * 0.5f, targetArea.x * 0.5f),
                    0,
                    UnityEngine.Random.Range(-targetArea.y * 0.5f, targetArea.y * 0.5f)
                );

                em.SetComponentData(e, new Position { Value = startPos });
                em.SetComponentData(e, new Needs {
                    Hunger = 100,
                    Warmth = 100,
                    Morale = 100,
                    Fatigue = 0
                });
                em.SetComponentData(e, new Movement {
                    Target = target,
                    Speed = baseSpeed + UnityEngine.Random.Range(-0.5f, 1.5f)
                });
                em.SetComponentData(e, new DoctrineState {
                    ActiveDoctrineA = 1, // stoicism (giảm morale decay)
                    ActiveDoctrineB = 0
                });
            }

            Debug.Log($"[DevSpawner] Spawned {citizenCount} citizens.");
        }
    }
}