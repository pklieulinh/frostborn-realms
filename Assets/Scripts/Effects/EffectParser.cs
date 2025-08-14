using System;
using System.Globalization;
using System.Collections.Generic;
using FrostbornRealms.Data;

namespace FrostbornRealms.Effects {
    public static class EffectParser {
        static Dictionary<string,int> _itemNameToId;
        static bool _cached;

        static void EnsureCache(){
            if(_cached) return;
            _itemNameToId = new(StringComparer.OrdinalIgnoreCase);
            foreach(var item in ItemRegistry.All){
                if(!_itemNameToId.ContainsKey(item.Name))
                    _itemNameToId[item.Name] = item.Id;
            }
            _cached = true;
        }

        static bool TryParseNumber(string s, out float val){
            return float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out val);
        }

        public static void ParseToken(string token, List<EffectAction> outActions){
            EnsureCache();
            token = token.Trim();
            if(string.IsNullOrEmpty(token)) return;

            if (ParseNeedAdjust(token, out var act)) { outActions.Add(act); return; }

            if (token.StartsWith("add_item:", StringComparison.OrdinalIgnoreCase)) {
                var p = token.Split(':');
                if(p.Length >=3 && _itemNameToId.TryGetValue(p[1], out var id) && int.TryParse(p[2], out var c)){
                    outActions.Add(new EffectAction{ Op=EffectOp.AddItem, ItemId=id, ItemCount=c});
                }
                return;
            }
            if (token.StartsWith("remove_item:", StringComparison.OrdinalIgnoreCase)) {
                var p = token.Split(':');
                if(p.Length >=3 && _itemNameToId.TryGetValue(p[1], out var id) && int.TryParse(p[2], out var c)){
                    outActions.Add(new EffectAction{ Op=EffectOp.RemoveItem, ItemId=id, ItemCount=c});
                }
                return;
            }
            if (token.StartsWith("doctrine_progress:", StringComparison.OrdinalIgnoreCase)){
                var p = token.Split(':');
                if(p.Length >=3 && TryParseNumber(p[2], out var amt)){
                    outActions.Add(new EffectAction{ Op=EffectOp.DoctrineProgress, DoctrineKey=p[1].GetHashCode(), DoctrineAmount=amt});
                }
                return;
            }
            if (ParseCategoryAdjust(token, out var cat)){
                outActions.Add(cat);
                return;
            }
        }

        static bool ParseNeedAdjust(string token, out EffectAction act){
            act = default;
            string[] needs = {"morale","warmth","hunger","fatigue"};
            foreach(var n in needs){
                if(token.StartsWith(n, StringComparison.OrdinalIgnoreCase)){
                    var rest = token.Substring(n.Length);
                    if(rest.Length>1 && (rest[0]=='+' || rest[0]=='-') && TryParseNumber(rest, out var val)){
                        NeedType nt = n switch {
                            "morale" => NeedType.Morale,
                            "warmth" => NeedType.Warmth,
                            "hunger" => NeedType.Hunger,
                            "fatigue" => NeedType.Fatigue,
                            _ => NeedType.Morale
                        };
                        act = new EffectAction{ Op=EffectOp.AdjustNeed, Need=nt, NeedDelta=val};
                        return true;
                    }
                }
            }
            return false;
        }

        static bool ParseCategoryAdjust(string token, out EffectAction act){
            act = default;
            string[] cats = {"fuel","food","medicine"};
            foreach(var c in cats){
                if(token.StartsWith(c, StringComparison.OrdinalIgnoreCase)){
                    var rest = token.Substring(c.Length);
                    if(rest.Length>1 && (rest[0]=='+' || rest[0]=='-') && TryParseNumber(rest, out var val)){
                        act = new EffectAction{ Op=EffectOp.AdjustCategory, CategoryKey=c.GetHashCode(), ItemCount=(int)val };
                        return true;
                    }
                }
            }
            return false;
        }

        public static List<EffectAction> ParseTokens(IEnumerable<string> tokens){
            var list = new List<EffectAction>();
            foreach(var t in tokens) ParseToken(t, list);
            return list;
        }
    }
}