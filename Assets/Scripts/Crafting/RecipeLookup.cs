using System.Collections.Generic;
using FrostbornRealms.Data;

namespace FrostbornRealms.Crafting {
    public static class RecipeLookup {
        static Dictionary<int,RecipeDef> _idCache;
        static Dictionary<string,RecipeDef> _keyCache;
        static bool _built;
        public static void Build(){
            if(_built) return;
            _idCache = new();
            _keyCache = new(System.StringComparer.OrdinalIgnoreCase);
            foreach(var r in RecipeRegistry.All){
                _idCache[r.Id]=r; _keyCache[r.Key]=r;
            }
            _built = true;
        }
        public static bool TryGet(int id, out RecipeDef def){
            Build();
            return _idCache.TryGetValue(id, out def);
        }
        public static bool TryGetKey(string key, out RecipeDef def){
            Build();
            return _keyCache.TryGetValue(key, out def);
        }
    }
}