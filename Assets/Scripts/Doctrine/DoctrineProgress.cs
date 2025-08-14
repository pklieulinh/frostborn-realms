using Unity.Entities;
using System.Collections.Generic;

namespace FrostbornRealms.Doctrine {
    public struct DoctrineProgressTag : IComponentData {}
    public struct DoctrineProgressEntry : IBufferElementData {
        public int KeyHash;
        public float Progress;
    }

    public static class DoctrineProgressAPI {
        static Entity _entity;
        static EntityManager _em;
        static bool _init;
        public static void Init(Entity e, EntityManager em){ _entity=e; _em=em; _init=true; }
        public static void AddProgress(int hash, float amt){
            if(!_init) return;
            var buf = _em.GetBuffer<DoctrineProgressEntry>(_entity);
            for(int i=0;i<buf.Length;i++){
                if(buf[i].KeyHash == hash){
                    var entry = buf[i];
                    entry.Progress += amt;
                    buf[i] = entry;
                    return;
                }
            }
            buf.Add(new DoctrineProgressEntry{ KeyHash = hash, Progress = amt});
        }
        public static Dictionary<int,float> Snapshot(){
            var buf = _em.GetBuffer<DoctrineProgressEntry>(_entity);
            var dict = new Dictionary<int,float>(buf.Length);
            for(int i=0;i<buf.Length;i++) dict[buf[i].KeyHash] = buf[i].Progress;
            return dict;
        }
        public static void Load(Dictionary<int,float> snap){
            var buf = _em.GetBuffer<DoctrineProgressEntry>(_entity);
            buf.Clear();
            if(snap!=null){
                foreach(var kv in snap) buf.Add(new DoctrineProgressEntry{ KeyHash = kv.Key, Progress = kv.Value});
            }
        }
    }
}