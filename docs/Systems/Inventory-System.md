# Inventory System (Planned)

## Vision
Hybrid model:
- Global stockpile entity for shared basics
- Optional per-citizen lightweight personal inventory (equipment / task items)
- Aggregation system compiles snapshot for UI & decisions.

## Current State
InventoryRef component exists; InventoryAggregationSystem placeholder.

## Next Milestone
- Introduce InventoryComponent with dynamic buffer (item id + count)
- Commands: AddItem, RemoveItem routed through InventoryCommandBufferSystem
- Crafting System consumes inputs / produces outputs via recipe lookup
- Decay System for perishable items (tick-based)

## Crafting Flow (Planned)
ActionRequest(Type=Craft) -> CraftingSystem:
1. Validate inputs (global or local)
2. Reserve items (lock semantics for concurrency)
3. Countdown time
4. Commit outputs

## Persistence
Later Save/Load writes JSON arrays of (itemId,count,flags).