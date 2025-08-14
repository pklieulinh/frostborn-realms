using Unity.Entities;
using Unity.Mathematics;
using FrostbornRealms.Heat;
using FrostbornRealms.ECS.Components;
using FrostbornRealms.Core;

namespace FrostbornRealms.ECS.Systems {
    public partial struct HeatDiffusionSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}

        public void OnUpdate(ref SystemState state) {
            var cfg = ServiceLocator.Get<SimulationConfig>();
            float ambient = cfg.AmbientTemperature;
            float dt = SystemAPI.Time.DeltaTime;

            foreach(var temp in SystemAPI.Query<RefRW<Temperature>>()){
                temp.ValueRW.Value = math.lerp(temp.ValueRO.Value, ambient, dt * 0.2f);
            }

            var sources = SystemAPI.Query<RefRO<HeatSource>, RefRO<Position>>();
            foreach(var (temp, pos) in SystemAPI.Query<RefRW<Temperature>, RefRO<Position>>()){
                float added = 0f;
                foreach(var (hs, sPos) in sources){
                    float dist = math.distance(pos.ValueRO.Value, sPos.ValueRO.Value);
                    if(dist <= hs.ValueRO.Radius){
                        float t = 1f - dist/hs.ValueRO.Radius;
                        added += hs.ValueRO.Intensity * t * t;
                    }
                }
                temp.ValueRW.Value += added * dt;
            }
        }
    }

    public partial struct CitizenHeatAffectSystem : ISystem {
        public void OnCreate(ref SystemState state) {}
        public void OnDestroy(ref SystemState state) {}

        public void OnUpdate(ref SystemState state){
            var cfg = ServiceLocator.Get<SimulationConfig>();
            foreach(var (needs, pos) in SystemAPI.Query<RefRW<Needs>, RefRO<Position>>()){
                float nearestTemp = cfg.AmbientTemperature;
                float bestDist = float.MaxValue;
                foreach(var (temp, tPos) in SystemAPI.Query<RefRO<Temperature>, RefRO<Position>>()){
                    float d = math.distance(pos.ValueRO.Value, tPos.ValueRO.Value);
                    if(d < bestDist){
                        bestDist = d;
                        nearestTemp = temp.ValueRO.Value;
                    }
                }
                float delta = nearestTemp - cfg.AmbientTemperature;
                if(delta > 0){
                    needs.ValueRW.Warmth = math.min(100, needs.ValueRW.Warmth + delta * cfg.WarmthBonusPerTempDegree * SystemAPI.Time.DeltaTime);
                }
            }
        }
    }
}