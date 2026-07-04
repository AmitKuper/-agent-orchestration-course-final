# Actor Development Plan — Cop/Thief Neural Actors and Model Bank

## 1. Purpose

This document defines the development plan for the Actor system of the Cop & Thief game.

The Actor system must support:

- A **Cop Actor**.
- A **Thief Actor**.
- Rule-aware action selection.
- Multiple actor backends.
- A Model Bank with general and specialized models.
- A fallback strategy when no trained model matches the active rules.
- Future training of neural actors that can play across many supported rule configurations.

This is an implementation plan, not the game-rules PRD.

---

## 2. Core Design Decision

Use **two general neural models** as the long-term target:

```text
cop_recurrent_ppo_general.pt
thief_recurrent_ppo_general.pt
```

Each model must be conditioned on:

1. The actor role.
2. The current board observation.
3. The active game rules/configuration.
4. The current turn/sub-game context.
5. An action mask that disables illegal actions.

The system should also support specialized models later:

```text
cop_tactical.pt
thief_tactical.pt
cop_aggressive.pt
thief_aggressive.pt
cop_full_observation.pt
thief_full_observation.pt
```

The Model Bank should select the best model available at game start.

---

## 3. Recommended Actor Types

The Actor system should support these actor backends:

| Actor Type | Purpose | Required for V1? |
|---|---|---:|
| `HeuristicActor` | Simple deterministic fallback | Yes |
| `RandomLegalActor` | Testing and sanity checks | Yes |
| `TabularQActor` | Tiny-grid experiments only | Optional |
| `DQNActor` | Simple neural baseline | Optional / V1.5 |
| `RecurrentDQNActor` | DQN with memory for partial observation | Optional |
| `RecurrentPPOActor` | Target production neural actor | Yes for final target |

Recommended development order:

```text
1. RandomLegalActor
2. HeuristicActor
3. ModelBank loader/selector
4. DQN or simple neural baseline
5. RecurrentPPOActor
6. Specialized model training pipeline
```

---

## 4. Why Recurrent PPO Is the Target

The game has properties that make plain tabular Q-learning or simple DQN insufficient as the final approach:

- Configurable rules.
- Partial observation.
- Hidden opponent position.
- Hidden barriers.
- Optional crumbtrails.
- Role switching.
- Self-play dynamics.
- Discrete but context-dependent action space.
- Need for a general model across multiple supported rule configurations.

A recurrent PPO actor is recommended because:

- PPO is generally stable for policy-gradient training.
- It directly learns an action policy.
- It works naturally with action masking.
- A recurrent memory layer can remember previous observations in partial-observation games.
- It is suitable for self-play training.

---

## 5. Actor Interface

All actors must implement a common interface.

```python
class BaseActor:
    def get_action(self, observation: ObservationState) -> Action:
        ...

    def on_result(self, observation: ObservationState, action: Action, result: ActionResult) -> None:
        ...
```

For neural actors, the interface should internally perform:

```text
ObservationState
→ FeatureEncoder
→ RuleConfigEncoder
→ NeuralPolicy
→ ActionMask
→ Selected Action
```

---

## 6. Observation Input

The actor receives only the information allowed by the active observation mode.

The actor input should include:

```json
{
  "role": "cop",
  "own_position": [3, 4],
  "visible_opponent_position": null,
  "visible_barriers": [[2, 4], [4, 4]],
  "visible_crumbtrails": [],
  "turn_index": 12,
  "thief_actions_used": 6,
  "barriers_remaining": 3,
  "subgame_index": 2,
  "rules": {
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
    "crumbtrail_mode": "both",
    "crumbtrail_max_age": 5
  },
  "action_mask": [true, true, false, true]
}
```

Important rule:

```text
Under partial observation, the actor must not receive hidden true state.
```

The actor may receive available **intended actions**, but not true legal actions if true legality would reveal hidden barriers.

---

## 7. Fixed Action Space

Use one fixed action space for all actor types.

```text
MOVE_N
MOVE_NE
MOVE_E
MOVE_SE
MOVE_S
MOVE_SW
MOVE_W
MOVE_NW
STAY
PLACE_BARRIER_CURRENT
PLACE_BARRIER_N
PLACE_BARRIER_NE
PLACE_BARRIER_E
PLACE_BARRIER_SE
PLACE_BARRIER_S
PLACE_BARRIER_SW
PLACE_BARRIER_W
PLACE_BARRIER_NW
FORFEIT
```

The game engine must provide an action mask for each actor turn.

Examples:

- If actor is Thief: mask out all `PLACE_BARRIER_*` actions.
- If `stay_enabled = false`: mask out `STAY`.
- If Cop has no barriers left: mask out all `PLACE_BARRIER_*` actions.
- If `barrier_placement_scope = adjacent_only`: mask out `PLACE_BARRIER_CURRENT`.
- If voluntary forfeit is disabled by UI/policy: mask out `FORFEIT`.

The neural actor must never select an action where `action_mask[action] = false`.

---

## 8. Model Bank Requirements

The Model Bank is responsible for storing, loading, and selecting actors.

### 8.1 Model Metadata

Each trained model must have metadata:

```json
{
  "model_id": "cop_recurrent_ppo_general_v1",
  "role": "cop",
  "algorithm": "recurrent_ppo",
  "rules_scope": "general",
  "supported_grid_sizes": [[5, 5], [8, 8], [10, 10]],
  "supported_observation_modes": ["full", "partial"],
  "supported_view_radii": [2, 3],
  "supported_crumbtrail_modes": ["none", "thief_only", "cop_only", "both"],
  "supported_move_orders": ["thief_first", "cop_first", "alternating"],
  "training_steps": 10000000,
  "created_at": "YYYY-MM-DD",
  "version": "1.0.0"
}
```

### 8.2 Selection Order

At game start, select actor model using this order:

```text
1. Exact specialized model for active rules and role.
2. Compatible specialized model.
3. General role model.
4. Heuristic role actor.
5. Random legal actor fallback.
6. Fail only if fallback actors are disabled.
```

Example:

```text
Active rules: 10x10, partial observation radius 2, crumbtrail none, role=cop

Try:
1. cop_10x10_partial_r2_crumbtrail_none.pt
2. cop_partial_r2_general.pt
3. cop_recurrent_ppo_general.pt
4. cop_heuristic
5. random_legal
```

---

## 9. Training Strategy

Do not train actors at game start.

Training should happen offline or in a dedicated training pipeline.

At game start, the server should only:

```text
1. Read active rules/config.
2. Select model from Model Bank.
3. Load actor.
4. Start game.
```

### 9.1 Rule-Conditioned Training

For the general Cop/Thief models, sample a different rule configuration at the start of each training episode.

Example:

```text
Episode 1: 5x5, full observation, no barriers
Episode 2: 5x5, partial observation radius 2, barriers enabled
Episode 3: 8x8, partial observation radius 3, crumbtrail both
Episode 4: 10x10, STAY disabled, adjacent-only barriers
```

This trains the model to react to both the board and the active rules.

### 9.2 Curriculum

Training should begin simple and gradually add complexity.

Recommended stages:

```text
Stage 1: 2x2 / 3x3, full observation, no barriers
Stage 2: 5x5, full observation, no barriers
Stage 3: 5x5, full observation, barriers enabled
Stage 4: 5x5, partial observation
Stage 5: 8x8 and 10x10, partial observation
Stage 6: crumbtrails enabled
Stage 7: randomized rule configurations
Stage 8: self-play with opponent pool
```

### 9.3 Opponent Pool

Do not train only against the latest version of the opponent model.

Maintain a pool of opponents:

```text
- random actor
- heuristic actor
- older Cop/Thief checkpoints
- current training opponent
- specialized actors if available
```

This reduces overfitting to one opponent behavior.

---

## 10. Reward Design

Reward design should be role-specific.

### 10.1 Cop Reward

Recommended Cop reward:

```text
+20.0  capture
+15.0  thief trapped
-10.0  thief survived
-0.05  per Cop action
-0.02  per Thief action survived
-1.0   invalid action selected before masking, if applicable
+small shaping reward for reducing distance to known/estimated thief position
```

Distance shaping must be used carefully under partial observation.

If the Thief is hidden, do not use hidden true Thief position for actor input. For reward shaping during training, hidden true state may be used only if the training design explicitly allows privileged critic/reward information.

### 10.2 Thief Reward

Recommended Thief reward:

```text
+10.0  survived max_moves
+15.0  cop trapped
-20.0  captured
+0.05  per Thief action survived
-1.0   invalid action selected before masking, if applicable
+small shaping reward for increasing distance from visible Cop
```

### 10.3 Avoid Over-Shaping

Do not make distance reward too strong. The final objective is winning, not only maximizing distance.

---

## 11. Neural Architecture

Recommended architecture for `RecurrentPPOActor`:

```text
Board Encoder
  - Multi-channel grid tensor
  - Channels: own position, visible opponent, visible barriers, crumbtrails, unknown/visible mask

Rule Encoder
  - MLP over normalized config values
  - Encodes grid size, max moves, barriers, observation mode, STAY, crumbtrail mode, move order

Context Encoder
  - Turn index, thief_actions_used, barriers_remaining, role

Fusion
  - Concatenate board embedding + rule embedding + context embedding

Memory
  - GRU or LSTM

Policy Head
  - logits over fixed action space
  - action mask applied before sampling/argmax

Value Head
  - scalar value estimate for PPO training
```

---

## 12. Training Environment

Implement a custom multi-agent RL environment around the game engine.

Recommended environment style:

```text
PettingZoo AEC-style environment
```

Reason:

```text
The game is sequential and turn-based: one actor acts, then the other actor acts.
```

The environment should expose:

```text
reset(config=None)
observe(agent)
step(action)
action_mask(agent)
rewards
terminations
truncations
infos
```

---

## 13. Evaluation Metrics

Every trained model must be evaluated before being added to the Model Bank.

Metrics:

```text
- Win rate as Cop
- Win rate as Thief
- Average score per 6-sub-game series
- Capture rate
- Survival rate
- Trapped rate
- Average Thief actions survived
- Illegal action rate before masking
- Timeout rate
- Performance by rule preset
- Performance under full observation
- Performance under partial observation
- Performance with/without crumbtrails
```

Evaluation opponents:

```text
- Random actor
- Heuristic actor
- Previous model version
- Specialized models
- General models
```

---

## 14. Inference Requirements

At runtime, actor inference must be fast enough for interactive play.

Requirements:

```text
- Actor decision should usually complete in less than 100 ms on server hardware.
- Actor must respect action mask.
- Actor must be deterministic when deterministic mode is enabled.
- Actor must support stochastic mode for training/evaluation.
- Actor must never access hidden state.
```

Inference modes:

```text
training: sample from policy distribution
competition: choose highest-probability valid action
debug: choose deterministic action and log logits/mask
```

---

## 15. Development Milestones

### Milestone 1 — Actor Interface and Fallbacks

Deliver:

```text
- BaseActor interface
- RandomLegalActor
- CopHeuristicActor
- ThiefHeuristicActor
- Action enum
- Action mask support
```

### Milestone 2 — Model Bank

Deliver:

```text
- Model metadata format
- Model registry
- Model selection logic
- Fallback selection logic
- Unit tests for selection
```

### Milestone 3 — RL Environment

Deliver:

```text
- PettingZoo-style environment wrapper
- Rule randomization support
- Observation encoding
- Action masking
- Reward calculation
```

### Milestone 4 — Neural Baseline

Deliver one of:

```text
- DQNActor baseline
- Simple PPOActor baseline
```

### Milestone 5 — Recurrent PPO

Deliver:

```text
- RecurrentPPOActor
- Training loop
- Checkpoint saving
- Evaluation reports
- Model Bank integration
```

### Milestone 6 — General Rule-Conditioned Models

Deliver:

```text
- cop_recurrent_ppo_general.pt
- thief_recurrent_ppo_general.pt
- Evaluation across official rule presets
- Fallback to heuristic if model unsupported
```

---

## 16. Acceptance Criteria

The Actor system is acceptable when:

```text
- Both Cop and Thief actors exist.
- Each actor can return valid actions for all supported official rule presets.
- The Actor does not access hidden state under partial observation.
- The Model Bank can select a model by role and rules.
- The system falls back safely when no model exists.
- Human vs server games can run using the actor system.
- Server vs server games can run using the actor system.
- Completed games can be replayed from logs.
- Neural actor checkpoints include metadata and versioning.
```

---

## 17. Non-Goals for First Version

Do not require these in the first working version:

```text
- Training at game start
- Perfect play
- One model that supports mathematically infinite configurations
- Transformer-based memory
- Distributed large-scale self-play
- GPU requirement for inference
```

---

## 18. Final Recommendation

Build the actor system so it can start simple but grow into neural self-play:

```text
V1: Heuristic Cop + Heuristic Thief + Model Bank interface
V2: DQN/PPO baseline
V3: Rule-conditioned Recurrent PPO Cop/Thief models
V4: Specialized models for popular presets
```

Do not train at match startup. Train offline, then load the best model at game start.
