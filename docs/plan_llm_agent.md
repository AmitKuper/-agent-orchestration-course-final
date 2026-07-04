# Plan — Built-In LLM Communication Agent

> **Document type:** Engineering / implementation plan  
> **Related PRD:** `PRD_llm_agent.md`

---

## 1. Module Layout

```text
backend/app/agents/
  communication_agent.py
  negotiation_agent.py
  message_generator.py
  message_parser.py
  mcp_tool_invoker.py
  hidden_state_filter.py
  prompt_loader.py
  schemas.py
  tests/
```

All LLM provider calls go through:

```text
backend/app/shared/gatekeeper.py
```

---

## 2. Gameplay Message Flow

```text
Actor decision
  -> hidden_state_filter
  -> message_generator
  -> gatekeeper LLM call
  -> structured message + MCP payload
  -> mcp_tool_invoker
```

The action inside the MCP payload must match the Actor-selected action.

---

## 3. Negotiation Message Flow

```text
NegotiationPolicy decision
  -> negotiation_agent
  -> gatekeeper LLM call
  -> natural-language proposal/counter/acceptance
  -> mcp_tool_invoker
```

---

## 4. Prompt Files

```text
backend/app/agents/prompts/
  game_turn_message.md
  negotiation_message.md
  opponent_message_summary.md
```

Prompts must instruct the model:

- do not invent hidden state;
- do not alter structured action;
- return valid JSON if structured output is required;
- keep message concise.

---

## 5. Fallback Behavior

If LLM generation fails:

- use a deterministic template message;
- preserve the Actor-selected action;
- log the failure;
- continue the game if protocol allows.

Example fallback:

```text
"I am taking my next move based on my current observation."
```

---

## 6. Tests

Required tests:

- action preservation test;
- hidden-state filtering test;
- prompt output schema validation;
- fallback-on-timeout test;
- MCP invocation payload test;
- token logging test.
