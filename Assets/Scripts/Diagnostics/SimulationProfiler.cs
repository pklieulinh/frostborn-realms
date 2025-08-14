using UnityEngine;

namespace FrostbornRealms.Diagnostics {
    public static class SimulationProfiler {
        private static int _eventsResolved;
        public static void IncEvents() => _eventsResolved++;
        public static void ResetFrame() { _eventsResolved = 0; }
        public static void DrawGUI() {
            GUI.Label(new Rect(8,8,300,20), $"Events Resolved: {_eventsResolved}");
        }
    }
}