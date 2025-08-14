using System;
using System.Collections.Generic;
using UnityEngine;

namespace FrostbornRealms.Assets {
    [CreateAssetMenu(fileName = "AssetManifest", menuName = "Frostborn/AssetManifest")]
    public class AssetManifest : ScriptableObject {
        [Serializable] public struct PrefabEntry { public string Key; public GameObject Prefab; }
        [Serializable] public struct AudioEntry { public string Key; public AudioClip Clip; public float DefaultVolume; }
        [Serializable] public struct MaterialEntry { public string Key; public Material Material; }
        [Serializable] public struct SpriteEntry { public string Key; public Sprite Sprite; }
        public PrefabEntry[] Prefabs;
        public AudioEntry[] Audio;
        public MaterialEntry[] Materials;
        public SpriteEntry[] Sprites;
    }
    public static class AssetResolver {
        static Dictionary<string, GameObject> _prefabs;
        static Dictionary<string, AudioClip> _audio;
        static Dictionary<string, Material> _materials;
        static Dictionary<string, Sprite> _sprites;
        public static void Initialize(AssetManifest manifest) {
            _prefabs = new(); _audio = new(); _materials = new(); _sprites = new();
            foreach (var p in manifest.Prefabs) if(!string.IsNullOrWhiteSpace(p.Key) && p.Prefab) _prefabs[p.Key] = p.Prefab;
            foreach (var a in manifest.Audio) if(!string.IsNullOrWhiteSpace(a.Key) && a.Clip) _audio[a.Key] = a.Clip;
            foreach (var m in manifest.Materials) if(!string.IsNullOrWhiteSpace(m.Key) && m.Material) _materials[m.Key] = m.Material;
            foreach (var s in manifest.Sprites) if(!string.IsNullOrWhiteSpace(s.Key) && s.Sprite) _sprites[s.Key] = s.Sprite;
        }
        public static GameObject Prefab(string key) => _prefabs != null && _prefabs.TryGetValue(key, out var go) ? go : null;
        public static AudioClip Audio(string key) => _audio != null && _audio.TryGetValue(key, out var ac) ? ac : null;
        public static Material Material(string key) => _materials != null && _materials.TryGetValue(key, out var mat) ? mat : null;
        public static Sprite Sprite(string key) => _sprites != null && _sprites.TryGetValue(key, out var sp) ? sp : null;
    }
}