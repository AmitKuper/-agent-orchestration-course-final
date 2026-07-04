# Plan — REST API Component

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_rest_api.md`

---

## 1. Implementation Approach

Implement REST endpoints in FastAPI routers grouped by domain.

```text
backend/app/api/
  routes_auth.py
  routes_games.py
  routes_live.py
  routes_replay.py
  routes_reports.py
  routes_admin.py
  dependencies.py
```

All routes should call the SDK layer:

```text
REST route -> SDK -> service/orchestrator -> engine/db/actors
```

Routes must not call internal services directly if an SDK method exists.

---

## 2. Request / Response Models

Use Pydantic models for all request and response bodies.

```text
backend/app/schemas/
  auth.py
  games.py
  actions.py
  replay.py
  reports.py
  errors.py
```

Every endpoint should have typed input and output models.

---

## 3. API Parity Testing

For each GUI flow, implement an API flow test.

| GUI Flow | API Test |
|---|---|
| Login | `test_login_api.py` |
| Start human game | `test_start_human_game_api.py` |
| Submit action | `test_submit_action_api.py` |
| View history | `test_history_api.py` |
| View replay | `test_replay_api.py` |
| Start external MCP match | `test_external_mcp_match_api.py` |
| Send report | `test_report_api.py` |

---

## 4. Error Format

Use one standard error shape:

```json
{
  "error": {
    "code": "invalid_action",
    "message": "Action is not valid for the current actor.",
    "details": {}
  }
}
```

---

## 5. Milestones

1. Auth and current-user endpoints.
2. Public history and replay endpoints.
3. Human-vs-server creation and action endpoints.
4. Server-vs-server creation endpoint.
5. Report endpoints.
6. Admin/debug endpoints.
7. API parity test suite.
