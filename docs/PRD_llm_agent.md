# PRD — Built-In LLM Communication Agent

> **Document type:** Product Requirements Document  
> **Scope:** Requirements for the built-in agent that speaks natural language and invokes MCP tools.

---

## 1. Purpose

The Built-In LLM Communication Agent converts structured strategic decisions into natural-language messages and MCP tool calls.

It is part of the web server application for MVP. It is not a separate unrelated process.

---

## 2. Responsibilities

The agent must:

- generate natural-language turn messages from Actor decisions;
- parse or summarize opponent natural-language messages;
- generate natural-language negotiation messages from Negotiation Strategy decisions;
- invoke the correct MCP tool through the MCP client layer;
- keep messages consistent with the current role, observation, and selected action;
- avoid hidden-state leakage;
- log prompts, model IDs, token usage, and outputs according to configuration.

---

## 3. Non-Responsibilities

The agent must not:

- own game strategy;
- replace the Actor-selected move by default;
- decide official game legality;
- mutate authoritative game state;
- compute score or winner;
- access hidden true state;
- bypass the LLM Gatekeeper;
- hard-code secrets or recipient addresses.

---

## 4. Inputs

For a gameplay turn, the agent may receive:

- observation-safe actor observation;
- Actor-selected structured action;
- Actor tactical intent/rationale;
- opponent's previous natural-language message;
- public rule summary;
- allowed communication style.

For negotiation, the agent may receive:

- Negotiation Strategy decision;
- supported rule summary;
- opponent proposal summary;
- public server identity;
- allowed MCP tool names.

---

## 5. Outputs

For gameplay:

```json
{
  "message_to_opponent": "I am closing the path near the center.",
  "mcp_tool_name": "submit_action",
  "mcp_payload": {
    "action": {"type": "barrier", "direction": "NE"}
  }
}
```

For negotiation:

```json
{
  "message_to_opponent": "I propose the tactical preset with partial observation.",
  "mcp_tool_name": "propose_match",
  "mcp_payload": {
    "proposal": {}
  }
}
```

---

## 6. Hidden-State Safety

The agent must receive only observation-safe state. If full true state is available elsewhere in the server, it must be filtered before the agent sees it.

Messages must not reveal:

- hidden opponent position;
- hidden barriers;
- internal model logits;
- private tokens;
- private debug data.

---

## 7. LLM Gatekeeper Requirement

All LLM calls must go through a centralized Gatekeeper module responsible for:

- API key access;
- rate limiting;
- retry policy;
- timeout policy;
- token usage logging;
- cost tracking;
- prompt/output logging rules.

No agent module may call an LLM provider directly.

---

## 8. Acceptance Criteria

The LLM Agent is acceptable when:

- it can generate a message for a structured Actor decision;
- it can generate a negotiation message for a structured negotiation action;
- it invokes the correct MCP client operation;
- it never changes the Actor action unless override mode is explicitly enabled;
- hidden-state leakage tests pass;
- LLM calls are routed through Gatekeeper;
- token usage is logged.
