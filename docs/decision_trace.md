# Decision Trace Format (Implemented v1)

Entries appended to world.state.decision_feed (last 50):
```
{
  "tick": 200,
  "type": "LeaderDecision",
  "options": [
    {"type":"build","target":"Housing","score":0.4,"afford":true},
    {"type":"build","target":"Storage","score":0.3,"afford":true},
    ...
  ],
  "chosen":"Housing"
}
```

Intervention Mode:
- If on, chosen decision stored in LeaderAI.intervention_pending array.
- Client must send confirm_decision {index} or reject_decision {index}.
- On confirm: enact_decision executes (build site spawn).
- On reject: pending removed; no fallback decision auto-picked this cycle.
