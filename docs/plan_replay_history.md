# Plan — Replay and History Component

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_replay_history.md`

---

## 1. Module Layout

```text
backend/app/history/
  service.py
  repositories.py
  filters.py
backend/app/replay/
  builder.py
  frames.py
  serializer.py
  tests/
```

---

## 2. Storage Strategy

Store full `state_after_json` in each game event for MVP. This makes replay simple and reliable.

Later optimization can generate frames from event logs on demand.

---

## 3. Frontend Integration

Replay page consumes:

```http
GET /api/games/{match_id}/subgames/{subgame_id}/replay
```

The response should include ordered frames and event metadata.

---

## 4. Tests

- replay frame count matches consumed events;
- terminal frame winner matches sub-game summary;
- public history excludes private debug data;
- filters and pagination work.
