using System.Collections.Generic;
using System.IO;
using UnityEngine;
using FrostbornRealms.Inventory;
using FrostbornRealms.Doctrine;
using FrostbornRealms.Core;
using FrostbornRealms.ECS.Components;
using Unity.Entities;

namespace FrostbornRealms.SaveLoad {
    public class SaveData {
        public float TimeElapsed;
        public int RNGSeed;
        public Dictionary<int,int> Inventory;
        public Dictionary<int,float> DoctrineProgress;
        public List<CitizenNeeds> Citizens;
        public List<CraftOrderData> CraftOrders;
    }
    public class CitizenNeeds {
        public float Hunger, Warmth, Morale, Fatigue;
    }
    public class CraftOrderData {
        public int RecipeId;
        public float TimeRemaining;
    }

    public static class SaveLoadService {
        static string FilePath => Path.Combine(Application.persistentDataPath, "frostborn_save.json");

        public static void Save(World world){
            var data = new SaveData();
            var time = ServiceLocator.Get<TimeService>();
            data.TimeElapsed = time.Elapsed;
            data.RNGSeed = 0; // future RNG capture
            data.Inventory = GlobalInventoryAPI.Snapshot();
            data.DoctrineProgress = DoctrineProgressAPI.Snapshot();

            data.Citizens = new List<CitizenNeeds>();
            var em = world.EntityManager;
            var needsQuery = em.CreateEntityQuery(typeof(Needs));
            using(var arr = needsQuery.ToComponentDataArray<Needs>(Unity.Collections.Allocator.Temp)){
                foreach(var n in arr){
                    data.Citizens.Add(new CitizenNeeds{ Hunger=n.Hunger, Warmth=n.Warmth, Morale=n.Morale, Fatigue=n.Fatigue });
                }
            }

            data.CraftOrders = new List<CraftOrderData>();
            var craftQuery = em.CreateEntityQuery(typeof(Crafting.CraftOrder));
            using(var arr = craftQuery.ToComponentDataArray<Crafting.CraftOrder>(Unity.Collections.Allocator.Temp)){
                foreach(var co in arr){
                    data.CraftOrders.Add(new CraftOrderData{ RecipeId = co.RecipeId, TimeRemaining = co.TimeRemaining });
                }
            }

            var json = JsonUtility.ToJson(new Wrapper{Data=data}, true);
            File.WriteAllText(FilePath, json);
            Debug.Log($"[SaveLoad] Saved to {FilePath}");
        }

        public static void Load(World world){
            if(!File.Exists(FilePath)){
                Debug.LogWarning("[SaveLoad] No save file.");
                return;
            }
            var json = File.ReadAllText(FilePath);
            var wrap = JsonUtility.FromJson<Wrapper>(json);
            var data = wrap.Data;
            var em = world.EntityManager;

            // Citizens reset
            var needsQuery = em.CreateEntityQuery(typeof(Needs));
            using(var ents = needsQuery.ToEntityArray(Unity.Collections.Allocator.Temp)){
                foreach(var e in ents) em.DestroyEntity(e);
            }
            foreach(var c in data.Citizens){
                var e = em.CreateEntity(typeof(Needs));
                em.SetComponentData(e, new Needs{ Hunger=c.Hunger, Warmth=c.Warmth, Morale=c.Morale, Fatigue=c.Fatigue });
            }

            GlobalInventoryAPI.LoadSnapshot(data.Inventory);
            DoctrineProgressAPI.Load(data.DoctrineProgress);

            // Craft orders
            var craftQuery = em.CreateEntityQuery(typeof(Crafting.CraftOrder));
            using(var ents = craftQuery.ToEntityArray(Unity.Collections.Allocator.Temp)){
                foreach(var e in ents) em.DestroyEntity(e);
            }
            foreach(var co in data.CraftOrders){
                var e = em.CreateEntity(typeof(Crafting.CraftOrder));
                em.SetComponentData(e, new Crafting.CraftOrder{ RecipeId=co.RecipeId, TimeRemaining=co.TimeRemaining });
            }

            Debug.Log("[SaveLoad] Load completed.");
        }

        [System.Serializable]
        class Wrapper { public SaveData Data; }
    }
}