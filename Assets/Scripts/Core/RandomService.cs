using System;

namespace FrostbornRealms.Core {
    public class RandomService {
        private Random _rng;
        public RandomService(int seed) { _rng = new Random(seed); }
        public int NextInt(int minInclusive, int maxExclusive) => _rng.Next(minInclusive, maxExclusive);
        public float NextFloat() => (float)_rng.NextDouble();
        public bool Chance(float p) => NextFloat() < p;
        public T Pick<T>(T[] arr) => arr.Length == 0 ? default : arr[NextInt(0, arr.Length)];
    }
}