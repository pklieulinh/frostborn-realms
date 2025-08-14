using Unity.Entities;
using FrostbornRealms.Data;
using System.Collections.Generic;
using UnityEngine;

namespace FrostbornRealms.Inventory {
    public struct GlobalInventoryTag : IComponentData {}
    public struct InventoryItemSlot : IBufferElementData {
        public int ItemId;
        public int Count;
    }

    public struct CategoryAggregate : IComponentData {
        public int Fuel;
        public int Food;
        public int Medicine;
    }

    public static class GlobalInventoryAPI {
        static Entity _entity;
        static EntityManager _em;
        static bool _initialized;
        static Dictionary<int,int> _cache = new();

        public static void Init(Entity entity, EntityManager em){
            _entity = entity;
            _em = em;
            _initialized = true;
            RebuildCache();
        }

        static void RebuildCache(){
            _cache.Clear();
            var buf = _em.GetBuffer<InventoryItemSlot>(_entity);
            for(int i=0;i<buf.Length;i++){
                _cache[buf[i].ItemId] = buf[i].Count;
            }
        }

        static void SyncBuffer(){
            var buf = _em.GetBuffer<InventoryItemSlot>(_entity);
            buf.Clear();
            foreach(var kv in _cache){
                if(kv.Value>0) buf.Add(new InventoryItemSlot{ ItemId = kv.Key, Count = kv.Value});
            }
        }

        public static void Add(int itemId, int count){
            if(!_initialized) return;
            if(!_cache.ContainsKey(itemId)) _cache[itemId] = 0;
            _cache[itemId] += count;
            SyncBuffer();
            UpdateCategory(itemId, count);
        }

        public static bool Remove(int itemId, int count){
            if(!_initialized) return false;
            if(!_cache.TryGetValue(itemId, out var have) || have<count) return false;
            have -= count;
            if(have<=0) _cache.Remove(itemId); else _cache[itemId] = have;
            SyncBuffer();
            UpdateCategory(itemId, -count);
            return true;
        }

        public static int Get(int itemId){
            return _cache.TryGetValue(itemId, out var v) ? v : 0;
        }

        static void UpdateCategory(int itemId, int delta){
            var def = ItemRegistry.All.Find(x=>x.Id==itemId);
            if(def == null) return;
            var catAgg = _em.GetComponentData<CategoryAggregate>(_entity);
            switch(def.Category){
                case "fuel": catAgg.Fuel += delta; break;
                case "food": catAgg.Food += delta; break;
                case "medicine": catAgg.Medicine += delta; break;
            }
            _em.SetComponentData(_entity, catAgg);
        }

        public static void AdjustCategory(int categoryKey, int delta){
            var catAgg = _em.GetComponentData<CategoryAggregate>(_entity);
            if("fuel".GetHashCode() == categoryKey) catAgg.Fuel += delta;
            else if("food".GetHashCode() == categoryKey) catAgg.Food += delta;
            else if("medicine".GetHashCode() == categoryKey) catAgg.Medicine += delta;
            _em.SetComponentData(_entity, catAgg);
        }

        public static Dictionary<int,int> Snapshot() => new Dictionary<int,int>(_cache);

        public static void LoadSnapshot(Dictionary<int,int> snap){
            _cache = snap ?? new Dictionary<int,int>();
            SyncBuffer();
            var catAgg = new CategoryAggregate();
            foreach(var kv in _cache){
                var item = ItemRegistry.All.Find(x=>x.Id==kv.Key);
                if(item==null) continue;
                switch(item.Category){
                    case "fuel": catAgg.Fuel += kv.Value; break;
                    case "food": catAgg.Food += kv.Value; break;
                    case "medicine": catAgg.Medicine += kv.Value; break;
                }
            }
            _em.SetComponentData(_entity, catAgg);
        }
    }
}