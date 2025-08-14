namespace FrostbornRealms.Core {
    public class TimeService {
        public float DeltaTime { get; private set; }
        public float Elapsed { get; private set; }
        public void Tick(float dt) { DeltaTime = dt; Elapsed += dt; }
    }
}