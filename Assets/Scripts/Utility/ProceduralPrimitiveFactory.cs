using UnityEngine;
using FrostbornRealms.Visual;

namespace FrostbornRealms.Utility {
    public static class ProceduralPrimitiveFactory {
        public static GameObject CreatePlaceholder(string label, MaterialKey matKey, PrimitiveType type = PrimitiveType.Cube) {
            var go = GameObject.CreatePrimitive(type); go.name = $"PH_{{label}}"; var renderer = go.GetComponent<Renderer>(); renderer.sharedMaterial = MaterialLibrary.Get(matKey);
#if UNITY_EDITOR
            var txt = new GameObject("Label"); txt.transform.SetParent(go.transform); txt.transform.localPosition = Vector3.up * 1.5f; var tm = txt.AddComponent<TextMesh>(); tm.text = label; tm.characterSize = 0.2f; tm.anchor = TextAnchor.MiddleCenter; tm.color = Color.white;
#endif
            return go;
        }
    }
}