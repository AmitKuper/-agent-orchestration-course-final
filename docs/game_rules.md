# Cops-and-Robbers Game Rules

## 1. Overview

**Cops-and-Robbers** is a two-player pursuit game played on a 2D grid between a **Cop** and a **Thief**.

- The **Cop** tries to capture or trap the Thief.
- The **Thief** tries to survive until the move limit or trap the Cop.
- Players act in turns according to the configured move order.
- The game may use partial observation, meaning each player may see only nearby information.
- Optional crumbtrails can reveal recent movement history.

The game is deterministic once the initial state, configuration, and player actions are fixed.

---

## 2. Game Structure

### 2.1 Sub-Game

A **sub-game** is one complete pursuit game on a single grid.

A sub-game begins with:

1. A grid of configured size.
2. One Cop starting position.
3. One Thief starting position.
4. Zero placed barriers.
5. Counters reset to zero.

A sub-game ends immediately when one win condition is met.

### 2.2 Game Series / Match

A **match** is a series of exactly **6 valid sub-games**.

Scores from all 6 valid sub-games are accumulated to determine the final match score.

### 2.3 Role Assignment Across the Series

Each human player must play exactly:

- **3 sub-games as Cop**
- **3 sub-games as Thief**

Default role schedule:

| Sub-game | Player A Role | Player B Role |
|---|---|---|
| 1 | Cop | Thief |
| 2 | Thief | Cop |
| 3 | Cop | Thief |
| 4 | Thief | Cop |
| 5 | Cop | Thief |
| 6 | Thief | Cop |

A different schedule is allowed only if both players still play exactly 3 sub-games as Cop and 3 as Thief.

### 2.4 Technical Invalid Game

If a sub-game does not complete because of a technical failure, crash, timeout, or invalid corrupted state, it is marked as **technical invalid**.

A technical invalid game:

- Does not count toward the 6 valid sub-games.
- Does not award score to either player.
- Must be replayed using the same match configuration.

---

## 3. Game Board

### 3.1 Grid Layout

- The board is a rectangular 2D grid.
- Grid size is configurable; default is **10 × 10**.
- Coordinates use Cartesian `[column, row]` format.
- Coordinates are 0-indexed.
- `(0, 0)` is the bottom-left cell.
- Valid columns are `0` through `cols - 1`.
- Valid rows are `0` through `rows - 1`.

### 3.2 Starting Positions

Starting positions are determined by configuration.

Supported modes:

| Mode | Meaning |
|---|---|
| `random` | The engine randomly chooses distinct valid starting cells. |
| `fixed` | The configuration provides explicit starting positions for each sub-game. |

Starting positions must satisfy:

- Cop and Thief start in different cells.
- Both positions are inside the grid.
- Neither position contains a barrier.

---

## 4. Actions and Turns

### 4.1 Turn Structure

On each turn, the acting player submits exactly one intended action.

Possible actions:

| Actor | Action | Description |
|---|---|---|
| Cop | `move` | Move to one adjacent cell. |
| Cop | `stay` | Remain in the current cell, if STAY is enabled. |
| Cop | `barrier` | Place one barrier, if barriers are enabled and available. |
| Cop | `forfeit` | Voluntarily lose the sub-game. |
| Thief | `move` | Move to one adjacent cell. |
| Thief | `stay` | Remain in the current cell, if STAY is enabled. |
| Thief | `forfeit` | Voluntarily lose the sub-game. |

Only the Cop can place barriers.

### 4.2 Movement Directions

A movement action may target one of the 8 adjacent cells:

- North
- Northeast
- East
- Southeast
- South
- Southwest
- West
- Northwest

A movement changes the actor's position by at most 1 column and at most 1 row.

### 4.3 STAY Action

If `stay_enabled = true`, both players may choose `stay` as their action.

A STAY action:

- Keeps the actor in the same cell.
- Consumes the actor's turn.
- Updates turn counters normally.
- Updates crumbtrail state normally.

If `stay_enabled = false`, STAY is not a legal action.

### 4.4 Voluntary Forfeit

A player may voluntarily choose `forfeit`.

A voluntary forfeit:

- Ends the sub-game immediately.
- Gives victory to the opponent.
- Uses win reason `cop_forfeit` if the Cop forfeits.
- Uses win reason `thief_forfeit` if the Thief forfeits.

This is different from an invalid action. Invalid actions do not automatically lose the game unless the player voluntarily forfeits or has no legal alternatives.

---

## 5. Movement Rules

### 5.1 Legal Movement

A movement action is legal if all of the following are true:

1. The destination is inside the grid.
2. The destination does not contain a barrier.
3. The movement follows one of the 8 adjacent directions.
4. The actor is allowed to enter the destination cell under the opponent-position rules in Section 5.2.

### 5.2 Opponent-Position Rules

The Cop and Thief do not follow symmetric collision rules.

#### Cop entering the Thief's cell

The Cop **may** move into the Thief's current cell.

If the Cop moves into the Thief's current cell:

- The Thief is captured.
- The sub-game ends immediately.
- The Cop wins with win reason `capture`.

#### Thief entering the Cop's cell

The Thief **may not** move into the Cop's current cell.

If the Thief attempts to move into the Cop's cell, the action is treated as an invalid move.

Since `view_radius` must be at least 1 in partial-observation mode, an adjacent Cop is normally visible to the Thief.

### 5.3 Position Swapping

There is no simultaneous movement. Only one actor moves at a time.

Therefore:

- The game validates movement against the current true state at the moment the action is executed.
- A player may move into a cell the opponent previously occupied, as long as the opponent is no longer there and the cell is otherwise legal.
- The Cop captures only by moving into the Thief's current cell.
- The Thief cannot enter the Cop's current cell.

### 5.4 Out-of-Bounds Attempts

If a player attempts to move outside the grid, the outcome depends on `out_of_bounds_behavior`.

| Value | Meaning |
|---|---|
| `stay` | The actor remains in place, the action consumes the turn, and the action result is reported as failed without disclosing extra hidden information. |
| `invalid` | The action is rejected, no state changes, no turn is consumed, and the actor must choose another action. |

Out-of-bounds attempts do **not** directly cause loss.

A player loses only if they forfeit or if they are trapped with no legal action.

### 5.5 Barrier-Collision Attempts

If a player attempts to move into a barrier cell, the outcome depends on `barrier_collision_behavior`.

| Value | Meaning |
|---|---|
| `stay` | The actor remains in place, the action consumes the turn, and the action result is reported as failed without revealing whether a hidden barrier caused the failure. |
| `invalid` | The action is rejected, no state changes, no turn is consumed, and the actor must choose another action. |

Moving into a barrier does **not** directly cause loss.

A player loses only if they forfeit or if they are trapped with no legal action.

---

## 6. Barrier Mechanics

### 6.1 Barrier Overview

Barriers are permanent blocked cells placed by the Cop.

- Only the Cop can place barriers.
- Placing a barrier is the Cop's entire action for that turn.
- When the Cop places a barrier, the Cop does not move.
- Barriers remain on the board until the sub-game ends.
- A barrier blocks both players from moving into its cell.

### 6.2 Barrier Placement Limit

The Cop may place at most `max_barriers` barriers per sub-game.

Default:

```text
max_barriers = 5
```

If `max_barriers = 0`, barrier placement is disabled.

### 6.3 Barrier Placement Scope

Barrier placement scope is controlled by `barrier_placement_scope`.

| Value | Meaning |
|---|---|
| `adjacent_only` | The Cop may place a barrier only on one of the 8 adjacent cells. |
| `current_and_adjacent` | The Cop may place a barrier either on one of the 8 adjacent cells or on the Cop's current cell. |

Default:

```text
barrier_placement_scope = "adjacent_only"
```

### 6.4 General Barrier Placement Constraints

The Cop may place a barrier only if all of the following are true:

1. The Cop has placed fewer than `max_barriers` barriers in the current sub-game.
2. The target cell is inside the grid.
3. The target cell does not already contain a barrier.
4. The target cell is not the Thief's current cell.
5. The target cell is allowed by `barrier_placement_scope`.

### 6.5 Barrier on the Cop's Current Cell

This rule applies only when:

```text
barrier_placement_scope = "current_and_adjacent"
```

If the Cop places a barrier on the Cop's current cell:

- The barrier is created under the Cop.
- The Cop remains in that cell for the current turn.
- The Cop may move out of that cell on a later turn, if the destination is legal.
- The barrier does not prevent the Cop from leaving the cell.
- Once the Cop leaves, neither player may move into that cell again.
- If STAY is enabled, the Cop may remain on that cell by choosing STAY.
- If STAY is disabled and all movement destinations are blocked, the Cop may become trapped unless another barrier action is legal.

This option is allowed but is more complex than `adjacent_only`. For simpler gameplay and implementation, use `adjacent_only`.

### 6.6 Barrier Visibility Under Partial Observation

Under partial observation:

- Barriers inside the actor's view radius are visible.
- Barriers outside the actor's view radius are hidden.
- Hidden barriers still block movement.
- If an attempted move fails because of a hidden barrier, the actor is not told that the hidden barrier was the reason.

Under full observation:

- All barriers are visible to both players.

---

## 7. Trapped Condition

A player is **trapped** if they have no legal action that can consume a turn and keep the game continuing.

### 7.1 Thief Trapped

The Thief is trapped if all of the following are true:

1. The Thief has no legal movement action.
2. STAY is disabled, or STAY is otherwise not legal.
3. The Thief has not chosen voluntary forfeit; voluntary forfeit is handled separately.

If the Thief is trapped, the Cop wins immediately with win reason `thief_trapped`.

If `stay_enabled = true`, the Thief is usually not trapped because STAY is a legal action.

### 7.2 Cop Trapped

The Cop is trapped if all of the following are true:

1. The Cop has no legal movement action.
2. STAY is disabled, or STAY is otherwise not legal.
3. The Cop has no legal barrier-placement action available.
4. The Cop has not chosen voluntary forfeit; voluntary forfeit is handled separately.

If the Cop is trapped, the Thief wins immediately with win reason `cop_trapped`.

If `stay_enabled = true`, the Cop is usually not trapped because STAY is a legal action.

### 7.3 Trapped Check Timing

After every consumed action, the engine checks whether the opponent is trapped.

If the opponent is trapped, the acting player wins immediately.

---

## 8. Victory Conditions

Win conditions are checked immediately after each consumed action.

### 8.1 Cop Victory

The Cop wins if any of the following occurs:

| Win Reason | Condition |
|---|---|
| `capture` | Cop moves into the Thief's current cell. |
| `thief_trapped` | Thief has no legal action after the Cop's action. |
| `thief_forfeit` | Thief voluntarily forfeits. |

### 8.2 Thief Victory

The Thief wins if any of the following occurs:

| Win Reason | Condition |
|---|---|
| `thief_survived` | Thief completes `max_moves` Thief actions without being captured. |
| `cop_trapped` | Cop has no legal action after the Thief's action. |
| `cop_forfeit` | Cop voluntarily forfeits. |

### 8.3 Win Detection Order

After each consumed action, check win conditions in this order:

1. **Voluntary forfeit**: If the actor forfeited, the opponent wins immediately.
2. **Capture**: If the Cop moved into the Thief's current cell, the Cop wins immediately.
3. **Opponent trapped**: If the opponent has no legal action, the actor wins immediately.
4. **Thief survival**: If the actor is the Thief and `thief_actions_completed >= max_moves`, the Thief wins immediately.

Invalid rejected actions do not trigger win-condition checks because they do not consume a turn and do not change the game state.

---

## 9. Move Limit

### 9.1 Meaning of `max_moves`

`max_moves` means the maximum number of **Thief actions that consume a turn**.

Default:

```text
max_moves = 25
```

A Thief action counts toward `max_moves` if it consumes a turn, including:

- Successful movement.
- STAY.
- Failed movement that results in STAY because of `out_of_bounds_behavior = "stay"`.
- Failed movement that results in STAY because of `barrier_collision_behavior = "stay"`.

A rejected invalid action does not count toward `max_moves` because it does not consume a turn.

### 9.2 Survival Timing

The Thief wins by survival immediately after the Thief completes the `max_moves`-th consumed Thief action, unless another earlier win condition in the same check already ended the game.

This means the Cop does not receive an extra final turn after the Thief has reached the survival limit.

---

## 10. Turn Order

### 10.1 Move Order Configuration

Turn order is controlled by `move_order`.

| Value | Meaning |
|---|---|
| `thief_first` | Each round acts in order: Thief, then Cop. |
| `cop_first` | Each round acts in order: Cop, then Thief. |
| `alternating` | Odd-numbered rounds: Thief, then Cop. Even-numbered rounds: Cop, then Thief. |

Default:

```text
move_order = "thief_first"
```

### 10.2 Round Definition

A **round** is a scheduled pair of turns in which each actor is scheduled to act once.

A round may end early if a win condition is met after the first actor's action.

### 10.3 Turn Counters

The game tracks:

| Counter | Meaning |
|---|---|
| `turn_counter` | Number of consumed actions by either player. |
| `thief_actions_completed` | Number of consumed Thief actions. This is used for `max_moves`. |
| `round_index` | Current scheduled round number, starting from 1. |

Rejected invalid actions do not increment counters.

---

## 11. Partial Observation

### 11.1 Observation Model

Partial observation is enabled by default.

When partial observation is enabled, each actor receives only information visible within their view radius.

Hidden information may include:

- Opponent position.
- Barriers.
- Crumbtrails.

### 11.2 View Radius

The default view radius is Chebyshev distance 2.

```text
view_radius = 2
```

Chebyshev distance between `(x1, y1)` and `(x2, y2)` is:

```text
max(abs(x1 - x2), abs(y1 - y2))
```

A cell is visible if its Chebyshev distance from the actor is less than or equal to `view_radius`.

### 11.3 Hidden Opponent Position

The opponent's position is visible only if the opponent is within the actor's view radius.

If the opponent is outside the actor's view radius, the observation reports the opponent position as hidden.

### 11.4 Hidden Barriers

A barrier is visible only if it is within the actor's view radius.

Hidden barriers still exist in the true game state and still block movement.

### 11.5 Legal Actions and Hidden Information

To avoid leaking hidden information, actors should not receive a full true-state legal-action list under partial observation.

Instead, each actor receives:

- Their own position.
- Visible cells within view radius.
- Visible barriers within view radius.
- Visible opponent position, if within view radius.
- Candidate actions that are structurally possible from their current position.

The engine validates submitted actions against the true state.

If a move fails because of hidden information, the result should be reported generically, for example:

```text
move_failed
```

The engine should not reveal whether the failure was caused by a hidden barrier, boundary, or another hidden-state rule unless full observation is enabled.

### 11.6 Full Observation Mode

If `partial_observation = false`:

- Both players see the full board.
- Both players see the opponent's exact position.
- Both players see all barriers.
- All crumbtrails enabled by configuration are visible.
- `view_radius` is ignored.

---

## 12. Crumbtrail Mechanics

### 12.1 Overview

A **crumbtrail** is a visible record of where a player has recently been.

Crumbtrails are optional and controlled by configuration.

Crumbtrails are informational only. They do not block movement.

### 12.2 Crumbtrail Modes

| Value | Meaning |
|---|---|
| `none` | No crumbtrails are visible. |
| `thief_only` | The Cop can see the Thief's crumbtrail. The Thief cannot see the Cop's crumbtrail. |
| `cop_only` | The Thief can see the Cop's crumbtrail. The Cop cannot see the Thief's crumbtrail. |
| `both` | Both players can see the opponent's crumbtrail. |

Default:

```text
crumbtrail_mode = "none"
```

### 12.3 Crumbtrail Markers

Thief crumbtrail markers:

| Marker | Meaning |
|---|---|
| `T` | Thief is currently on this cell, if visible. |
| `1` | Thief was on this cell 1 completed Thief action ago. |
| `2` | Thief was on this cell 2 completed Thief actions ago. |
| `N` | Thief was on this cell N completed Thief actions ago. |

Cop crumbtrail markers:

| Marker | Meaning |
|---|---|
| `C` | Cop is currently on this cell, if visible. |
| `1001` | Cop was on this cell 1 completed Cop action ago. |
| `1002` | Cop was on this cell 2 completed Cop actions ago. |
| `1000 + N` | Cop was on this cell N completed Cop actions ago. |

The separate numeric ranges prevent confusion when both trails are visible.

### 12.4 Crumbtrail Age Unit

Crumbtrail age is measured in the owning actor's consumed actions.

Examples:

- A Thief trail age increases only when the Thief completes an action.
- A Cop trail age increases only when the Cop completes an action.
- STAY refreshes the actor's current cell.
- A failed move that consumes the turn refreshes the actor's current cell.
- A rejected invalid action does not update crumbtrails.

### 12.5 Crumbtrail Persistence

Crumbtrail persistence is controlled by `crumbtrail_max_age`.

| Value | Meaning |
|---|---|
| `-1` | Trails never fade. |
| `0` | Only the current visible position marker may be shown; no past trail remains. |
| `N > 0` | Trail markers older than N completed actions of that actor disappear. |

Default:

```text
crumbtrail_max_age = -1
```

### 12.6 Crumbtrail Visibility

Under partial observation:

- A crumbtrail marker is visible only if its cell is within the viewer's view radius.
- Crumbtrails outside the view radius are hidden.
- Hidden crumbtrails do not affect movement.

Under full observation:

- All enabled crumbtrails are visible.

### 12.7 Revisiting a Cell

If a player revisits a cell, that cell becomes the player's current marker again:

- `T` for the Thief.
- `C` for the Cop.

The previous age value for that cell is reset.

---

## 13. Scoring System

### 13.1 Per-Sub-Game Scoring

| Sub-game Outcome | Cop Score | Thief Score |
|---|---:|---:|
| Cop wins by `capture`, `thief_trapped`, or `thief_forfeit` | 20 | 5 |
| Thief wins by `thief_survived`, `cop_trapped`, or `cop_forfeit` | 5 | 10 |

### 13.2 Series Totals

Because each human player plays exactly 3 sub-games as Cop and 3 as Thief:

- Maximum possible score for one player: `3 × 20 + 3 × 10 = 90`.
- Minimum possible score for one player: `3 × 5 + 3 × 5 = 30`.

The player with the higher cumulative score after 6 valid sub-games wins the match.

If both players have the same cumulative score, the match is a draw unless a tie-break rule is configured separately.

---

## 14. Configuration Parameters

The following parameters are read from `config.json` or from the agreed pre-game configuration.

They must not be hard-coded.

| Parameter | Description | Default |
|---|---|---|
| `grid_size` | Grid dimensions `[cols, rows]`. | `[10, 10]` |
| `num_games` | Number of valid sub-games in a match. | `6` |
| `max_moves` | Maximum number of consumed Thief actions before Thief survival win. | `25` |
| `max_barriers` | Maximum barriers the Cop may place per sub-game. | `5` |
| `view_radius` | Chebyshev distance for partial observation. | `2` |
| `partial_observation` | Whether partial observation is enabled. | `true` |
| `stay_enabled` | Whether players may choose STAY. | `true` |
| `out_of_bounds_behavior` | `stay` or `invalid`. | `stay` |
| `barrier_collision_behavior` | `stay` or `invalid`. | `stay` |
| `barrier_placement_scope` | `adjacent_only` or `current_and_adjacent`. | `adjacent_only` |
| `starting_position_mode` | `random` or `fixed`. | `random` |
| `move_order` | `thief_first`, `cop_first`, or `alternating`. | `thief_first` |
| `crumbtrail_mode` | `none`, `thief_only`, `cop_only`, or `both`. | `none` |
| `crumbtrail_max_age` | Non-negative integer or `-1`. | `-1` |
| `scoring.cop_win` | Cop score when Cop wins. | `20` |
| `scoring.thief_win` | Thief score when Thief wins. | `10` |
| `scoring.cop_loss` | Cop score when Cop loses. | `5` |
| `scoring.thief_loss` | Thief score when Thief loses. | `5` |

---

## 15. Configuration Validation

Before starting a match, validate the configuration.

Required checks:

- `grid_size` must be at least `[2, 2]`.
- `num_games` must equal `6` unless the scoring and role schedule are also changed.
- `max_moves` must be an integer greater than or equal to `1`.
- `max_barriers` must be an integer greater than or equal to `0`.
- `view_radius` must be an integer greater than or equal to `1`, or infinity for full observation.
- If `partial_observation = false`, `view_radius` is ignored.
- `stay_enabled` must be `true` or `false`.
- `out_of_bounds_behavior` must be `stay` or `invalid`.
- `barrier_collision_behavior` must be `stay` or `invalid`.
- `barrier_placement_scope` must be `adjacent_only` or `current_and_adjacent`.
- `starting_position_mode` must be `random` or `fixed`.
- If `starting_position_mode = fixed`, all 6 sub-games must have explicit valid Cop and Thief starting positions.
- `move_order` must be `thief_first`, `cop_first`, or `alternating`.
- `crumbtrail_mode` must be `none`, `thief_only`, `cop_only`, or `both`.
- `crumbtrail_max_age` must be `-1` or a non-negative integer.
- Scoring values must be non-negative integers.
- The role schedule must assign each human player exactly 3 Cop games and 3 Thief games.

Recommended consistency rules:

- If strict no-leak partial observation is desired, prefer `out_of_bounds_behavior = stay` and `barrier_collision_behavior = stay`.
- If `stay_enabled = true`, trapping is rare or impossible because STAY is usually a legal action.
- If trapping should be an important win condition, use `stay_enabled = false`.
- For simpler implementation, use `barrier_placement_scope = adjacent_only`.

---

## 16. State Representation

### 16.1 True Game State

The engine maintains the true game state.

Required fields:

| Field | Description |
|---|---|
| `game_id` | Unique identifier for the sub-game. |
| `grid_size` | Current grid dimensions `[cols, rows]`. |
| `cop_player_id` | Human player currently assigned as Cop. |
| `thief_player_id` | Human player currently assigned as Thief. |
| `cop_position` | Current Cop position `[col, row]`. |
| `thief_position` | Current Thief position `[col, row]`. |
| `barriers` | Set or list of barrier positions. |
| `barriers_placed` | Number of barriers placed by the Cop in this sub-game. |
| `turn_counter` | Number of consumed actions by either actor. |
| `thief_actions_completed` | Number of consumed Thief actions. |
| `round_index` | Current scheduled round number, starting from 1. |
| `current_actor` | Actor whose turn it is: `cop` or `thief`. |
| `game_over` | Boolean indicating whether the sub-game has ended. |
| `winner` | `cop`, `thief`, or `null` before game end. |
| `win_reason` | Reason for victory, or `null` before game end. |
| `crumbtrail_state` | Stored trail history, if crumbtrails are enabled. |

### 16.2 Per-Actor Observation State

Each actor receives an observation derived from the true state.

Always visible:

- Own position.
- Turn counters.
- Round index.
- Own role.
- Remaining Cop barriers, if the actor is the Cop.
- Game-over status, if the game has ended.

Visible only if allowed by observation mode:

- Opponent position.
- Barriers.
- Crumbtrails.

Under partial observation, the observation must not expose hidden barriers by giving a true-state legal-action list.

---

## 17. Game Flow Summary

### 17.1 Match Initialization

1. Load and validate configuration.
2. Create the 6-sub-game role schedule.
3. Initialize both players' cumulative scores to 0.
4. Start sub-game 1.

### 17.2 Sub-Game Initialization

For each sub-game:

1. Create an empty grid.
2. Assign Cop and Thief roles according to the role schedule.
3. Choose starting positions according to `starting_position_mode`.
4. Verify starting positions are valid and distinct.
5. Reset barriers to empty.
6. Reset `barriers_placed` to 0.
7. Reset `turn_counter` to 0.
8. Reset `thief_actions_completed` to 0.
9. Set `round_index` to 1.
10. Initialize crumbtrail state, if enabled.
11. Determine the first actor from `move_order`.

### 17.3 Main Loop

Repeat until `game_over = true`:

1. Determine the current actor from `move_order` and `round_index`.
2. Provide the actor with an observation state.
3. Actor submits one intended action.
4. Engine validates the action against the true state.
5. If the action is rejected as invalid:
   - No state changes.
   - No counters increment.
   - The same actor must choose another action.
6. If the action consumes the turn:
   - Apply the action result.
   - Increment `turn_counter`.
   - If actor is Thief, increment `thief_actions_completed`.
   - Update crumbtrail state.
   - Check win conditions in the order defined in Section 8.3.
7. If the game is not over, advance to the next scheduled actor.
8. If both actors have completed their scheduled turns for the round, increment `round_index`.

### 17.4 End of Sub-Game

When a sub-game ends:

1. Record the winner.
2. Record the win reason.
3. Assign scores according to Section 13.
4. Add scores to the players' cumulative match totals.
5. Continue to the next sub-game until 6 valid sub-games have completed.

### 17.5 End of Match

After 6 valid sub-games:

1. Sum each player's score.
2. Higher score wins the match.
3. Equal score means draw unless a tie-break rule is configured.

---

## 18. Example Configurations

### 18.1 Conservative / Beginner-Friendly

```text
Grid: 10×10
Max Moves: 25
Max Barriers: 5
STAY: enabled
Out-of-Bounds: stay
Barrier Collision: stay
Partial Observation: true
View Radius: 2
Barrier Placement: adjacent_only
Move Order: thief_first
Crumbtrail: none
```

This setup is forgiving because invalid movement attempts waste turns instead of requiring re-selection, and STAY prevents most trapped losses.

### 18.2 Tactical / Balanced

```text
Grid: 10×10
Max Moves: 20
Max Barriers: 3
STAY: disabled
Out-of-Bounds: invalid
Barrier Collision: invalid
Partial Observation: true
View Radius: 3
Barrier Placement: adjacent_only
Move Order: thief_first
Crumbtrail: both
Crumbtrail Max Age: 5
```

This setup makes trapping meaningful because STAY is disabled.

### 18.3 Aggressive / Cop-Favored

```text
Grid: 8×8
Max Moves: 15
Max Barriers: 6
STAY: disabled
Out-of-Bounds: invalid
Barrier Collision: invalid
Partial Observation: false
Barrier Placement: current_and_adjacent
Move Order: cop_first
Crumbtrail: both
Crumbtrail Max Age: 3
```

This setup favors the Cop because the grid is smaller, the Cop has more barriers, and the Cop moves first.

---

## 19. Sanity Check Stages

Recommended testing progression:

| Stage | Grid Dimensions | Goal | Complexity |
|---|---|---|---|
| 1 | 2×2 | Basic action validation, capture, and counters. | Very Low |
| 2 | 3×2 / 2×3 | Turn order, role switching, and survival timing. | Low |
| 3 | 4×3 / 3×4 | Barriers, trapping, and partial observation. | Medium |
| 4 | 5×5 | Crumbtrails and strategic behavior. | High |
| 5 | 10×10 | Full default match testing. | Full |

---

## 20. Key Mechanics Summary

- A match contains exactly 6 valid sub-games.
- Each player plays 3 sub-games as Cop and 3 as Thief.
- The Cop wins by capturing the Thief, trapping the Thief, or receiving a Thief forfeit.
- The Thief wins by surviving `max_moves` consumed Thief actions, trapping the Cop, or receiving a Cop forfeit.
- Only the Cop may enter the opponent's current cell; this causes capture.
- The Thief may not enter the Cop's current cell.
- `max_moves` counts consumed Thief actions, not full rounds and not both players' turns.
- STAY is configurable.
- If STAY is enabled, trapped losses are usually impossible because STAY is a legal action.
- Barriers block entry into cells but do not cause automatic loss.
- Hidden barriers still block movement under partial observation.
- Crumbtrails are informational only and never block movement.
- Invalid rejected actions do not consume turns and do not trigger win checks.
- Voluntary forfeit immediately loses the sub-game.

---

## 21. Resolved Ambiguities From Earlier Drafts

The following design choices resolve previously ambiguous or contradictory rules:

1. **Capture vs legal movement**: The Cop may enter the Thief's cell to capture; the Thief may not enter the Cop's cell.
2. **Forfeit vs invalid action**: `forfeit` means voluntary loss. Invalid actions are now called `invalid` and do not automatically lose the game.
3. **Move limit**: `max_moves` counts consumed Thief actions only.
4. **Move order**: The main loop supports `thief_first`, `cop_first`, and `alternating`.
5. **STAY and trapping**: STAY is a legal action when enabled; therefore a player with STAY available is not trapped.
6. **Barriers on the Cop's current cell**: This is allowed only under `current_and_adjacent` and has explicit movement semantics.
7. **Series scoring**: The 90-point maximum assumes each player plays exactly 3 Cop games and 3 Thief games.
8. **Partial-observation leakage**: Actors should not receive true hidden-state legal moves under partial observation.
