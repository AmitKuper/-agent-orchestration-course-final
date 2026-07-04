# PRD — Final Project: Cop & Thief Multi-Server Game Platform

> **Document type:** General Product Requirements Document  
> **Scope:** High-level product requirements for the final project. Component-specific PRDs define detailed requirements.

---

## 1. Purpose

Build a complete Cop & Thief multi-server game platform that supports human play, autonomous server play, MCP-based inter-group matches, public history, replay, reports, and learned actor/negotiation strategies.

---

## 2. Product Goals

The system must:

1. implement the updated Cop & Thief rules through a deterministic Game Engine;
2. expose a responsive web UI;
3. expose a normal REST API under `/api` for every GUI operation;
4. expose an MCP API under `/mcp` for server-to-server and agent play;
5. support human-vs-server games;
6. support local-server-vs-external-group-server games;
7. support guest MCP games against this server only;
8. store public history and replay data;
9. generate machine-readable reports;
10. optionally send reports by email using configured recipients only;
11. use Actor components for board strategy;
12. use a built-in LLM Communication Agent for natural-language messages and MCP tool invocation;
13. use a Negotiation Strategy component for learned or rule-based match-term negotiation.

---

## 3. Non-Goals

The first final-project version does not require:

- perfect game strategy;
- training neural models at match start;
- direct browser-to-MCP control;
- global matchmaking service;
- public self-registration;
- distributed training infrastructure;
- exposing private debug prompts or hidden live-game state.

---

## 4. High-Level Component List

| Component | PRD | Plan |
|---|---|---|
| Game Rules | `game_rules.md` | N/A |
| Game Engine | `PRD_game_engine.md` | `plan_game_engine.md` |
| Web Server | `PRD_webserver.md` | `plan_webserver.md` |
| REST API | `PRD_rest_api.md` | `plan_rest_api.md` |
| Inter-Group MCP | `PRD_mcp_intergroup.md` | `plan_mcp_intergroup.md` |
| Actor System | `PRD_actor.md` | `plan_actor.md` |
| Built-In LLM Agent | `PRD_llm_agent.md` | `plan_llm_agent.md` |
| Negotiation Strategy | `PRD_negotiation.md` | `plan_negotiation.md` |
| Replay and History | `PRD_replay_history.md` | `plan_replay_history.md` |
| Report and Email | `PRD_email_report.md` | `plan_email_report.md` |
| Development Rules | `development_rules.md` | N/A |

---

## 5. Authority Boundaries

| System Concern | Authority |
|---|---|
| Rules, validation, scoring, win/loss | Game Engine |
| Board action strategy | Actor System |
| Match-term negotiation strategy | Negotiation Strategy |
| Natural-language communication | Built-In LLM Agent |
| MCP protocol transport | Inter-Group MCP Component |
| Browser and public pages | Web Server |
| Script/test access | REST API |
| Replay/history storage | Replay and History |
| JSON reports and email delivery | Report and Email |

---

## 6. Core Architectural Principle

The Game Engine is the only authoritative rules layer.

REST, MCP, Web UI, actors, LLM agents, reports, and replay must not reimplement rules independently.

---

## 7. Acceptance Criteria

The final project is acceptable when:

- a full 6-valid-sub-game match can run locally;
- a human can play against the server through the GUI;
- the same human flow can be executed through `/api` using code;
- the server can play another compatible server through `/mcp`;
- the Actor system selects Cop/Thief actors according to rules;
- the LLM Agent generates messages and invokes MCP without changing Actor actions;
- negotiation can accept/reject/counter-propose match configs;
- completed games are visible in public history;
- completed games can be replayed step by step;
- reports can be generated and downloaded;
- email delivery, if enabled, uses configured recipients only;
- secrets and recipient addresses are not hard-coded.
