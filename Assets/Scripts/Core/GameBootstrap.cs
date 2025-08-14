using UnityEngine;
using FrostbornRealms.Core;
using FrostbornRealms.Data;
using FrostbornRealms.Assets;
using FrostbornRealms.Visual;
using FrostbornRealms.Audio;
using Unity.Entities;
using FrostbornRealms.Inventory;
using FrostbornRealms.Effects;
using FrostbornRealms.Doctrine;

namespace FrostbornRealms {
    public class GameBootstrap : MonoBehaviour {
        [SerializeField] int seed = 12345;
        [SerializeField] SimulationConfig config;
        [Header("Assets")] [SerializeField] AssetManifest assetManifest;
        [Header("Dev")] public bool AutoSpawnHeatSource = true;

        private void Awake(){
            if(config == null){ config = ScriptableObject.CreateInstance<SimulationConfig>(); }
            ServiceLocator.Register(new TimeService());
            ServiceLocator.Register(new RandomService(seed));
            ServiceLocator.Register(config);

            RegistryBootstrap.LoadAll("Mods");

            if(assetManifest != null){
                AssetResolver.Initialize(assetManifest);
                MaterialLibrary.Initialize();
                AudioManager.Instance.PlayAmbient("sfx_wind_loop");
            }

            var world = World.DefaultGameObjectInjectionWorld;
            var em = world.EntityManager;

            // Global Inventory singleton
            var inventoryEntity = em.CreateEntity(typeof(GlobalInventoryTag));
            em.AddBuffer<InventoryItemSlot>(inventoryEntity);
            em.AddComponentData(inventoryEntity, new CategoryAggregate());
            GlobalInventoryAPI.Init(inventoryEntity, em);

            // Effect queue singleton
            var effectEntity = em.CreateEntity(typeof(EffectQueueTag));
            em.AddBuffer<EffectToken>(effectEntity);
            em.AddBuffer<EffectActionBuffer>(effectEntity);

            // Doctrine progress singleton
            var doctrineEntity = em.CreateEntity(typeof(DoctrineProgressTag));
            em.AddBuffer<DoctrineProgressEntry>(doctrineEntity);
            DoctrineProgressAPI.Init(doctrineEntity, em);

            // Heat source demo
            if(AutoSpawnHeatSource){
                var heatSource = em.CreateEntity(
                    typeof(ECS.Components.Position),
                    typeof(Heat.HeatSource),
                    typeof(Heat.Temperature));
                em.SetComponentData(heatSource, new ECS.Components.Position{ Value = new Unity.Mathematics.float3(0,0,0)});
                em.SetComponentData(heatSource, new Heat.HeatSource{ Intensity = 80f, Radius = 25f});
                em.SetComponentData(heatSource, new Heat.Temperature{ Value = config.AmbientTemperature + 40f});
            }

            // Debug HUD
            if(FindObjectOfType<UI.DebugHUD>() == null){
                var hud = new GameObject("DebugHUD");
                hud.AddComponent<UI.DebugHUD>();
            }

            Debug.Log($"Frostborn Realms bootstrap complete. Items={ItemRegistry.All.Count} Events={EventRegistry.All.Count}");
        }

        private void Update(){
            ServiceLocator.Get<TimeService>().Tick(Time.deltaTime);
        }
    }
}