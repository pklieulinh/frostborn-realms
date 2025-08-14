using UnityEngine;
using FrostbornRealms.Core;
using FrostbornRealms.Data;

namespace FrostbornRealms {
    public class GameBootstrap : MonoBehaviour {
        [SerializeField] int seed = 12345;
        [SerializeField] SimulationConfig config;
        private float _eventTimer;

        private void Awake(){
            if(config == null){
                config = ScriptableObject.CreateInstance<SimulationConfig>();
            }
            ServiceLocator.Register(new TimeService());
            ServiceLocator.Register(new RandomService(seed));
            ServiceLocator.Register(config);
            RegistryBootstrap.LoadAll("Mods");
            Debug.Log($"Frostborn Realms bootstrap complete. Items={ItemRegistry.All.Count} Events={EventRegistry.All.Count}");
        }
        private void Update(){
            ServiceLocator.Get<TimeService>().Tick(Time.deltaTime);
            _eventTimer += Time.deltaTime;
            // (Optional future) could drive manual world tick pacing here.
        }
    }
}