using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using System.Text.Json;

namespace FrostbornRealms.Data {
    internal class ItemFile { public List<JsonItem> items {get;set;} }
    internal class JsonItem { public int id; public string name; public string category; public bool perishable; }

    internal class EventFile { public List<JsonEvent> events {get;set;} }
    internal class JsonEvent { public int id; public string key; public string title; public string description; public List<JsonChoice> choices; }
    internal class JsonChoice { public string key; public string description; public List<string> effects; }

    internal class DoctrineFile { public List<JsonDoctrine> doctrines {get;set;} }
    internal class JsonDoctrine { public int id; public string key; public string name; public List<string> effects; }

    internal class MonsterFile { public List<JsonMonster> monsters {get;set;} }
    internal class JsonMonster { public int id; public string key; public string name; public int threatTier; }

    internal class BuildingFile { public List<JsonBuilding> buildings {get;set;} }
    internal class JsonBuilding { public int id; public string key; public string name; public string category; }

    internal class RecipeFile { public List<JsonRecipe> recipes {get;set;} }
    internal class JsonRecipe { public int id; public string key; public List<JsonIO> inputs; public List<JsonIO> outputs; public float time; }
    internal class JsonIO { public string item; public int count; }

    public static class RegistryBootstrap {
        public static void LoadAll(string modsFolder){
            string root = Path.Combine(Application.dataPath, "..", modsFolder);
            LoadItems(Path.Combine(root, "items.alpha.json"));
            LoadEvents(Path.Combine(root, "events.beta.json"));
            LoadDoctrines(Path.Combine(root, "doctrines.alpha.json"));
            LoadMonsters(Path.Combine(root, "monsters.alpha.json"));
            LoadBuildings(Path.Combine(root, "buildings.alpha.json"));
            LoadRecipes(Path.Combine(root, "recipes.alpha.json"));
        }
        static T ReadJson<T>(string path){
            if(!File.Exists(path)){
                Debug.unityLogger.LogWarning("Registry", $"Missing json file {path}");
                return default;
            }
            var opts = new JsonSerializerOptions{PropertyNameCaseInsensitive = true};
            return JsonSerializer.Deserialize<T>(File.ReadAllText(path), opts);
        }
        static void LoadItems(string path){
            var data = ReadJson<ItemFile>(path); if(data?.items==null) return;
            foreach(var i in data.items) ItemRegistry.All.Add(new(i.id,i.name,i.category,i.perishable));
        }
        static void LoadEvents(string path){
            var data = ReadJson<EventFile>(path); if(data?.events==null) return;
            foreach(var e in data.events){
                var choices = new List<EventChoice>();
                if(e.choices!=null){
                    foreach(var c in e.choices){
                        choices.Add(new EventChoice(
                            c.key,
                            c.description,
                            c.effects?.ToArray() ?? System.Array.Empty<string>()));
                    }
                }
                EventRegistry.All.Add(new(e.id,e.key,e.title,e.description,choices));
            }
        }
        static void LoadDoctrines(string path){
            var data = ReadJson<DoctrineFile>(path); if(data?.doctrines==null) return;
            foreach(var d in data.doctrines)
                DoctrineRegistry.All.Add(new(d.id,d.key,d.name,d.effects?.ToArray()??System.Array.Empty<string>()));
        }
        static void LoadMonsters(string path){
            var data = ReadJson<MonsterFile>(path); if(data?.monsters==null) return;
            foreach(var m in data.monsters)
                MonsterRegistry.All.Add(new(m.id,m.key,m.name,m.threatTier));
        }
        static void LoadBuildings(string path){
            var data = ReadJson<BuildingFile>(path); if(data?.buildings==null) return;
            foreach(var b in data.buildings)
                BuildingRegistry.All.Add(new(b.id,b.key,b.name,b.category));
        }
        static void LoadRecipes(string path){
            var data = ReadJson<RecipeFile>(path); if(data?.recipes==null) return;
            foreach(var r in data.recipes){
                var inputs = r.inputs?.Select(x => new RecipeIO(x.item,x.count)).ToList()?? new();
                var outputs = r.outputs?.Select(x => new RecipeIO(x.item,x.count)).ToList()?? new();
                RecipeRegistry.All.Add(new(r.id,r.key,inputs,outputs,r.time));
            }
        }
    }
}