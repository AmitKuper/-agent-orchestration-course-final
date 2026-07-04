# PRD — Inter-Group MCP Component

> **Document type:** Product Requirements Document  
> **Scope:** Requirements for MCP-based play between this server and other group servers.

---

## 1. Purpose

The Inter-Group MCP component allows this web server to play matches against remote group servers through MCP.

The local server must be both:

- an MCP server exposing tools under `/mcp`;
- an MCP client capable of calling another group server's `/mcp` endpoint.

---

## 2. Goals

The component must support:

- capability discovery;
- match proposal and acceptance;
- rule negotiation;
- role scheduling;
- action request/response;
- natural-language game messages;
- state-hash comparison where supported;
- technical-invalid handling;
- replay and report generation.

---

## 3. Required MCP Capabilities

The MCP API must expose tools or equivalent operations for:

```text
get_server_info
list_supported_rules
propose_match
respond_to_match_proposal
start_subgame
request_action
submit_action_result
get_match_status
get_public_history
get_replay
```

The exact MCP tool schema must be versioned.

---

## 4. Match Handshake Requirements

Before a match starts, both servers must agree on:

- rules version;
- match ID;
- number of valid sub-games;
- role schedule;
- seed policy;
- game configuration;
- scoring configuration;
- timeout policy;
- report expectations;
- authentication token/session.

If agreement fails, the match must not start.

---

## 5. Rule Negotiation Requirements

The MCP component must support structured negotiation payloads.

Negotiation may include:

- proposed preset name;
- full proposed config;
- supported/unsupported rules;
- counter-proposal;
- accept/reject decision;
- natural-language explanation.

Negotiation strategy is decided by the Negotiation Strategy component. The MCP component only transports messages and structured proposals.

---

## 6. Turn Communication Requirements

Every MCP turn exchange must include:

- match ID;
- sub-game ID;
- actor role;
- actor side;
- observation or observation reference;
- opponent message, if any;
- returned natural-language message;
- structured action;
- optional state hash;
- timestamp.

The message has no direct game-state effect. The action is validated by the Game Engine.

---

## 7. Security Requirements

- External server initiation from GUI must require authentication.
- Guest MCP clients may start games against this server only, subject to rate limits.
- Guest MCP clients must not make this server call arbitrary external URLs.
- Outbound remote server URLs must be validated.
- Tokens must be revocable.
- Hidden active-game state must not be exposed to the wrong side.

---

## 8. Acceptance Criteria

The component is acceptable when:

- two local test servers can discover each other;
- a match config can be proposed, negotiated, and accepted;
- six valid sub-games can be completed through MCP;
- natural-language messages and structured actions are logged;
- technical-invalid sub-games are marked correctly;
- completed inter-group matches appear in history and reports.
