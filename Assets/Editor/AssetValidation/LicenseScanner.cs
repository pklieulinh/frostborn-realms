#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FrostbornRealms.EditorTools {
    public static class LicenseScanner {
        [MenuItem("Tools/Frostborn/Scan Asset Licenses")]
        public static void Scan() {
            string root = "Assets/External";
            if (!Directory.Exists(root)) {
                Debug.LogWarning("No Assets/External directory.");
                return;
            }
            var dirs = Directory.GetDirectories(root, "*", SearchOption.AllDirectories);
            int ok=0, missing=0;
            foreach (var d in dirs) {
                var files = Directory.GetFiles(d, "*", SearchOption.TopDirectoryOnly);
                bool hasLicense = false;
                foreach (var f in files) {
                    var name = Path.GetFileName(f).ToLowerInvariant();
                    if (name.StartsWith("license") || name == "license.txt" || name == "readme.txt") {
                        hasLicense = true; break;
                    }
                }
                if (hasLicense) ok++; else { missing++; Debug.LogWarning($"[LicenseScanner] Missing LICENSE in: {d}"); }
            }
            Debug.Log($"[LicenseScanner] Scan complete. Folders OK={ok}, Missing={missing}");
        }
    }
}
#endif