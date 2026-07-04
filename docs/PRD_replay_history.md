# PRD — Replay and History Component

> **Document type:** Product Requirements Document  
> **Scope:** Requirements for storing public history and replaying completed games.

---

## 1. Purpose

The Replay and History component stores match results, sub-game summaries, event logs, messages, state snapshots, and replay data for public viewing and audit.

---

## 2. Requirements

The component must:

- store every match and sub-game;
- store every consumed action;
- store invalid/protocol events needed for audit;
- store natural-language messages;
- store enough state to replay the game step by step;
- support public history pages;
- support API access for tests and scripts;
- distinguish completed, live, technical-invalid, aborted, and cancelled games.

---

## 3. Replay Requirements

Replay must show:

- board state;
- Cop and Thief positions;
- barriers;
- crumbtrails when enabled;
- turn/action timeline;
- message for each turn when available;
- action result;
- winner and win reason at terminal frame.

Completed-game replay may show full true state. Actor-perspective replay is optional but must be clearly labeled if implemented.

---

## 4. Acceptance Criteria

- A completed match appears in public history.
- Clicking a match shows sub-game summaries.
- Replay can step forward and backward.
- Replay data is available through REST API.
- Stored events can reconstruct the terminal state.
