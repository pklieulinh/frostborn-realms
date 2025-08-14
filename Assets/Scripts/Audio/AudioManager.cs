using System.Collections.Generic;
using UnityEngine;
using FrostbornRealms.Core;
using FrostbornRealms.Assets;

namespace FrostbornRealms.Audio {
    public class AudioManager : MonoBehaviour {
        const int PoolSize = 12;
        Queue<AudioSource> _pool = new();
        List<AudioSource> _active = new();
        AudioSource _ambient;
        static AudioManager _instance;

        public static AudioManager Instance {
            get {
                if (_instance == null) {
                    var go = new GameObject("AudioManager");
                    _instance = go.AddComponent<AudioManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        void Awake() {
            if (_instance != null && _instance != this) { Destroy(gameObject); return; }
            _instance = this;
            for (int i=0;i<PoolSize;i++) {
                var s = gameObject.AddComponent<AudioSource>();
                s.playOnAwake = false;
                _pool.Enqueue(s);
            }
            _ambient = gameObject.AddComponent<AudioSource>();
            _ambient.loop = true;
        }

        AudioSource GetSource() {
            if (_pool.Count > 0) {
                var s = _pool.Dequeue();
                _active.Add(s);
                return s;
            }
            var extra = gameObject.AddComponent<AudioSource>();
            extra.playOnAwake = false;
            _active.Add(extra);
            return extra;
        }

        public void PlayOneShot(string key, float volumeScale = 1f) {
            var clip = AssetResolver.Audio(key);
            if (!clip) return;
            var src = GetSource();
            src.clip = clip;
            src.volume = volumeScale;
            src.loop = false;
            src.Play();
            StartCoroutine(RecycleWhenDone(src));
        }

        public void PlayAmbient(string key, float fadeSeconds = 1.5f) {
            var clip = AssetResolver.Audio(key);
            if (_ambient.clip == clip) return;
            StopAllCoroutines();
            StartCoroutine(SwapAmbient(clip, fadeSeconds));
        }

        System.Collections.IEnumerator SwapAmbient(AudioClip target, float fade) {
            float t=0;
            float start = _ambient.volume;
            while (t<fade) {
                t += Time.deltaTime;
                _ambient.volume = Mathf.Lerp(start, 0, t/fade);
                yield return null;
            }
            _ambient.clip = target;
            if (target) _ambient.Play();
            t=0;
            while (t<fade) {
                t += Time.deltaTime;
                _ambient.volume = Mathf.Lerp(0, 1, t/fade);
                yield return null;
            }
        }

        System.Collections.IEnumerator RecycleWhenDone(AudioSource s) {
            while (s.isPlaying) yield return null;
            s.clip = null;
            _active.Remove(s);
            _pool.Enqueue(s);
        }
    }
}