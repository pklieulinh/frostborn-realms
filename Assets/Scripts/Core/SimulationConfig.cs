using UnityEngine;

namespace FrostbornRealms.Core {
    [CreateAssetMenu(fileName = "SimulationConfig", menuName = "Frostborn/SimulationConfig")]
    public class SimulationConfig : ScriptableObject {
        [Header("Needs Decay per second")]
        public float HungerDecay = 0.5f;
        public float WarmthDecay = 0.2f;
        public float MoraleDecay = 0.05f;
        public float FatigueGain = 0.3f;

        [Header("Event System")]
        public float EventCheckInterval = 20f;
        public float EventProbability = 0.35f;

        [Header("Doctrine")]
        public float StoicismMoraleDecayMultiplier = 0.85f;

        [Header("Heat")]
        public float AmbientTemperature = -20f;
        public float CitizenComfortTemp = 5f;
        public float WarmthBonusPerTempDegree = 0.02f;

        [Header("Crafting")]
        public int MaxParallelCrafts = 4;
    }
}