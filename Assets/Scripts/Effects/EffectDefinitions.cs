using Unity.Entities;
using Unity.Collections;

namespace FrostbornRealms.Effects {
    public enum EffectOp : byte {
        AdjustNeed,
        AddItem,
        RemoveItem,
        AdjustCategory,
        DoctrineProgress
    }

    public enum NeedType : byte { Hunger, Warmth, Morale, Fatigue }

    public struct EffectAction {
        public EffectOp Op;
        public NeedType Need;
        public float NeedDelta;
        public int ItemId;
        public int ItemCount;
        public int CategoryKey;
        public int DoctrineKey;
        public float DoctrineAmount;
    }

    public struct EffectToken : IBufferElementData {
        public FixedString64Bytes Value;
    }

    public struct EffectActionBuffer : IBufferElementData {
        public EffectAction Action;
    }

    public struct EffectQueueTag : IComponentData {}
}