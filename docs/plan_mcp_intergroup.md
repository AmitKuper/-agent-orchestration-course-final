# Plan — Inter-Group MCP Component

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_mcp_intergroup.md`

---

## 1. Module Layout

```text
backend/app/mcp/
  server.py
  client.py
  tools.py
  schemas.py
  auth.py
  sessions.py
  errors.py
  compatibility.py
```

---

## 2. Server Role

The MCP server exposes tools under `/mcp` and delegates all work to the SDK.

```text
Remote MCP client -> /mcp -> MCP tools -> SDK -> Orchestrator
```

---

## 3. Client Role

The MCP client is used when an authenticated user initiates a match against another group server.

```text
GUI/API -> SDK -> InterGroupMatchService -> MCP client -> Remote /mcp
```

---

## 4. Handshake Flow

```text
1. validate remote URL
2. call get_server_info
3. call list_supported_rules
4. generate proposal through Negotiation Strategy
5. send propose_match
6. handle accept/reject/counter
7. create local match record
8. start sub-game loop
```

---

## 5. Action Flow

```text
1. Game Orchestrator asks local Actor for local action when local side acts.
2. Built-in LLM Agent turns actor decision into natural-language message.
3. MCP client sends action/message to remote server.
4. Remote server validates/responds.
5. Both sides update logs and compare state hash when available.
```

When the remote side acts:

```text
1. Local server sends observation-safe request_action to remote server.
2. Remote server returns message + structured action.
3. Local Game Engine validates and applies action.
4. Local server returns result/state hash.
```

---

## 6. Test Strategy

Implement a fake MCP opponent server for tests.

Required tests:

- capability discovery;
- unsupported rule rejection;
- successful negotiation;
- full six-sub-game match;
- timeout handling;
- malformed action handling;
- hidden-state leakage checks;
- state-hash mismatch technical-invalid handling.
