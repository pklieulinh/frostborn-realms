# Frostborn Realms – Roadmap

## Milestone Sequence (Repository Branch Strategy)
1. init-project (YOU just performed via initial commit) – manifest only.
2. 2-ecs-core
   - Base components: Position, Needs (Packed), Movement, ActionRequest
   - Basic Systems: Needs decay, Movement, JobAssignment
   - Save/Load skeleton
3. 3-simulation-systems
   - Heat (frontier baseline), Events Loader, Doctrine modifiers
   - Inventory + Crafting core
4. 4-boss-trade-overlay
   - Leviathan Phase 1–3 systems (phase controller, anchors, pulses)
   - Trade Demand, Caravan spawn/move
   - Overlay palettes + colorblind switch
5. 5-content-json-full
   - All JSON registries (already included, but integrate loaders)
   - Effect Dispatcher robust mapping
6. 6-heat-job-path-optim
   - Jobified heat diffusion full
   - Hierarchical path caching (flow fields)
7. 7-beta-polish
   - Balancing passes, profiling instrumentation, replay delta
8. 8-final-beta-package
   - Documentation polish, CI workflows, tag v0.9.0-beta

## Post-Beta (Future)
- Biomes expansion
- Advanced Diplomacy & Multi-faction trade
- Animation & VFX pass
- Additional Boss patterns
- Workshop (Mod distribution pipeline)
