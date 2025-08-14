using System.Collections.Generic;

namespace FrostbornRealms.Data {
    public record ItemDef(int Id, string Name, string Category, bool Perishable);
    public record EventChoice(string Key, string Description, string[] Effects);
    public record EventDef(int Id, string Key, string Title, string Description, List<EventChoice> Choices);
    public record DoctrineDef(int Id, string Key, string Name, string[] Effects);
    public record MonsterDef(int Id, string Key, string Name, int ThreatTier);
    public record BuildingDef(int Id, string Key, string Name, string Category);
    public record RecipeIO(string Item, int Count);
    public record RecipeDef(int Id, string Key, List<RecipeIO> Inputs, List<RecipeIO> Outputs, float Time);
}