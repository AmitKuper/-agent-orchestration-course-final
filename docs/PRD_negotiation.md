# PRD — Negotiation Strategy Component

> **Document type:** Product Requirements Document  
> **Scope:** Requirements for selecting match terms before inter-group MCP matches.

---

## 1. Purpose

The Negotiation Strategy component decides what match configuration to propose, accept, reject, or counter-propose when playing against other group servers.

The component chooses negotiation strategy. The LLM Agent only expresses that strategy in natural language and invokes MCP tools.

---

## 2. Responsibilities

The component must:

- evaluate supported rule configurations;
- use local Actor capabilities and model performance;
- use opponent history when available;
- decide whether to accept, reject, or counter-propose;
- produce structured negotiation actions;
- support learning from self-play and historical matches;
- log negotiation decisions and outcomes.

---

## 3. Non-Responsibilities

The component must not:

- generate final natural-language messages;
- call remote MCP tools directly;
- validate authoritative game rules;
- choose board actions during a sub-game;
- access hidden live-game state.

---

## 4. Negotiation Action Space

The component must support structured actions such as:

```text
ACCEPT
REJECT
ASK_CAPABILITIES
PROPOSE_PRESET
COUNTER_PROPOSE
REQUEST_RULE_CHANGE
REQUEST_ROLE_SCHEDULE
```

Each action must include a structured payload when needed.

---

## 5. Inputs

The component may use:

- local server capabilities;
- remote server capabilities;
- allowed official rule presets;
- current proposal;
- model bank metadata;
- actor evaluation results by rule preset;
- opponent profile/history;
- negotiation turn count;
- administrative constraints.

---

## 6. Output

Example output:

```json
{
  "decision": "COUNTER_PROPOSE",
  "reason": "Local models perform better on partial observation radius 2.",
  "proposal": {
    "preset_id": "tactical_partial_r2",
    "config": {}
  }
}
```

The LLM Agent converts this into text and MCP calls.

---

## 7. Learning Requirement

The component must support learning from repeated self-play and historical matches.

The system should support this progression:

1. rule-based negotiation;
2. performance-table preset selection;
3. contextual bandit over rule presets;
4. optional reinforcement-learning policy for multi-step negotiation.

For MVP, a rule-based or performance-table strategy is sufficient.

---

## 8. Acceptance Criteria

The component is acceptable when:

- it can propose a valid supported configuration;
- it can reject unsupported configurations;
- it can select a preferred preset using local Actor evaluation data;
- it can use opponent history if available;
- it returns structured decisions for the LLM Agent;
- all negotiation decisions are logged and replayable.
