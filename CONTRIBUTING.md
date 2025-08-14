# Contributing

## Commit Style
Use Conventional Commits:
- feat: new feature
- fix: bug fix
- chore: tooling changes
- docs: documentation
- refactor: no behavior change
- perf: performance improvements
- test: tests

## Branching
Feature branches per milestone slice. Example:
2-ecs-core, 3-heat-system

## JSON Data
Run CI locally (ajv) or rely on GH Actions to validate schema.

## Code Style
4 spaces, LF, final newline. Keep systems small & pure where possible.

## Performance
Burst + Entities friendly patterns: avoid large managed allocations in OnUpdate loops.

## PR Guidelines
Describe:
1. Motivation
2. Architectural Impact
3. Test / Validation steps
4. Follow-ups