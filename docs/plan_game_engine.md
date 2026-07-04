# Plan — Game Engine Component

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_game_engine.md`  
> **Scope:** How to implement the deterministic rules engine used by REST, MCP, actors, replay, and tests.

---

## 1. Purpose

Implement the game engine as the single authoritative source for rules, state transitions, validation, scoring, replay state, observation filtering, and state hashing.

The engine must not depend on FastAPI, MCP, the web UI, LLM APIs, or model-training code.

---

## 2. Design Principles

- Pure Python package with no web-server dependencies.
- Deterministic behavior from config, seed, initial state, and action sequence.
- Explicit separation between true state and actor observation.
- No hidden-state leakage through legal-action lists or error messages.
- Engine validates all actions, even if actors or remote servers claim the action is legal.
- Game logs must be replayable into the same terminal state.

---

## 3. Suggested Package Layout

```text
src/cop_thief/game_engine/
  __init__.py
  config.py
  constants.py
  coordinates.py
  actions.py
  state.py
  observations.py
  validation.py
  transitions.py
  win_conditions.py
  scoring.py
  crumbtrails.py
  barriers.py
  role_schedule.py
  hashing.py
  replay.py
  errors.py
  tests/
    test_movement.py
    test_barriers.py
    test_trapped.py
    test_survival.py
    test_observation.py
    test_hashing.py
    test_replay.py
```

Follow the repository rule that implementation files should stay small and focused. Split modules instead of creating large monolithic files.

---

## 4. Core Classes

```text
GameConfig
GameState
ObservationState
Action
ActionResult
GameEngine
RoleSchedule
ReplayLog
StateHasher
```

`GameEngine` should expose a small SDK-facing API:

```python
initialize_subgame(config, seed, roles) -> GameState
get_observation(state, actor_side_or_role) -> ObservationState
get_available_intended_actions(state, actor_role) -> list[ActionDescriptor]
apply_action(state, actor_role, action) -> ActionResult
is_terminal(state) -> bool
score_subgame(state) -> ScoreResult
state_hash(state) -> str
```

---

## 5. Implementation Order

1. Config model and validation.
2. Coordinate and movement utilities.
3. Game state model.
4. Action schema and parser.
5. Movement validation.
6. Barrier validation.
7. Turn counters and consumed-action semantics.
8. Win-condition detection.
9. Observation filtering.
10. Crumbtrail logic.
11. State hashing.
12. Replay from event logs.
13. Integration tests for full 6-sub-game matches.

---

## 6. Testing Strategy

Use unit tests for each rules module and integration tests for full matches.

Required test stages:

| Stage | Grid | Goal |
|---|---|---|
| 1 | 2x2 | Basic movement, capture, invalid actions. |
| 2 | 3x2 / 2x3 | Turn order, survival timing, trapping. |
| 3 | 4x3 / 3x4 | Barriers and partial observation. |
| 4 | 5x5 | Crumbtrails and replay/hash validation. |
| 5 | 10x10 | Default full gameplay. |

---

## 7. Integration Points

| Consumer | Engine Responsibility |
|---|---|
| Web server | create matches, apply human/server actions, produce replay data. |
| REST API | validate and apply action requests through orchestration. |
| MCP API | validate remote actions and compare hashes. |
| Actor system | provide actor-scoped observations and action masks. |
| LLM agent | provide only observation-safe summaries and action results. |
| Report system | provide final match/sub-game results and event logs. |

---

## 8. Acceptance Checklist

- All PRD game rules are implemented.
- Full 6-valid-sub-game match succeeds.
- Technical-invalid sub-games are not scored.
- Hidden state never appears in actor observation under partial observation.
- Rejected invalid actions do not increment counters.
- Consumed failed moves increment counters correctly.
- Replay reconstructs the same terminal state.
- State hashes match across deterministic duplicate engines.
