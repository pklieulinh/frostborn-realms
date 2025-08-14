using System.Collections.Generic;
using UnityEngine;
using FrostbornRealms.Assets;

namespace FrostbornRealms.Visual {
    public enum MaterialKey { Ice, Rock, Wood, HeatSource, CreatureTier1, CreatureTier2, CreatureTier3, CreatureTier4, Fallback }
    public static class MaterialLibrary {
        static Dictionary<MaterialKey, Material> _cache = new(); static bool _initialized;
        public static void Initialize() { if (_initialized) return; Load(MaterialKey.Ice, "mat_ice", Color.cyan*0.7f); Load(MaterialKey.Rock, "mat_rock", Color.gray); Load(MaterialKey.Wood, "mat_wood", new Color(0.35f,0.2f,0.1f)); Load(MaterialKey.HeatSource, "mat_heat", new Color(1f,0.4f,0.1f)); Load(MaterialKey.CreatureTier1, "mat_creature_t1", new Color(0.6f,1f,0.6f)); Load(MaterialKey.CreatureTier2, "mat_creature_t2", new Color(0.6f,0.8f,1f)); Load(MaterialKey.CreatureTier3, "mat_creature_t3", new Color(1f,0.8f,0.5f)); Load(MaterialKey.CreatureTier4, "mat_creature_t4", new Color(1f,0.4f,0.4f)); Load(MaterialKey.Fallback, "mat_fallback", Color.magenta); _initialized = true; }
        static void Load(MaterialKey key, string assetKey, Color fallbackColor) { var mat = AssetResolver.Material(assetKey); if (!mat) { mat = new Material(Shader.Find("Standard")) { color = fallbackColor }; mat.EnableKeyword("_EMISSION"); } _cache[key] = mat; }
        public static Material Get(MaterialKey key) { if(!_initialized) Initialize(); return _cache.TryGetValue(key, out var m) ? m : _cache[MaterialKey.Fallback]; }
    }
}