using UnityEngine;
using FrostbornRealms.Core;
using FrostbornRealms.Data;
using FrostbornRealms.Assets;
using FrostbornRealms.Visual;
using FrostbornRealms.Audio;

namespace FrostbornRealms {
    public class GameBootstrap : MonoBehaviour {
        [SerializeField] int seed = 12345;
        [SerializeField] SimulationConfig config;
        [Header("Assets")] [SerializeField] AssetManifest assetManifest;
        private float _eventTimer;

        private void Awake(){
            if(config == null){ config = ScriptableObject.CreateInstance<SimulationConfig>(); }
            ServiceLocator.Register(new TimeService());
            ServiceLocator.Register(new RandomService(seed));
            ServiceLocator.Register(config);
            RegistryBootstrap.LoadAll("Mods");

            // Initialize asset layer if manifest provided
            if(assetManifest != null){
                AssetResolver.Initialize(assetManifest);
                MaterialLibrary.Initialize();
                AudioManager.Instance.PlayAmbient("sfx_wind_loop");
            }

            Debug.Log($"Frostborn Realms bootstrap complete. Items={{ItemRegistry.All.Count}} Events={{EventRegistry.All.Count}});
        }
        private void Update(){ ServiceLocator.Get<TimeService>().Tick(Time.deltaTime); _eventTimer += Time.deltaTime; }
    }
}