using UnityEngine;

namespace FrostbornRealms.Diagnostics {
    public class FrameStatsCollector : MonoBehaviour {
        void OnGUI() {
            SimulationProfiler.DrawGUI();
        }
    }
}