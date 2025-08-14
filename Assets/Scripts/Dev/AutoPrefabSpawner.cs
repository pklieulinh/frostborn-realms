using UnityEngine;
using FrostbornRealms.Assets;
using FrostbornRealms.Utility;
using FrostbornRealms.Visual;

namespace FrostbornRealms.Dev {
    public class AutoPrefabSpawner : MonoBehaviour {
        [System.Serializable] public struct SpawnRequest { public string PrefabKey; public Vector3 Position; public MaterialKey PlaceholderMaterial; public PrimitiveType PlaceholderShape; }
        public SpawnRequest[] Objects;
        void Start() {
            foreach (var r in Objects) {
                var prefab = AssetResolver.Prefab(r.PrefabKey);
                GameObject inst;
                if (prefab) { inst = GameObject.Instantiate(prefab, r.Position, Quaternion.identity); }
                else { inst = ProceduralPrimitiveFactory.CreatePlaceholder(r.PrefabKey, r.PlaceholderMaterial, r.PlaceholderShape); inst.transform.position = r.Position; }
            }
        }
    }
}