using UnityEngine;
using Unity.Entities;
using FrostbornRealms.ECS.Components;

namespace FrostbornRealms.UI {
    public class DebugHUD : MonoBehaviour {
        bool _visible = true;
        Rect _rect = new Rect(10,10,380,240);
        World _world;

        void Awake(){ _world = World.DefaultGameObjectInjectionWorld; }

        void Update(){
            if(Input.GetKeyDown(KeyCode.F3)) _visible = !_visible;
            if(Input.GetKeyDown(KeyCode.F5)) SaveLoad.SaveLoadService.Save(_world);
            if(Input.GetKeyDown(KeyCode.F9)) SaveLoad.SaveLoadService.Load(_world);
        }

        void OnGUI(){
            if(!_visible) return;
            GUILayout.BeginArea(_rect, GUI.skin.box);
            GUILayout.Label("== DEBUG HUD ==");
            var em = _world.EntityManager;
            var needsQuery = em.CreateEntityQuery(typeof(Needs));
            using(var arr = needsQuery.ToComponentDataArray<Needs>(Unity.Collections.Allocator.Temp)){
                if(arr.Length>0){
                    float avgH=0, avgW=0, avgM=0, avgF=0;
                    foreach(var n in arr){
                        avgH += n.Hunger; avgW += n.Warmth; avgM += n.Morale; avgF += n.Fatigue;
                    }
                    float inv = 1f/arr.Length;
                    GUILayout.Label($"Needs Avg  H:{avgH*inv:F1}  W:{avgW*inv:F1}  M:{avgM*inv:F1}  F:{avgF*inv:F1}");
                } else GUILayout.Label("No Citizens");
            }
            GUILayout.Label("[F5] Save  [F9] Load  [F3] Toggle HUD");
            GUILayout.EndArea();
        }
    }
}