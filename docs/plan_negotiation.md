# Plan — Negotiation Strategy Component

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_negotiation.md`

---

## 1. Module Layout

```text
backend/app/negotiation/
  manager.py
  policy_base.py
  rule_based_policy.py
  performance_table_policy.py
  contextual_bandit_policy.py
  opponent_profile.py
  presets.py
  schemas.py
  training.py
  tests/
```

---

## 2. Development Stages

### Stage 1 — Rule-Based Policy

Rules:

- accept exact supported config;
- reject unsupported config;
- counter with default official preset;
- prefer configs with available exact Actor models.

### Stage 2 — Performance Table

Use offline Actor evaluations:

```text
config_preset_id, cop_score, thief_score, average_match_score
```

Select the preset with best expected local score.

### Stage 3 — Contextual Bandit

Treat each rule preset as an arm. Context includes opponent identity, model availability, and recent results.

Reward:

```text
local_match_score - opponent_match_score - negotiation_penalty
```

### Stage 4 — Optional RL Negotiation

Use only if negotiation becomes multi-step and strategically meaningful.

---

## 3. Self-Play Training Loop

```text
1. sample local policy and opponent policy
2. negotiate config
3. if agreement reached, run simulated 6-sub-game match
4. compute reward from final score
5. update negotiation policy
6. store result in opponent/profile tables
```

---

## 4. Data Artifacts

```text
data/negotiation/presets.json
data/negotiation/performance_table.csv
data/negotiation/opponent_profiles.json
models/negotiation/bandit_state.json
```

---

## 5. Integration

```text
MCP proposal received
  -> NegotiationManager.evaluate_proposal
  -> structured decision
  -> LLM Agent verbalizes
  -> MCP Client/Server sends response
```

---

## 6. Tests

Required tests:

- unsupported config rejected;
- exact supported config accepted;
- better local preset selected;
- opponent profile updates after match;
- bandit update changes preference after repeated losses;
- LLM Agent receives only structured decision, not hidden game state.
