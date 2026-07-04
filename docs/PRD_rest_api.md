# PRD — REST API Component

> **Document type:** Product Requirements Document  
> **Scope:** Requirements for the normal programmatic API under `/api`.

---

## 1. Purpose

The REST API provides a normal code-accessible interface for every operation that can be performed through the web GUI.

The API exists so automated tests, scripts, developers, and the frontend can perform the same operations without browser-only behavior.

---

## 2. Core Requirement

Every GUI operation must have an equivalent REST API endpoint or documented WebSocket operation.

No business capability may be available only through the GUI.

---

## 3. In Scope

The REST API must support:

- authentication and current user state;
- public history retrieval;
- game detail retrieval;
- sub-game detail retrieval;
- replay retrieval;
- creating human-vs-server games;
- creating local-server-vs-external-MCP-server matches;
- validating remote MCP endpoints;
- submitting human actions;
- retrieving live human observations;
- retrieving current available intended actions;
- cancelling permitted games;
- downloading match reports;
- retrieving report delivery status;
- optional admin operations.

---

## 4. Out of Scope

The REST API must not:

- implement game rules;
- directly mutate game state outside the Game Orchestrator;
- expose hidden state to unauthorized users;
- bypass MCP authentication for server-to-server play;
- send raw secrets, tokens, or LLM prompts to public clients.

---

## 5. Endpoint Groups

### 5.1 Authenticated User API

```http
POST /api/auth/login
POST /api/auth/logout
GET  /api/me
```

### 5.2 Public History API

```http
GET /api/games
GET /api/games/{match_id}
GET /api/games/{match_id}/subgames
GET /api/games/{match_id}/subgames/{subgame_id}
GET /api/games/{match_id}/subgames/{subgame_id}/replay
GET /api/games/{match_id}/events
```

### 5.3 Game Creation API

```http
POST /api/games/human-vs-server
POST /api/games/server-vs-server
POST /api/games/validate-opponent
```

### 5.4 Human Action API

```http
GET  /api/games/{match_id}/live-state
GET  /api/games/{match_id}/current-observation
GET  /api/games/{match_id}/available-actions
POST /api/games/{match_id}/human-action
POST /api/games/{match_id}/forfeit
POST /api/games/{match_id}/cancel
```

### 5.5 Report API

```http
GET  /api/reports
GET  /api/reports/{report_id}
GET  /api/reports/{report_id}/download
POST /api/reports/{report_id}/send-email
GET  /api/reports/{report_id}/delivery-status
```

### 5.6 Admin API, Optional

```http
GET  /api/admin/technical-failures
GET  /api/admin/state-divergences
POST /api/admin/games/{match_id}/void
POST /api/admin/config
```

---

## 6. API Security Requirements

- Public endpoints must expose only public data.
- Authenticated endpoints must verify session/token identity.
- Game-action endpoints must verify that the user owns or is allowed to control the active human game.
- Server-vs-server initiation must require authentication.
- Remote endpoint validation must protect against unsafe internal network targets.
- Report email endpoints must not accept arbitrary unauthenticated recipients.

---

## 7. Acceptance Criteria

The REST API is acceptable when:

- all GUI operations are scriptable through `/api` or documented WebSocket messages;
- automated tests can start and complete a human-vs-server game without using the GUI;
- automated tests can start a server-vs-server match against a test MCP server;
- replay and reports can be downloaded via API;
- hidden live state is not exposed through API responses;
- invalid API requests return structured errors.
