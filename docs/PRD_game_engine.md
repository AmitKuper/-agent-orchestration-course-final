# PRD — Game Engine: Cops-and-Robbers Pursuit Game

> **Updated engine PRD.** This document updates the earlier `PRD_game_engine.md` so the engine supports the expanded and clarified Cops-and-Robbers rules.
>
> This PRD is the authoritative implementation specification for the game engine: configuration, state machine, action validation, partial observation, crumbtrails, barriers, win detection, scoring, logging, replay, and state synchronization.

---

## Overview

The game engine implements a deterministic, configurable, turn-based pursuit game on a 2D grid.

Two roles participate in every sub-game:

- **Cop**: attempts to capture or trap the Thief.
- **Thief**: attempts to survive until the move limit or trap the Cop.

A match is a series of exactly **6 valid sub-games**. Each human player plays exactly **3 sub-games as Cop** and **3 sub-games as Thief**. Technical-invalid sub-games are not scored and must be replayed until 6 valid sub-games are completed.

### Key Design Principles

- **No hard-coded rules**: grid size, move order, STAY, barriers, observation, crumbtrails, scoring, and limits are loaded from `config.json` or match setup.
- **Deterministic state machine**: given the same config, seed, initial state, and action sequence, both engines reach the same state.
- **No central referee required**: both engines independently validate actions and compare state hashes.
- **Observation safety**: under partial observation, hidden state must not leak to the actor through true legal-move lists or detailed failure reasons.
- **Implementation clarity**: invalid actions, voluntary forfeit, technical failures, and trapped conditions are separate concepts.

---

## 1. Core Game Model

### 1.1 Sub-Game

A **sub-game** is one complete pursuit game on a single grid.

A sub-game begins with:

1. A configured rectangular grid.
2. One Cop position.
3. One Thief position.
4. No placed barriers.
5. All counters reset.
6. Optional crumbtrail state reset.

A sub-game ends immediately when a win condition is met.

### 1.2 Match / Series

A **match** is a sequence of exactly `num_games` valid sub-games.

Default:

```json
"num_games": 6
```

For the default 6-game match:

- each player plays Cop 3 times;
- each player plays Thief 3 times;
- scores accumulate across all valid sub-games.

### 1.3 Technical Invalid Sub-Games

A sub-game is marked **technical_invalid** if it cannot be completed because of a non-gameplay failure, for example:

- engine crash;
- network failure;
- timeout policy failure;
- corrupted state;
- state-hash divergence;
- unrecoverable invalid protocol message.

A technical-invalid sub-game:

- does not count toward the required valid sub-games;
- awards no score;
- must be replayed using the same match configuration;
- may use a deterministic replay seed policy defined in Section 5.5.

A technical-invalid game is **not** a Cop win and **not** a Thief win.

---

## 2. Coordinate System and Grid

### 2.1 Coordinate Convention

The canonical engine coordinate system is:

- coordinate format: `[col, row]`;
- 0-indexed;
- `(0, 0)` is the **bottom-left** cell;
- column increases to the right;
- row increases upward.

For a grid `[cols, rows]`:

- valid columns are `0 <= col < cols`;
- valid rows are `0 <= row < rows`.

Example 5×5 grid:

```text
row
 4  .  .  .  .  .
 3  .  .  .  .  T
 2  .  .  C  .  .
 1  .  .  .  .  .
 0  .  .  .  .  .
    0  1  2  3  4   col
```

The UI may render rows top-down, but logs, hashes, config, and engine APIs must use the canonical bottom-left coordinate system.

### 2.2 Grid Size

The grid is rectangular and configurable.

Default:

```json
"grid_size": [10, 10]
```

Validation:

- `cols >= 2`;
- `rows >= 2`.

### 2.3 Starting Positions

Starting positions are controlled by `starting_position_mode`.

| Mode | Meaning |
|---|---|
| `random` | Engine deterministically samples distinct valid starting cells using the agreed seed. |
| `fixed` | Config provides explicit Cop and Thief starting positions for each sub-game. |

Starting positions must be:

- inside the grid;
- distinct from each other;
- not occupied by barriers, since barriers are empty at initialization.

---

## 3. Roles and Match Structure

### 3.1 Role Schedule

The engine must maintain a role schedule assigning each human player to Cop or Thief for each valid sub-game.

Default 6-game schedule:

| Sub-game | Player A Role | Player B Role |
|---:|---|---|
| 1 | Cop | Thief |
| 2 | Thief | Cop |
| 3 | Cop | Thief |
| 4 | Thief | Cop |
| 5 | Cop | Thief |
| 6 | Thief | Cop |

`Player A` is the initiator by default unless explicitly configured otherwise.

A custom schedule is allowed only if:

- `num_games = 6`, or scoring expectations are explicitly updated;
- each player receives exactly 3 Cop games and 3 Thief games.

### 3.2 Sub-Game Count

A match ends after exactly `num_games` valid sub-games.

Technical-invalid games are replayed and do not increment the valid sub-game counter.

### 3.3 Score Ownership

Scores are awarded to the human player currently occupying each role in the sub-game.

Example:

- If Player A is Cop and Cop wins, Player A receives `scoring.cop_win`.
- If Player B is Thief and Cop wins, Player B receives `scoring.thief_loss`.

---

## 4. Actions and Turn Semantics

### 4.1 Action Types

The acting role submits exactly one intended action per turn.

| Actor | Action | Description |
|---|---|---|
| Cop | `move` | Move one step to an adjacent cell. |
| Cop | `stay` | Stay in current cell, if enabled. |
| Cop | `barrier` | Place a barrier, if legal. |
| Cop | `forfeit` | Voluntarily lose the sub-game. |
| Thief | `move` | Move one step to an adjacent cell. |
| Thief | `stay` | Stay in current cell, if enabled. |
| Thief | `forfeit` | Voluntarily lose the sub-game. |

Only the Cop may use `barrier`.

### 4.2 Mandatory Message + Action Protocol

If the communication protocol requires role-play messages, each turn must include:

1. one free-text message; and
2. one action payload.

The message is logged but has no direct effect on the game state.

A missing message, missing action, malformed action, or unparseable payload is a **protocol invalid submission**, not an in-game movement failure.

### 4.3 Consumed vs Rejected Actions

The engine must distinguish **consumed actions** from **rejected invalid actions**.

A consumed action:

- changes the state, or intentionally leaves the actor in place;
- increments `turn_counter`;
- increments `thief_actions_completed` if the actor is Thief;
- updates crumbtrails;
- triggers win-condition checks.

A rejected invalid action:

- does not change the state;
- does not increment counters;
- does not update crumbtrails;
- does not trigger win-condition checks;
- returns control to the same actor to submit another action, subject to protocol retry policy.

### 4.4 Voluntary Forfeit

`forfeit` is a legal explicit action that immediately ends the sub-game.

| Actor Forfeits | Winner | Win Reason |
|---|---|---|
| Cop | Thief | `cop_forfeit` |
| Thief | Cop | `thief_forfeit` |

Forfeit must not be used to mean “stay in place.”

---

## 5. Configuration

### 5.1 Required Config Parameters

All game parameters must be read from `config.json` or agreed match setup.

| Parameter | Type | Default | Description |
|---|---:|---:|---|
| `grid_size` | `[int, int]` | `[10, 10]` | Grid dimensions `[cols, rows]`. |
| `num_games` | `int` | `6` | Number of valid sub-games in a match. |
| `max_moves` | `int` | `25` | Maximum consumed Thief actions before Thief survival win. |
| `max_barriers` | `int` | `5` | Maximum barriers Cop may place per sub-game. |
| `view_radius` | `int` or `"inf"` | `2` | Chebyshev radius for partial observation. |
| `partial_observation` | `bool` | `true` | Whether hidden information is enabled. |
| `stay_enabled` | `bool` | `true` | Whether both players may use STAY. |
| `out_of_bounds_behavior` | `enum` | `"stay"` | `"stay"` or `"invalid"`. |
| `barrier_collision_behavior` | `enum` | `"stay"` | `"stay"` or `"invalid"`. |
| `barrier_placement_scope` | `enum` | `"adjacent_only"` | `"adjacent_only"` or `"current_and_adjacent"`. |
| `starting_position_mode` | `enum` | `"random"` | `"random"` or `"fixed"`. |
| `move_order` | `enum` | `"thief_first"` | `"thief_first"`, `"cop_first"`, or `"alternating"`. |
| `crumbtrail_mode` | `enum` | `"none"` | `"none"`, `"thief_only"`, `"cop_only"`, or `"both"`. |
| `crumbtrail_max_age` | `int` | `-1` | `-1` for permanent trail, otherwise non-negative max age. |
| `turn_timeout_seconds` | `int` | `30` | Wall-clock timeout per actor submission. |
| `max_illegal_retries` | `int` | `2` | Re-prompts after invalid protocol/action submission. |
| `max_consecutive_technical_invalid` | `int` | `3` | Abort match after repeated technical-invalid sub-games. |

### 5.2 Scoring Config

| Parameter | Default | Meaning |
|---|---:|---|
| `scoring.cop_win` | `20` | Cop score on Cop victory. |
| `scoring.thief_win` | `10` | Thief score on Thief victory. |
| `scoring.cop_loss` | `5` | Cop score on Cop loss. |
| `scoring.thief_loss` | `5` | Thief score on Thief loss. |

### 5.3 Optional Match Setup Parameters

The following may be negotiated during match setup:

| Parameter | Description |
|---|---|
| `match_id` | Unique identifier for the match. |
| `random_seed` | Base seed for deterministic random start positions. |
| `player_a_id` | Human/player identifier for Player A. |
| `player_b_id` | Human/player identifier for Player B. |
| `role_schedule` | Explicit 6-sub-game role schedule. |
| `fixed_start_positions` | Required if `starting_position_mode = "fixed"`. |
| `mechanics_overrides` | Optional per-match overrides to config values. |

### 5.4 Config Validation

Before a match starts, validate:

- `grid_size[0] >= 2` and `grid_size[1] >= 2`;
- `num_games = 6` unless role/scoring assumptions are deliberately changed;
- `max_moves >= 1`;
- `max_barriers >= 0`;
- `view_radius >= 1` or `view_radius = "inf"`;
- if `partial_observation = false`, ignore `view_radius` for visibility;
- `out_of_bounds_behavior in {"stay", "invalid"}`;
- `barrier_collision_behavior in {"stay", "invalid"}`;
- `barrier_placement_scope in {"adjacent_only", "current_and_adjacent"}`;
- `starting_position_mode in {"random", "fixed"}`;
- `move_order in {"thief_first", "cop_first", "alternating"}`;
- `crumbtrail_mode in {"none", "thief_only", "cop_only", "both"}`;
- `crumbtrail_max_age = -1` or `crumbtrail_max_age >= 0`;
- all scoring values are non-negative integers;
- each player appears exactly 3 times as Cop and 3 times as Thief in a default 6-game schedule.

### 5.5 Seed Policy

The deterministic seed for sub-game `i` should be derived from the agreed match seed and the valid sub-game index.

Recommended:

```text
subgame_seed = SHA256(match_id || random_seed || valid_subgame_index || replay_attempt_index)
```

If a sub-game is technical-invalid and replayed, use one of these policies and record it in logs:

| Policy | Description |
|---|---|
| `same_seed_replay` | Replay with the same sub-game seed. Best for debugging. |
| `new_replay_seed` | Include `replay_attempt_index` in seed derivation. Best for avoiding repeated unlucky technical failures. |

Default recommendation: `same_seed_replay` for deterministic auditability.

---

## 6. Movement Rules

### 6.1 Movement Directions

A `move` action targets one of the 8 adjacent cells:

| Direction | Delta `[dc, dr]` |
|---|---:|
| `N` | `[0, 1]` |
| `NE` | `[1, 1]` |
| `E` | `[1, 0]` |
| `SE` | `[1, -1]` |
| `S` | `[0, -1]` |
| `SW` | `[-1, -1]` |
| `W` | `[-1, 0]` |
| `NW` | `[-1, 1]` |

A movement changes the actor position by at most one column and at most one row.

### 6.2 Legal Movement

A movement is legal if:

1. the target follows one of the 8 direction deltas;
2. the target is inside the grid;
3. the target does not contain a barrier;
4. the target satisfies the opponent-position rules.

### 6.3 Opponent-Position Rules

Cop and Thief collision rules are asymmetric.

#### Cop entering the Thief's cell

The Cop may move into the Thief's current cell. This causes immediate capture.

Result:

```json
{ "winner": "cop", "win_reason": "capture" }
```

#### Thief entering the Cop's cell

The Thief may not move into the Cop's current cell.

If attempted, the action is treated as invalid. It does not produce capture, escape, or automatic loss.

### 6.4 Position Swapping

There is no simultaneous movement. Movement is validated against the true current state at the moment the action executes.

Therefore:

- the Cop captures only by entering the Thief's current cell;
- the Thief cannot enter the Cop's current cell;
- either player may enter a cell the opponent previously occupied if the opponent has already left it and the cell is otherwise legal.

### 6.5 Out-of-Bounds Movement Attempts

Behavior is controlled by `out_of_bounds_behavior`.

| Value | Engine Result |
|---|---|
| `stay` | Action consumes the turn; actor remains in place; result is generic `move_failed`. |
| `invalid` | Action is rejected; no state/counter changes; actor must resubmit. |

Out-of-bounds movement never directly causes loss.

### 6.6 Barrier-Collision Movement Attempts

Behavior is controlled by `barrier_collision_behavior`.

| Value | Engine Result |
|---|---|
| `stay` | Action consumes the turn; actor remains in place; result is generic `move_failed`. |
| `invalid` | Action is rejected; no state/counter changes; actor must resubmit. |

Moving into a barrier never directly causes loss.

### 6.7 STAY Action

If `stay_enabled = true`, `stay` is legal for both actors.

A STAY action:

- consumes the turn;
- keeps the actor in the same cell;
- increments counters normally;
- updates crumbtrails normally;
- can trigger win-condition checks after the action.

If `stay_enabled = false`, STAY is rejected as invalid.

---

## 7. Barrier Mechanics

### 7.1 Barrier Overview

Barriers are permanent blocked cells placed by the Cop.

Rules:

- only the Cop may place barriers;
- barrier placement is a complete Cop action;
- the Cop does not move when placing a barrier;
- barriers remain until the sub-game ends;
- barriers block entry into their cell for both players;
- barriers do not automatically cause loss.

### 7.2 Barrier Limit

The Cop may place at most `max_barriers` barriers in a sub-game.

If `max_barriers = 0`, barrier placement is disabled.

### 7.3 Barrier Placement Scope

Controlled by `barrier_placement_scope`.

| Value | Allowed Target Cells |
|---|---|
| `adjacent_only` | One of the 8 cells adjacent to the Cop. |
| `current_and_adjacent` | One of the 8 adjacent cells or the Cop's current cell. |

Default:

```json
"barrier_placement_scope": "adjacent_only"
```

### 7.4 Barrier Placement Validation

A barrier action is legal if:

1. actor is Cop;
2. `barriers_placed < max_barriers`;
3. target cell is inside the grid;
4. target cell does not already contain a barrier;
5. target cell is not the Thief's current cell;
6. target cell is allowed by `barrier_placement_scope`.

### 7.5 Barrier on Cop's Current Cell

This is legal only when `barrier_placement_scope = "current_and_adjacent"`.

If the Cop places a barrier on his own current cell:

- the Cop remains on that cell for the current turn;
- the barrier blocks future entry into that cell;
- the barrier does not prevent the Cop from leaving the cell on a later turn;
- once the Cop leaves, neither player may move into that cell again;
- if STAY is enabled, the Cop may continue staying on that barrier cell;
- if STAY is disabled and all exits are blocked, the Cop may become trapped unless another barrier action is legal.

### 7.6 Barrier Visibility

Under partial observation:

- barriers inside the actor's view radius are visible;
- barriers outside the actor's view radius are hidden;
- hidden barriers still block movement;
- failed movement into hidden barriers must be reported generically.

Under full observation:

- all barriers are visible to both players.

---

## 8. Turn Order and Counters

### 8.1 Move Order

Controlled by `move_order`.

| Value | Round Order |
|---|---|
| `thief_first` | Thief, then Cop every round. |
| `cop_first` | Cop, then Thief every round. |
| `alternating` | Odd rounds: Thief→Cop. Even rounds: Cop→Thief. |

### 8.2 Round Definition

A **round** is a scheduled pair of turns where each actor is scheduled once.

A round can end early if a win condition is met after the first actor's action.

### 8.3 Counters

The true state must track:

| Counter | Meaning |
|---|---|
| `turn_counter` | Number of consumed actions by either actor. |
| `thief_actions_completed` | Number of consumed Thief actions; used for `max_moves`. |
| `round_index` | Current scheduled round, starting from 1. |
| `actor_turn_index_in_round` | `0` or `1`, indicating first or second scheduled actor in the round. |

Rejected invalid actions do not increment counters.

### 8.4 Meaning of `max_moves`

`max_moves` means the maximum number of **consumed Thief actions**.

A Thief action counts if it consumes the turn, including:

- successful movement;
- STAY;
- failed movement that becomes STAY due to `out_of_bounds_behavior = "stay"`;
- failed movement that becomes STAY due to `barrier_collision_behavior = "stay"`.

Rejected invalid actions do not count.

### 8.5 Survival Timing

The Thief wins by survival immediately after completing the `max_moves`-th consumed Thief action, unless an earlier win condition in the same check already ended the game.

The Cop does not receive an extra final turn after the Thief reaches `max_moves`.

---

## 9. Trapped Condition

A player is **trapped** if the player has no legal action that can consume a turn and keep the sub-game continuing.

### 9.1 Thief Trapped

The Thief is trapped if:

1. the Thief has no legal movement action;
2. STAY is disabled or otherwise not legal;
3. the Thief has not voluntarily forfeited.

If true, Cop wins with:

```json
{ "winner": "cop", "win_reason": "thief_trapped" }
```

If `stay_enabled = true`, the Thief is usually not trapped because STAY is legal.

### 9.2 Cop Trapped

The Cop is trapped if:

1. the Cop has no legal movement action;
2. STAY is disabled or otherwise not legal;
3. the Cop has no legal barrier-placement action;
4. the Cop has not voluntarily forfeited.

If true, Thief wins with:

```json
{ "winner": "thief", "win_reason": "cop_trapped" }
```

If `stay_enabled = true`, the Cop is usually not trapped because STAY is legal.

### 9.3 Trap Check Timing

After every consumed action, the engine checks whether the opponent is trapped.

Invalid rejected actions do not trigger trap checks.

---

## 10. Win Conditions

### 10.1 Cop Wins

| Win Reason | Condition |
|---|---|
| `capture` | Cop moves into the Thief's current cell. |
| `thief_trapped` | Thief has no legal action after the Cop's consumed action. |
| `thief_forfeit` | Thief voluntarily forfeits. |

### 10.2 Thief Wins

| Win Reason | Condition |
|---|---|
| `thief_survived` | Thief completes `max_moves` consumed actions without prior capture. |
| `cop_trapped` | Cop has no legal action after the Thief's consumed action. |
| `cop_forfeit` | Cop voluntarily forfeits. |

### 10.3 Win Detection Order

After each consumed action, evaluate in this order:

1. **Voluntary forfeit**: if actor forfeited, opponent wins.
2. **Capture**: if Cop moved into Thief's current cell, Cop wins.
3. **Opponent trapped**: if opponent has no legal action, actor wins.
4. **Thief survival**: if actor is Thief and `thief_actions_completed >= max_moves`, Thief wins.

Invalid rejected actions do not trigger win checks.

---

## 11. Partial Observation and Full Observation

### 11.1 Visibility Model

If `partial_observation = true`, each actor sees only cells within Chebyshev distance `view_radius` from its own position.

Chebyshev distance:

```text
max(abs(col1 - col2), abs(row1 - row2))
```

A cell is visible if distance is less than or equal to `view_radius`.

### 11.2 Visible Information Under Partial Observation

Each actor always sees:

- own position;
- own role;
- `turn_counter`;
- `thief_actions_completed`;
- `round_index`;
- game-over status;
- own remaining barriers if actor is Cop.

The actor sees only if within view radius:

- opponent position;
- barriers;
- crumbtrail markers.

### 11.3 Hidden Information Must Not Leak

Under partial observation, the actor must not receive the full true-state legal-action list.

The engine may provide **candidate actions** that are structurally possible from visible information, but the engine must validate final submitted actions against the true state.

Bad API behavior under partial observation:

```python
actor_legal_moves = engine.get_true_legal_actions(actor)
```

This leaks hidden barriers because blocked hidden cells disappear from the list.

Required behavior:

```python
observation = engine.get_observation(actor)
candidate_actions = engine.get_candidate_actions(actor, observation_safe=True)
result = engine.apply_action(actor, submitted_action)
```

### 11.4 Failure Messages Under Partial Observation

If movement fails due to a hidden barrier or hidden-state rule, the actor-facing result must be generic.

Allowed generic result:

```json
{ "status": "move_failed" }
```

Do not reveal:

```json
{ "status": "blocked_by_hidden_barrier" }
```

unless `partial_observation = false`.

### 11.5 Full Observation

If `partial_observation = false`:

- both actors see the full board;
- opponent positions are always visible;
- all barriers are visible;
- all enabled crumbtrails are visible;
- `view_radius` is ignored for visibility.

---

## 12. Crumbtrail Mechanics

### 12.1 Overview

A crumbtrail is an informational record of where a player has recently been.

Crumbtrails:

- are optional;
- do not block movement;
- are visible according to `crumbtrail_mode` and observation rules;
- are stored in true state for deterministic replay.

### 12.2 Crumbtrail Modes

| Value | Meaning |
|---|---|
| `none` | No crumbtrails visible. |
| `thief_only` | Cop can see Thief trail; Thief cannot see Cop trail. |
| `cop_only` | Thief can see Cop trail; Cop cannot see Thief trail. |
| `both` | Both players can see the opponent's trail. |

### 12.3 Marker Encoding

Thief markers:

| Marker | Meaning |
|---|---|
| `T` | Thief currently visible on this cell. |
| `1` | Thief was there 1 consumed Thief action ago. |
| `N` | Thief was there N consumed Thief actions ago. |

Cop markers:

| Marker | Meaning |
|---|---|
| `C` | Cop currently visible on this cell. |
| `1001` | Cop was there 1 consumed Cop action ago. |
| `1000 + N` | Cop was there N consumed Cop actions ago. |

Separate numeric ranges prevent ambiguity when both trails are visible.

### 12.4 Age Unit

Crumbtrail age is measured in the owning actor's consumed actions.

- Thief trail ages increase when Thief completes a consumed action.
- Cop trail ages increase when Cop completes a consumed action.
- STAY refreshes the current cell.
- Failed movement that consumes the turn refreshes the current cell.
- Rejected invalid actions do not update trails.

### 12.5 Persistence

Controlled by `crumbtrail_max_age`.

| Value | Meaning |
|---|---|
| `-1` | Trails never fade. |
| `0` | Only current visible position marker is shown; no history. |
| `N > 0` | Trail markers older than N consumed actions of the owner disappear. |

### 12.6 Visibility

Under partial observation, crumbtrail cells are visible only if within the viewer's view radius.

Under full observation, all enabled crumbtrails are visible.

---

## 13. State Representation

### 13.1 True State Schema

The engine must maintain this true state internally:

```json
{
  "game_id": "match-123-subgame-1-attempt-0",
  "match_id": "match-123",
  "valid_subgame_index": 1,
  "replay_attempt_index": 0,
  "grid_size": [10, 10],
  "cop_player_id": "player_a",
  "thief_player_id": "player_b",
  "cop_position": [2, 2],
  "thief_position": [8, 7],
  "barriers": [],
  "barriers_placed": 0,
  "turn_counter": 0,
  "thief_actions_completed": 0,
  "round_index": 1,
  "actor_turn_index_in_round": 0,
  "current_actor": "thief",
  "crumbtrail_state": {
    "cop": {},
    "thief": {}
  },
  "game_over": false,
  "winner": null,
  "win_reason": null
}
```

### 13.2 Observation State Schema

Actor-facing observation must be derived from true state.

Example partial-observation schema:

```json
{
  "actor": "thief",
  "own_position": [8, 7],
  "opponent_position": null,
  "opponent_visible": false,
  "visible_barriers": [[7, 7]],
  "visible_crumbtrails": {
    "cop": [[6, 6, 1002]],
    "thief": []
  },
  "turn_counter": 4,
  "thief_actions_completed": 2,
  "round_index": 3,
  "barriers_remaining_if_cop": null,
  "candidate_actions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "stay", "forfeit"]
}
```

Important: `candidate_actions` is not guaranteed to be true-state legal under partial observation.

### 13.3 Hashable State

For state synchronization, hash only canonical true-state fields that affect gameplay:

- grid size;
- role assignment;
- positions;
- barriers;
- counters;
- current actor / round index;
- crumbtrail state;
- game-over state;
- winner / win reason.

Do not include actor-facing observations, UI rendering, free-text messages, timestamps, or local retry counters in the gameplay hash.

---

## 14. Action Validation and Application

### 14.1 Validation Pipeline

For every submitted action:

```text
1. Parse action payload.
2. Validate actor turn ownership.
3. Validate action type is allowed for actor.
4. Validate action-specific parameters.
5. Classify result:
   - consumed_success
   - consumed_failure_stay
   - rejected_invalid
   - terminal_forfeit
6. If consumed/terminal, apply state transition.
7. Update counters and crumbtrails if consumed.
8. Run win-condition checks.
9. Log result.
10. Compute state hash.
```

### 14.2 Action Result Types

| Result Type | Consumes Turn | State Changes | Win Check | Example |
|---|---:|---:|---:|---|
| `consumed_success` | Yes | Yes | Yes | legal move, legal barrier, STAY |
| `consumed_failure_stay` | Yes | Actor remains in place | Yes | OOB with behavior `stay` |
| `rejected_invalid` | No | No | No | OOB with behavior `invalid` |
| `terminal_forfeit` | Yes | Game ends | Yes | actor action `forfeit` |

### 14.3 Invalid Action Retry Policy

Protocol invalid submissions and `rejected_invalid` actions may be retried up to `max_illegal_retries`.

After retries are exhausted, use one configured policy:

| Policy | Description |
|---|---|
| `technical_invalid` | Mark sub-game technical-invalid. Recommended default. |
| `auto_forfeit` | Submit a forced `forfeit` for the actor. This causes gameplay loss. |

Recommended default:

```json
"invalid_action_exhaustion_policy": "technical_invalid"
```

Rationale: because `forfeit` now means voluntary loss, the engine should not silently convert parse errors into a gameplay forfeit unless the project explicitly wants that behavior.

### 14.4 Timeout Policy

A per-turn timeout is a protocol failure, not a movement rule.

Recommended default:

```json
"timeout_policy": "technical_invalid"
```

Optional alternative:

```json
"timeout_policy": "auto_forfeit"
```

The selected timeout policy must be logged at match setup.

---

## 15. Game Loop

### 15.1 Match Initialization

```text
1. Load config.json.
2. Apply agreed match setup overrides.
3. Validate configuration.
4. Create role schedule.
5. Initialize player scores to 0.
6. Initialize valid_subgame_index = 1.
7. Initialize technical_invalid_count = 0.
```

### 15.2 Sub-Game Initialization

```text
1. Assign Cop and Thief from role schedule.
2. Derive sub-game seed.
3. Create empty grid.
4. Generate or load starting positions.
5. Validate starting positions.
6. Set barriers = empty set.
7. Set counters to zero.
8. Initialize crumbtrail state.
9. Set round_index = 1.
10. Determine first actor from move_order.
11. Log initial state.
```

### 15.3 Per-Turn Loop

```text
while not game_over:
    actor = current_actor
    observation = get_observation(actor)
    submission = receive_action(actor, observation)

    result = validate_and_apply(actor, submission)

    if result == rejected_invalid:
        handle_retry_or_policy(actor)
        continue

    if result consumes turn:
        update_counters(actor)
        update_crumbtrails(actor)
        check_win_conditions()
        log_turn()
        compute_and_exchange_state_hash()

    if hash_mismatch:
        mark_technical_invalid()
        break

    if not game_over:
        advance_turn_order()
```

### 15.4 Advancing Turn Order

For each round, compute the scheduled actor pair:

```python
def actors_for_round(round_index: int, move_order: str) -> list[str]:
    if move_order == "thief_first":
        return ["thief", "cop"]
    if move_order == "cop_first":
        return ["cop", "thief"]
    if move_order == "alternating":
        return ["thief", "cop"] if round_index % 2 == 1 else ["cop", "thief"]
    raise ConfigError("invalid move_order")
```

After the first actor in a round completes a consumed action and the game is not over, set current actor to the second actor.

After the second actor completes a consumed action and the game is not over:

- increment `round_index`;
- set `actor_turn_index_in_round = 0`;
- compute the first actor for the new round.

### 15.5 End of Sub-Game

If gameplay ended normally:

1. record `winner` and `win_reason`;
2. compute role-based scores;
3. assign points to human players;
4. write terminal log entry;
5. increment valid sub-game index.

If technical-invalid:

1. write technical-invalid terminal entry;
2. do not award points;
3. do not increment valid sub-game index;
4. replay or abort based on technical-invalid policy.

---

## 16. Scoring

### 16.1 Per-Sub-Game Scoring

| Winner | Win Reasons | Cop Score | Thief Score |
|---|---|---:|---:|
| Cop | `capture`, `thief_trapped`, `thief_forfeit` | `20` | `5` |
| Thief | `thief_survived`, `cop_trapped`, `cop_forfeit` | `5` | `10` |

Use config values, not literals:

```json
{
  "scoring": {
    "cop_win": 20,
    "thief_win": 10,
    "cop_loss": 5,
    "thief_loss": 5
  }
}
```

### 16.2 Series Score

For each valid sub-game:

```text
human_player_score += score_for_that_player_current_role
```

Maximum possible score for a player in the default 6-game schedule:

```text
3 Cop wins × 20 + 3 Thief wins × 10 = 90
```

Minimum possible score:

```text
3 Cop losses × 5 + 3 Thief losses × 5 = 30
```

If final scores are equal, the match is a draw unless a separate tie-break rule is configured.

---

## 17. Logging and Replay

### 17.1 Log Format

Each sub-game must produce append-only JSON Lines logs.

Required log entry types:

- `match_setup`;
- `subgame_initial_state`;
- `turn_result`;
- `state_hash`;
- `terminal_result`;
- `technical_invalid_result`, if applicable.

### 17.2 Match Setup Entry

```json
{
  "entry_type": "match_setup",
  "match_id": "match-123",
  "config_hash": "sha256:...",
  "random_seed": 42,
  "num_games": 6,
  "role_schedule": [
    {"subgame": 1, "cop": "player_a", "thief": "player_b"},
    {"subgame": 2, "cop": "player_b", "thief": "player_a"}
  ],
  "coordinate_system": "bottom_left_col_row",
  "invalid_action_exhaustion_policy": "technical_invalid",
  "timeout_policy": "technical_invalid"
}
```

### 17.3 Initial State Entry

```json
{
  "entry_type": "subgame_initial_state",
  "game_id": "match-123-subgame-1-attempt-0",
  "valid_subgame_index": 1,
  "replay_attempt_index": 0,
  "grid_size": [10, 10],
  "max_moves": 25,
  "max_barriers": 5,
  "stay_enabled": true,
  "out_of_bounds_behavior": "stay",
  "barrier_collision_behavior": "stay",
  "barrier_placement_scope": "adjacent_only",
  "partial_observation": true,
  "view_radius": 2,
  "move_order": "thief_first",
  "crumbtrail_mode": "none",
  "crumbtrail_max_age": -1,
  "cop_player_id": "player_a",
  "thief_player_id": "player_b",
  "cop_start": [2, 2],
  "thief_start": [8, 7],
  "subgame_seed": "sha256:..."
}
```

### 17.4 Turn Result Entry

```json
{
  "entry_type": "turn_result",
  "turn_counter": 7,
  "round_index": 4,
  "actor_turn_index_in_round": 0,
  "actor": "thief",
  "player_id": "player_b",
  "message": "Trying to disappear behind the corner.",
  "submitted_action": {
    "type": "move",
    "direction": "NW"
  },
  "result_type": "consumed_success",
  "public_result": "move_applied",
  "from": [8, 7],
  "to": [7, 8],
  "barrier_at": null,
  "state_after": {
    "cop_position": [2, 2],
    "thief_position": [7, 8],
    "barriers": [],
    "barriers_placed": 0,
    "thief_actions_completed": 4,
    "game_over": false,
    "winner": null,
    "win_reason": null
  }
}
```

### 17.5 Barrier Entry Example

```json
{
  "entry_type": "turn_result",
  "turn_counter": 8,
  "round_index": 4,
  "actor_turn_index_in_round": 1,
  "actor": "cop",
  "player_id": "player_a",
  "message": "Blocking the escape route.",
  "submitted_action": {
    "type": "barrier",
    "target": [3, 2]
  },
  "result_type": "consumed_success",
  "public_result": "barrier_placed",
  "from": [2, 2],
  "to": [2, 2],
  "barrier_at": [3, 2],
  "state_after": {
    "cop_position": [2, 2],
    "thief_position": [7, 8],
    "barriers": [[3, 2]],
    "barriers_placed": 1,
    "thief_actions_completed": 4,
    "game_over": false,
    "winner": null,
    "win_reason": null
  }
}
```

### 17.6 Failed-Move-Stay Entry Example

```json
{
  "entry_type": "turn_result",
  "turn_counter": 9,
  "round_index": 5,
  "actor": "thief",
  "submitted_action": {
    "type": "move",
    "direction": "N"
  },
  "result_type": "consumed_failure_stay",
  "public_result": "move_failed",
  "private_engine_reason": "out_of_bounds",
  "from": [7, 9],
  "to": [7, 9],
  "state_after": {
    "thief_position": [7, 9],
    "thief_actions_completed": 5
  }
}
```

`private_engine_reason` may appear in full audit logs, but must not be sent to the actor under partial observation if it would reveal hidden information.

### 17.7 Terminal Entry

```json
{
  "entry_type": "terminal_result",
  "game_id": "match-123-subgame-1-attempt-0",
  "winner": "cop",
  "win_reason": "capture",
  "turn_counter": 18,
  "round_index": 9,
  "thief_actions_completed": 9,
  "barriers_placed": 2,
  "cop_score": 20,
  "thief_score": 5,
  "player_scores_awarded": {
    "player_a": 20,
    "player_b": 5
  },
  "final_state": {
    "cop_position": [7, 8],
    "thief_position": [7, 8],
    "barriers": [[3, 2], [4, 4]]
  }
}
```

### 17.8 Technical Invalid Entry

```json
{
  "entry_type": "technical_invalid_result",
  "game_id": "match-123-subgame-2-attempt-0",
  "reason": "state_hash_mismatch",
  "turn_counter": 11,
  "scores_awarded": false,
  "replay_required": true
}
```

### 17.9 Replay Requirements

Replay must be able to:

- reconstruct initial state;
- apply each consumed action in order;
- reject invalid actions consistently;
- recompute crumbtrails;
- recompute hashes;
- reproduce terminal winner and scores.

---

## 18. State Synchronization

### 18.1 Deterministic State Machine

Both engines must apply identical rules:

- same coordinate system;
- same config;
- same random seed policy;
- same role schedule;
- same action sequence;
- same win detection order;
- same crumbtrail update logic.

### 18.2 State Hash

After each consumed action, compute a canonical state hash.

Recommended canonicalization:

```text
SHA256(JSON.stringify(canonical_state, sort_keys=True, no_whitespace=True))
```

Canonical state must sort unordered collections such as barriers and crumbtrail entries.

### 18.3 Hash Exchange

After each consumed action:

1. local engine computes state hash;
2. local engine sends hash to peer;
3. peer sends its hash;
4. if hashes match, continue;
5. if hashes differ, mark sub-game technical-invalid.

### 18.4 Hash Exclusions

Do not include:

- free-text messages;
- actor-facing observations;
- local timestamps;
- retry counters;
- UI-only fields;
- network metadata.

---

## 19. API

### 19.1 Engine Initialization

```python
engine = GameEngine(config: dict, match_setup: dict)
engine.initialize_match()
engine.initialize_subgame(valid_subgame_index: int, replay_attempt_index: int = 0)
```

### 19.2 State Queries

```python
true_state = engine.get_true_state()  # Engine/internal use only.
observation = engine.get_observation(actor="cop" | "thief")
state_hash = engine.compute_state_hash()
```

### 19.3 Action Helpers

```python
candidate_actions = engine.get_candidate_actions(actor: str, observation_safe: bool = True)
true_legal_actions = engine.get_true_legal_actions(actor: str)  # Internal/trap checks only.
```

Rules:

- `get_candidate_actions(..., observation_safe=True)` may be exposed to actors.
- `get_true_legal_actions(...)` must not be exposed to actors under partial observation.

### 19.4 Action Submission

```python
result = engine.apply_action(
    actor="cop" | "thief",
    action={
        "type": "move" | "stay" | "barrier" | "forfeit",
        "direction": "N" | "NE" | "E" | "SE" | "S" | "SW" | "W" | "NW" | None,
        "target": [int, int] | None
    },
    message=str | None
)
```

Return schema:

```python
{
    "result_type": "consumed_success" | "consumed_failure_stay" | "rejected_invalid" | "terminal_forfeit",
    "public_result": str,
    "actor_message": str,
    "state_changed": bool,
    "turn_consumed": bool,
    "game_over": bool,
    "winner": "cop" | "thief" | None,
    "win_reason": str | None,
    "state_hash": str | None
}
```

### 19.5 Game/Match Queries

```python
engine.is_game_over() -> bool
engine.get_winner() -> tuple[str | None, str | None]
engine.get_role_schedule() -> list[dict]
engine.get_subgame_scores() -> dict
engine.get_match_scores() -> dict
engine.needs_replay() -> bool
```

---

## 20. Testing and Validation

### 20.1 Unit Tests

Required unit tests:

- coordinate validation using bottom-left convention;
- all 8 movement directions;
- Cop capture by entering Thief cell;
- Thief cannot enter Cop cell;
- movement into previously occupied cell after opponent leaves;
- out-of-bounds behavior `stay`;
- out-of-bounds behavior `invalid`;
- barrier collision behavior `stay`;
- barrier collision behavior `invalid`;
- STAY enabled/disabled;
- voluntary forfeit;
- barrier placement adjacent-only;
- barrier placement current-and-adjacent;
- barrier on Cop current cell semantics;
- max barrier limit;
- Thief trapped logic;
- Cop trapped logic;
- Thief survival after exactly `max_moves` consumed Thief actions;
- no extra Cop turn after survival;
- `thief_first`, `cop_first`, and `alternating` move order;
- crumbtrail aging, revisits, STAY refresh, and fade;
- partial-observation hiding of opponent, barriers, and crumbtrails;
- no true legal-action leakage under partial observation;
- state hash canonicalization.

### 20.2 Integration Tests

Required integration tests:

- full 6-valid-sub-game match;
- role schedule gives each player 3 Cop and 3 Thief games;
- scoring totals match role ownership;
- technical-invalid sub-game replay does not award points;
- state hash mismatch voids sub-game;
- timeout policy behavior;
- invalid-action retry behavior;
- replay from JSONL log exactly reproduces terminal state.

### 20.3 Sanity Test Stages

| Stage | Grid | Goal |
|---|---|---|
| 1 | 2×2 | Capture, invalid moves, counters. |
| 2 | 3×2 / 2×3 | Turn order, survival timing, trapping. |
| 3 | 4×3 / 3×4 | Barriers and partial observation. |
| 4 | 5×5 | Crumbtrails and hash/replay. |
| 5 | 10×10 | Full default gameplay. |

---

## 21. Implementation Notes

### 21.1 Avoid Old PRD Ambiguities

The previous PRD used several behaviors that are now changed:

| Old Behavior | Updated Behavior |
|---|---|
| `forfeit` meant stay in place after retries. | `forfeit` means voluntary loss. Protocol failures are technical-invalid by default. |
| `max_moves` meant rounds. | `max_moves` means consumed Thief actions. |
| Thief always moves first. | Move order is configurable. |
| Barrier placement only on Cop current cell. | Barrier placement scope is configurable. |
| Top-left coordinate origin. | Canonical engine origin is bottom-left. |
| Actor could receive legal moves. | Under partial observation, actor receives observation-safe candidate actions only. |
| Capture if both occupy same cell at any point. | Only Cop may enter Thief cell; Thief cannot enter Cop cell. |

### 21.2 Recommended Default Configuration

```json
{
  "grid_size": [10, 10],
  "num_games": 6,
  "max_moves": 25,
  "max_barriers": 5,
  "partial_observation": true,
  "view_radius": 2,
  "stay_enabled": true,
  "out_of_bounds_behavior": "stay",
  "barrier_collision_behavior": "stay",
  "barrier_placement_scope": "adjacent_only",
  "starting_position_mode": "random",
  "move_order": "thief_first",
  "crumbtrail_mode": "none",
  "crumbtrail_max_age": -1,
  "turn_timeout_seconds": 30,
  "max_illegal_retries": 2,
  "invalid_action_exhaustion_policy": "technical_invalid",
  "timeout_policy": "technical_invalid",
  "max_consecutive_technical_invalid": 3,
  "scoring": {
    "cop_win": 20,
    "thief_win": 10,
    "cop_loss": 5,
    "thief_loss": 5
  }
}
```

---

## 22. Acceptance Criteria

The updated engine is complete when:

- it can run 6 valid sub-games with correct role alternation;
- it supports all config parameters listed in Section 5;
- it applies capture, trapped, survival, and forfeit wins exactly as specified;
- it distinguishes rejected invalid actions from consumed failed-STAY actions;
- it prevents hidden-state leakage under partial observation;
- it logs enough information for deterministic replay;
- it uses bottom-left `[col, row]` coordinates consistently;
- it computes matching hashes on both engines for the same action sequence;
- it voids and replays technical-invalid sub-games without scoring them;
- all required unit and integration tests pass.

---

## 23. References

- Original engine PRD: `PRD_game_engine.md`
- Updated rules source: `game_rules_fixed.md`
- Project-level PRD, actor PRD, testing guide, and assignment references should be updated to use this PRD as the engine authority.
