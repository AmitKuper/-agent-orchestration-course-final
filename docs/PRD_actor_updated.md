# PRD — Actor System: Cop & Thief Pursuit Game

> This document defines the product requirements for the Actor system.
> The Actor system is responsible for selecting legal game actions for Cop and Thief roles under the current game rules, observation model, and match configuration.
>
> This PRD is requirements-only. Implementation details such as training algorithms, model formats, storage technology, and serving architecture should be described in a separate implementation plan.

---

## 1. Purpose

The Actor system provides automated decision-making for the Cop & Thief pursuit game.

The system must support:

- A **Cop Actor** that plays the Cop role.
- A **Thief Actor** that plays the Thief role.
- Selection of the most appropriate actor/model according to the active game rules.
- A **Model Bank** containing multiple trained actor weights or strategies.
- Deterministic and valid action selection during gameplay.
- Compatibility with partial observation, barriers, configurable movement rules, crumbtrails, and role alternation.

The Actor system must never contain authoritative game rules. Game legality, state transition, scoring, and win detection remain the responsibility of the Game Engine.

---

## 2. Scope

### 2.1 In Scope

The Actor system must:

- Receive an actor-specific observation from the Game Engine or Game Orchestrator.
- Return exactly one intended action for the current actor turn.
- Support both Cop and Thief roles.
- Support multiple actor models/weights through a Model Bank.
- Select an actor/model based on the current game configuration.
- Avoid using hidden information under partial observation.
- Support fallback behavior when no exact model is available.
- Expose metadata describing model compatibility, version, and expected rule configuration.
- Be testable, reproducible, and auditable.

### 2.2 Out of Scope

The Actor system must not:

- Decide whether an action is legally accepted by the game.
- Mutate the authoritative game state directly.
- Compute scoring.
- Decide game winners.
- Access hidden opponent position or hidden barriers under partial observation.
- Override protocol-level timeout, retry, or technical-invalid behavior.
- Persist public game history or replay data.

---

## 3. Actor Roles

### 3.1 Cop Actor

The Cop Actor must choose actions whose strategic goal is to cause a Cop victory.

Cop victory conditions are defined by the Game Engine and include:

- Capturing the Thief by moving into the Thief's current cell.
- Causing the Thief to become trapped.

The Cop Actor may choose from Cop-supported action types allowed by the active configuration:

- Move in one of the supported movement directions.
- Stay, if `stay_enabled = true`.
- Place a barrier, if barriers are enabled and the Cop has remaining barriers.
- Voluntarily forfeit, only if the protocol/UI explicitly exposes forfeit as an allowed action.

The Cop Actor must understand that only the Cop can capture by entering the Thief's cell. The Cop Actor should not assume the Thief can capture the Cop.

### 3.2 Thief Actor

The Thief Actor must choose actions whose strategic goal is to cause a Thief victory.

Thief victory conditions are defined by the Game Engine and include:

- Surviving until `max_moves` consumed Thief actions.
- Causing the Cop to become trapped.

The Thief Actor may choose from Thief-supported action types allowed by the active configuration:

- Move in one of the supported movement directions.
- Stay, if `stay_enabled = true`.
- Voluntarily forfeit, only if the protocol/UI explicitly exposes forfeit as an allowed action.

The Thief Actor must not attempt to move into the Cop's current cell, because the Thief cannot capture the Cop.

---

## 4. Actor Input / Output Contract

### 4.1 Input: Observation State

Each actor receives an `ObservationState` scoped to the actor's role and current turn.

The observation must include:

- `game_id`
- `subgame_id`
- `actor_role`: `"cop"` or `"thief"`
- `turn_index`
- `thief_actions_consumed`
- `max_moves`
- `grid_size`
- actor's own position
- visible opponent position, or `null` if hidden
- visible barriers
- visible crumbtrails, if enabled and visible
- barriers remaining, for Cop only
- active configuration summary
- available intended actions, not necessarily true legal actions under partial observation
- previous action result, if available

Under partial observation, the observation must not expose hidden state.

### 4.2 Output: Intended Action

The actor must return exactly one intended action.

Allowed action format:

```json
{
  "type": "move",
  "direction": "N"
}
```

```json
{
  "type": "stay"
}
```

```json
{
  "type": "barrier",
  "target": [3, 4]
}
```

```json
{
  "type": "forfeit"
}
```

The actor output must be treated as an intended action. The Game Engine remains responsible for final validation and state transition.

### 4.3 Action Validity Requirement

The Actor should prefer actions from the provided `available_intended_actions` list.

However, because partial observation may hide barriers or opponent location, an action that appears possible to the actor may still fail during engine validation.

The Actor system must handle action results returned by the engine, including:

- `moved`
- `stayed`
- `barrier_placed`
- `invalid_action`
- `failed_move_turn_consumed`
- `capture`
- `trapped`
- `survived`
- `forfeit_loss`
- `technical_invalid`

---

## 5. Supported Game Rules

The Actor system must support the current rule set used by the Game Engine.

At minimum, actors must be compatible with the following configurable mechanics:

| Rule Parameter | Requirement |
|---|---|
| `grid_size` | Actor must support configurable grid dimensions. |
| `max_moves` | Actor must reason over Thief actions consumed until survival. |
| `num_games` | Actor must support 6-sub-game series with role alternation. |
| `max_barriers` | Cop Actor must support configurable barrier count. |
| `view_radius` | Actor must support partial observation radius. |
| `partial_observation` | Actor must support hidden opponent/barriers. |
| `stay_enabled` | Actor must support configurations where STAY is enabled or disabled. |
| `out_of_bounds_behavior` | Actor must handle `stay` or `invalid` behavior. |
| `barrier_collision_behavior` | Actor must handle `stay` or `invalid` behavior. |
| `barrier_placement_scope` | Cop Actor must support `adjacent_only` and `current_and_adjacent`. |
| `starting_position_mode` | Actor must support random and fixed starts. |
| `move_order` | Actor must support `thief_first`, `cop_first`, and `alternating`. |
| `crumbtrail_mode` | Actor must support no trails, one-sided trails, or both trails. |
| `crumbtrail_max_age` | Actor must support finite, zero, and permanent trail history. |
| scoring values | Actor may use scoring values for strategy selection but must not compute official score. |

---

## 6. Model Bank Requirements

### 6.1 Purpose

The Model Bank stores multiple actor models, weights, or strategies so the system can select an appropriate actor for the active game rules.

The Model Bank must support both:

- Cop-role models.
- Thief-role models.

The Model Bank may contain multiple models for the same role, optimized for different rule configurations.

### 6.2 Model Metadata

Every model entry must include metadata.

Required metadata:

```json
{
  "model_id": "cop_10x10_po2_barriers5_v1",
  "role": "cop",
  "rules_version": "1.0",
  "actor_type": "trained_model",
  "created_at": "2026-07-04T00:00:00+03:00",
  "artifact_path": "models/cop_10x10_po2_barriers5_v1",
  "checksum": "sha256:...",
  "supported_config": {
    "grid_size": [10, 10],
    "max_moves": 25,
    "max_barriers": 5,
    "partial_observation": true,
    "view_radius": 2,
    "stay_enabled": true,
    "out_of_bounds_behavior": "stay",
    "barrier_collision_behavior": "stay",
    "barrier_placement_scope": "current_and_adjacent",
    "move_order": "thief_first",
    "crumbtrail_mode": "none",
    "crumbtrail_max_age": -1
  },
  "training_summary": {
    "training_status": "completed",
    "episodes": 200000,
    "training_duration_seconds": 0,
    "evaluation_games": 0,
    "win_rate": null,
    "average_score": null
  }
}
```

### 6.3 Model Compatibility

The Model Bank must support compatibility matching.

Compatibility levels:

1. **Exact Match** — all relevant rule parameters match the current game configuration.
2. **Compatible Match** — model was trained on a broader or equivalent configuration and is safe to use.
3. **Fallback Match** — model is not optimized for the exact configuration but can still produce valid actions.
4. **No Match** — model must not be used.

The system must prefer exact matches over compatible or fallback matches.

### 6.4 Rules Signature

The Actor system must compute a deterministic `rules_signature` from the active configuration.

The signature must be used to:

- Find matching models.
- Store training artifacts.
- Compare model compatibility.
- Debug actor selection.
- Prevent accidental use of incompatible weights.

Example conceptual signature:

```text
rules_v1_grid10x10_moves25_barriers5_po1_r2_stay1_oobstay_bstay_scopecurrentadj_orderthieffirst_trailnone_age-1
```

### 6.5 Actor Selection

Before each sub-game, the Actor Manager must select the appropriate actor for the actor's role and active rules.

Selection order:

1. Exact model for role and rules signature.
2. Compatible model for same role and compatible rule family.
3. Generic trained model for the same role.
4. Heuristic/rule-based actor for the same role.
5. Safe random legal-action actor, only if enabled by configuration.
6. Fail actor initialization if no safe fallback is allowed.

The selected actor and selection reason must be logged.

---

## 7. Training and Retraining Requirements

### 7.1 Offline Training Requirement

The system must support offline training or importing of Cop and Thief actors into the Model Bank.

Offline-trained models must be registered with complete metadata before they are eligible for runtime selection.

### 7.2 Match-Start Training Requirement

Training at the start of every game is not required for MVP.

The Actor system may support match-start training only if all of the following are true:

- The selected training method can finish within a configured time budget.
- The training job produces a model compatible with the exact active rule configuration.
- The training job does not block the server from accepting other requests.
- The resulting actor is evaluated before being selected for live play.
- A fallback actor is available if training fails, times out, or performs poorly.

### 7.3 Training Time Budget

The system must expose configurable training-time limits.

Required settings:

| Setting | Description |
|---|---|
| `training.enabled` | Whether training is enabled at all. |
| `training.allow_match_start_training` | Whether a missing actor may be trained during match setup. |
| `training.max_training_seconds` | Maximum allowed training duration before fallback. |
| `training.min_evaluation_games` | Minimum evaluation games before registering a model. |
| `training.min_acceptance_metric` | Minimum performance threshold required for model selection. |
| `training.background_training_enabled` | Whether missing configurations may be trained asynchronously after fallback selection. |

### 7.4 Training Output Requirements

A successful training job must produce:

- Model artifact or strategy artifact.
- Metadata file.
- Rules signature.
- Training duration.
- Evaluation results.
- Actor version.
- Reproducibility seed or training run ID.
- Registration status in the Model Bank.

### 7.5 Training Failure Behavior

If training fails or times out, the Actor system must:

- Log the failure reason.
- Avoid registering the failed model as usable.
- Select the next fallback actor if available.
- Return a clear actor-selection status to the Game Orchestrator.

---

## 8. Runtime Behavior

### 8.1 Initialization

At match or sub-game start, the Actor Manager must receive:

- role
- active game configuration
- rules version
- rules signature
- model-bank path or registry reference
- fallback policy

The Actor Manager must return:

- selected actor ID
- actor role
- model compatibility level
- selection reason
- selected model metadata

### 8.2 Per-Turn Action Selection

For every actor turn:

1. Receive actor-scoped observation.
2. Verify observation role matches actor role.
3. Select one intended action.
4. Return action within the configured turn timeout.
5. Record optional actor diagnostics.

The Actor must not mutate authoritative state.

### 8.3 Result Feedback

The Actor system must support result feedback after each submitted action.

Feedback may include:

- action accepted or rejected
- final action result
- updated observation
- reward signal, if online learning is enabled
- terminal result, if the sub-game ended

Online learning is optional and must be disabled by default unless explicitly configured.

---

## 9. Partial Observation Requirements

When `partial_observation = true`, the Actor must receive only actor-visible information.

The Actor must not receive:

- hidden opponent position
- hidden barriers
- global full board state
- true legal actions that reveal hidden barriers
- opponent private observation
- opponent internal model state

The Actor may receive:

- own position
- visible opponent position, if within view radius
- visible barriers
- visible crumbtrails
- available intended actions based on visible information
- previous action result
- public counters and configuration

Public counters include:

- turn index
- Thief actions consumed
- max moves
- barriers remaining, if actor is Cop
- sub-game index
- series index

---

## 10. Barrier Requirements

The Cop Actor must support barrier placement according to the active configuration.

Barrier-related actor requirements:

- Use `max_barriers` and barriers remaining.
- Respect `barrier_placement_scope`.
- Avoid placing barriers outside the grid.
- Avoid placing barriers on the Thief's current cell if visible.
- Avoid placing barriers on occupied or already-barriered visible cells.
- Understand that barriers remain for the entire sub-game.
- Understand that hidden barriers may still block movement.

If `barrier_placement_scope = "current_and_adjacent"`, the Cop Actor may propose a barrier on its current cell, but the Game Engine is authoritative over whether the placement is accepted.

---

## 11. Crumbtrail Requirements

The Actor system must support observations that include crumbtrail data.

Crumbtrail-related requirements:

- Support `crumbtrail_mode = "none"`.
- Support `crumbtrail_mode = "thief_only"`.
- Support `crumbtrail_mode = "cop_only"`.
- Support `crumbtrail_mode = "both"`.
- Support `crumbtrail_max_age = 0`.
- Support finite positive crumbtrail age.
- Support `crumbtrail_max_age = -1` for permanent trails.
- Treat crumbtrails as informational only.
- Never treat crumbtrails as blocking cells.

The Actor must be able to ignore crumbtrail data if the selected model does not use it, as long as the returned action remains valid and safe.

---

## 12. Determinism and Reproducibility

The Actor system must support deterministic inference when configured with a fixed seed.

Requirements:

- Same actor model + same observation + same seed must produce the same action.
- Randomized fallback actors must be seedable.
- Selected actor ID must be logged.
- Model checksum must be logged.
- Actor version must be logged.
- Rules signature must be logged.

---

## 13. Logging and Audit Requirements

For every sub-game, the system must log:

- selected Cop Actor ID
- selected Thief Actor ID
- model compatibility level for each actor
- rules signature
- model metadata reference
- actor selection reason
- per-turn action chosen
- whether the action was accepted by the Game Engine
- action result
- optional actor diagnostics

Actor diagnostics must not expose hidden information to the opponent or public live viewers.

---

## 14. Performance Requirements

### 14.1 Inference Latency

The Actor must return an action within the configured turn timeout.

Recommended requirement:

- Local actor inference should normally complete in under 500 ms.
- If an actor cannot respond within the turn timeout, the Game Orchestrator handles timeout behavior according to protocol rules.

### 14.2 Model Selection Latency

Actor selection from the Model Bank should be fast enough to run at sub-game start.

Recommended requirement:

- Exact or fallback actor selection should normally complete in under 1 second.

### 14.3 Training Latency

Training is not part of the normal turn loop.

If match-start training is enabled, it must obey the configured training-time budget and must not block unrelated server activity.

---

## 15. Fallback Actor Requirements

The system must include at least one safe fallback actor for each role.

Fallback actor types may include:

- Rule-based Cop Actor.
- Rule-based Thief Actor.
- Random visible-action actor.
- Conservative survival actor.
- Conservative chase actor.

Fallback actors must:

- Return actions in the expected action schema.
- Avoid intentionally illegal actions when visible information is sufficient.
- Respect role restrictions.
- Be deterministic when seeded.
- Be clearly marked as fallback in logs.

---

## 16. Public API Requirements

The Actor system should expose an internal API to the Game Orchestrator.

Required operations:

```python
select_actor(role, config, rules_signature) -> ActorSelection
get_action(actor_id, observation) -> Action
on_result(actor_id, observation, action, result) -> None
list_models(role=None, rules_signature=None) -> List[ModelMetadata]
register_model(model_metadata, artifact_ref) -> RegistrationResult
```

The Actor API is internal. External REST or MCP clients must not call actor internals directly unless explicitly exposed for debugging or administration.

---

## 17. Acceptance Criteria

The Actor system is acceptable when:

- A Cop Actor can be selected for every supported Cop configuration or a clear fallback/failure is produced.
- A Thief Actor can be selected for every supported Thief configuration or a clear fallback/failure is produced.
- Model Bank selection is deterministic and logged.
- Actors never receive hidden state under partial observation.
- Actors return exactly one intended action per turn.
- Game Engine validation remains authoritative.
- Actors support the fixed rule set, including configurable movement, STAY, barriers, partial observation, crumbtrails, move order, and role alternation.
- A full 6-sub-game series can run with selected Cop and Thief actors.
- Replay logs include enough actor metadata to identify which model produced each action.
- Missing exact models do not crash the system if fallback is enabled.
- Training failure does not corrupt the Model Bank.

---

## 18. Open Product Decisions

The following decisions must be resolved before final implementation planning:

1. Which actor types are required for MVP: trained only, heuristic only, or both?
2. Should match-start training be allowed, or should all trained models be prepared offline?
3. What is the maximum acceptable training wait time during game setup?
4. What metrics decide whether a newly trained actor is good enough to register?
5. Should Cop and Thief be trained separately or through self-play pairs?
6. Should models be specialized by exact rules signature or generalized across rule families?
7. Should public replays reveal which actor model was used?
8. Should online learning during live games be forbidden for fairness/reproducibility?
