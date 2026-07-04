# PRD — Cop & Thief Web Server

> **Document type:** Product Requirements Document  
> **Scope:** Requirements only — what the web server must support.  
> **Related documents:** `game_rules_fixed.md`, `PRD_game_engine_updated.md`  
> **Status:** Draft v1

---

## 1. Purpose

Build a web server for the Cop & Thief pursuit game that allows humans, local server logic, and remote MCP-compatible game servers to play, view, and replay games.

The web server must expose:

- a web UI for humans;
- a REST API under `/api`;
- an MCP API under `/mcp`;
- public game history and replay pages;
- authenticated game initiation for trusted users;
- guest-accessible history;
- guest MCP game initiation against this server only.

The server must integrate with the existing game engine rules and must not redefine or duplicate game mechanics outside the engine layer.

---

## 2. Goals

The system must:

1. Allow authenticated users to initiate games from the web UI.
2. Allow authenticated users to initiate games against external MCP game servers.
3. Allow humans to play against the local server through the web UI.
4. Allow guest MCP clients to initiate a game against the local server through `/mcp`.
5. Expose game history publicly.
6. Expose detailed game and sub-game results publicly.
7. Provide replay visualization for completed games.
8. Update the web UI without requiring manual page refresh.
9. Preserve complete game logs for replay, audit, and debugging.
10. Keep the REST API, MCP API, and web UI consistent by using the same backend game orchestration service.

---

## 3. Non-Goals

This PRD does not require:

- a production-grade AI strategy for the local server bot;
- global matchmaking;
- payments or subscriptions;
- user-generated custom rule plugins;
- mobile native applications;
- decentralized trust or blockchain-based result validation;
- direct browser-to-MCP communication as the primary human UI path.

---

## 4. User Roles

## 4.1 Guest

A guest is an unauthenticated visitor.

A guest must be able to:

- view public game history;
- open a completed game detail page;
- view sub-game summaries;
- watch completed game replays;
- initiate a game against this server through the MCP API, subject to rate limits.

A guest must not be able to:

- initiate a game from the web UI;
- initiate a server-vs-server match against an external MCP server;
- access private live-game hidden state;
- modify game configuration;
- cancel games;
- access admin or debug information.

## 4.2 Authenticated User

An authenticated user is a named user allowed to initiate games from the web UI.

An authenticated user must be able to:

- start a human-vs-server game from the GUI;
- start a local-server-vs-external-MCP-server game from the GUI;
- configure permitted match options before starting a game;
- play their active human game through the browser;
- view public history and replay pages;
- view live status for games they initiated.

## 4.3 Admin

Admin functionality is optional for the first version.

If implemented, an admin should be able to:

- manage users;
- view technical failures;
- inspect state-divergence errors;
- cancel or void games;
- update server-level configuration;
- manage guest MCP rate limits.

---

## 5. Permission Requirements

| Feature | Guest | Authenticated User | Admin |
|---|---:|---:|---:|
| View public history | Yes | Yes | Yes |
| View completed game details | Yes | Yes | Yes |
| Watch completed replays | Yes | Yes | Yes |
| Start human-vs-server from GUI | No | Yes | Yes |
| Submit human GUI action | No | Own active games | Any, if admin override exists |
| Start local server vs external MCP server | No | Yes | Yes |
| Start guest MCP game vs this server | Yes, rate-limited | Yes | Yes |
| Cancel own active game | No | Yes | Yes |
| View technical/debug logs | No | No | Yes |
| Change global server config | No | No | Yes |

---

## 6. Supported Game Modes

## 6.1 Human vs Server

The system must allow an authenticated user to start a game against the local server.

Requirements:

- The user starts the game from the GUI.
- The user selects from allowed configuration options.
- The local server controls the opponent role.
- The browser shows the player only the information they are allowed to see according to the observation rules.
- The user submits actions through the web UI.
- The local server automatically submits its actions.
- The game must update live without page refresh.
- The completed game must appear in public history.

## 6.2 Local Server vs External MCP Server

The system must allow an authenticated user to start a match against another web server that exposes a compatible MCP endpoint.

Requirements:

- The user enters the external MCP URL.
- The local server validates the URL before connecting.
- The local server discovers or verifies the remote server's supported game tools/rules.
- The local server proposes a match configuration.
- The remote server accepts or rejects the match.
- If accepted, the match is played using MCP messages.
- The local server stores the full match history and replay data.
- The completed match must appear in public history.

## 6.3 Guest MCP Client vs This Server

The system must allow a guest MCP client to start a game against this server through `/mcp`.

Requirements:

- Guest MCP initiation must be rate-limited.
- Guest MCP clients may only start games against the local server.
- Guest MCP clients must not be allowed to instruct this server to connect to another external server.
- The completed game must appear in public history.
- The local server must store replay and audit data for the game.

---

## 7. Web UI Requirements

## 7.1 General UI Requirements

The web UI must be:

- responsive on desktop, tablet, and mobile;
- visually polished and easy to understand;
- usable without manual page refresh;
- clear about the current game state;
- clear about whose turn it is;
- clear about whether the viewer is seeing full state or limited observation.

## 7.2 Required Pages

The web UI must include:

1. Home page.
2. Login page.
3. New game page for authenticated users.
4. Public game history page.
5. Game detail page.
6. Sub-game detail page or sub-game section.
7. Replay page.
8. Live human game page.

## 7.3 Home Page

The home page must show:

- server name/status;
- recent games;
- navigation to game history;
- login/logout state;
- a start-game entry point for authenticated users;
- basic explanation of the game and available modes.

## 7.4 New Game Page

The new game page must be available only to authenticated users.

It must support:

- starting human-vs-server games;
- starting local-server-vs-external-MCP-server games;
- choosing allowed game configuration options;
- entering an external MCP endpoint for server-vs-server games;
- validating the opponent endpoint before game start;
- showing clear error messages when game initiation fails.

## 7.5 Public History Page

The history page must be available to guests.

Each game row/card must show:

- game ID or display identifier;
- local server name;
- opponent/player name;
- game mode;
- date;
- time;
- result from local server perspective: `won`, `lost`, `tied`, `voided`, or `aborted`;
- final score if available;
- number of valid sub-games;
- status: `live`, `completed`, `technical_invalid`, `aborted`, or `cancelled`.

The history page should support:

- pagination;
- sorting by date/time;
- filtering by result;
- filtering by mode;
- filtering by opponent/player name.

## 7.6 Game Detail Page

Clicking a game from history must open a detail page.

The page must show:

- game metadata;
- participants;
- player/server names;
- mode;
- creation/start/end time;
- final result;
- final score;
- rules/configuration used;
- list of sub-games;
- status of each sub-game;
- winner of each sub-game;
- win reason of each sub-game;
- number of turns/actions;
- number of consumed Thief actions;
- number of barriers used;
- link/button to replay each sub-game.

## 7.7 Replay Page

The replay page must show the game board and allow the viewer to move through the game step by step.

The replay must support:

- board visualization;
- Cop position;
- Thief position;
- barriers;
- crumbtrails, when enabled;
- turn/action timeline;
- action messages, when available;
- current frame number;
- actor for the current step;
- action result;
- sub-game selector;
- play/pause;
- next step;
- previous step;
- jump to start;
- jump to end;
- playback speed control.

For completed games, the replay may show the full true state. If actor-perspective replay is supported, the UI must clearly indicate which perspective is being shown.

## 7.8 Live Human Game Page

The live human game page must show:

- current observation available to the human player;
- visible board state;
- whose turn it is;
- available intended actions;
- move controls;
- STAY control when enabled;
- barrier placement controls when the human is Cop;
- confirmation before voluntary forfeit;
- live event log;
- sub-game and match score;
- connection status.

The live page must not reveal hidden information that the game rules say the human cannot observe.

---

## 8. REST API Requirements

The server must expose a REST API under:

```text
/api
```

The REST API must support the web UI.

The REST API must provide capabilities for:

- authentication;
- current user profile;
- game creation for authenticated users;
- human action submission;
- game history retrieval;
- game detail retrieval;
- replay retrieval;
- live-game status retrieval;
- cancellation of allowed games;
- optional admin operations.

The REST API must not contain independent game-rule logic. It must delegate gameplay to the shared game orchestration layer.

---

## 9. MCP API Requirements

The server must expose an MCP API under:

```text
/mcp
```

The MCP API must support game interaction with remote MCP clients and remote MCP game servers.

The MCP API must provide capabilities for:

- discovering supported rules and capabilities;
- starting a guest game against this server;
- proposing or accepting a server-vs-server match;
- retrieving an observation;
- submitting an action;
- retrieving game status;
- retrieving public history;
- retrieving replay data for completed games.

The MCP API must not expose hidden state during an active game unless the requesting player is allowed to see it.

The MCP API must not allow unauthenticated guests to cause this server to initiate outbound connections to arbitrary external servers.

---

## 10. Real-Time Update Requirements

The system must update active browser pages without manual refresh.

Real-time updates must be available for:

- live human games;
- game status changes;
- action submission results;
- sub-game start/end;
- match completion;
- replay playback state if controlled by the server;
- history updates where practical.

The system must gracefully recover from temporary browser disconnection.

---

## 11. Game History and Result Requirements

The system must calculate the final result from the local server perspective.

Result values:

- `won`: local server score is greater than opponent score;
- `lost`: local server score is lower than opponent score;
- `tied`: local server score equals opponent score after a completed match;
- `voided`: game or sub-game was invalid due to technical failure;
- `aborted`: match did not finish and was stopped.

The public history must not expose private tokens, raw credentials, internal network addresses, or hidden live-game state.

---

## 12. Data Retention Requirements

For every game, the system must store enough data to reconstruct:

- initial game configuration;
- participant names and roles;
- sub-game order;
- every submitted action;
- every accepted action result;
- every state transition required for replay;
- terminal state;
- winner and win reason;
- score calculation;
- technical errors, if any.

Completed games should be replayable even after server restart.

---

## 13. Authentication and Authorization Requirements

The system must support login for specific users.

Authenticated actions must include:

- starting human-vs-server games;
- starting server-vs-server games;
- submitting actions in a user's own active human games;
- cancelling a user's own active games.

Guest access must be allowed for:

- viewing history;
- viewing completed replays;
- starting MCP guest games against this server, if enabled.

All authorization decisions must be enforced server-side.

---

## 14. Security Requirements

The system must:

- validate all user input;
- validate external MCP URLs before connecting;
- protect against SSRF when connecting to external MCP servers;
- rate-limit guest MCP game initiation;
- rate-limit login attempts;
- prevent hidden-state leakage in live games;
- prevent guests from modifying games;
- store secrets and tokens securely;
- avoid exposing stack traces to guests;
- log security-relevant events.

---

## 15. Reliability Requirements

The system must:

- continue to serve public history if no active game is running;
- mark failed games clearly;
- not corrupt existing game history when an active game fails;
- support deterministic replay from stored data;
- persist completed games and sub-games;
- handle remote MCP server disconnection gracefully;
- mark technical-invalid games according to the game-engine rules.

---

## 16. Performance Requirements

The system should support:

- multiple concurrent history viewers;
- multiple concurrent replay viewers;
- at least one active human-vs-server game;
- at least one active server-vs-server game;
- paginated history so old games do not slow down the UI.

Concrete scale targets may be defined later.

---

## 17. Acceptance Criteria

The web server is acceptable when:

1. A guest can open the history page and view completed game details.
2. A guest can watch a completed replay.
3. An authenticated user can start a human-vs-server game from the GUI.
4. An authenticated user can submit human actions from the GUI.
5. The live human game updates without manual refresh.
6. An authenticated user can start a match against an external MCP-compatible server.
7. A guest MCP client can start a game against the local server through `/mcp`.
8. Completed games appear in public history.
9. Clicking a game shows sub-game winners, win reasons, turn/action counts, and replay links.
10. Hidden live-game state is not leaked to unauthorized viewers.
11. REST and MCP both use the same game orchestration layer.
12. The server can be restarted without losing completed game history.

---

## 18. Open Product Questions

1. Should live games be publicly viewable, or only completed games?
2. Should completed replay default to full true-state replay or actor-perspective replay?
3. Should guests be allowed to start browser-based human-vs-server games later, or remain MCP-only?
4. What is the first local server bot strategy?
5. Should authenticated users be created manually, or should self-registration exist?
6. Should external MCP opponents require an allowlist?
7. Should failed/voided games appear in public history by default?

---

## 19. Programmatic API Parity Requirement

Every operation available through the web GUI must also be available through a normal authenticated REST API under `/api`, so developers can test and operate the system using code.

The API must support, at minimum:

- login/logout and current-user lookup;
- listing games and filtering history;
- opening game details;
- opening sub-game details;
- retrieving replay data;
- starting human-vs-server games;
- starting local-server-vs-external-MCP-server matches;
- validating remote MCP endpoints;
- submitting human actions;
- cancelling permitted active games;
- reading live-game status;
- reading available intended actions for the current human turn;
- retrieving public report summaries;
- downloading machine-readable match reports.

No GUI-only backend operation is allowed. The GUI must use the same REST API, WebSocket channel, or documented internal API that automated tests can use.

---

## 20. Built-In Agent Requirement

The web server must include a built-in LLM Communication Agent module for server-to-server MCP play.

The built-in agent must:

- convert Actor decisions into natural-language game messages;
- parse or summarize opponent natural-language messages;
- invoke the proper local or remote MCP tool;
- support negotiation messages before match start;
- use only observation-safe information;
- use a centralized LLM Gatekeeper for all LLM API calls;
- be part of the same server application for MVP, not a separate unrelated process.

The built-in agent must not own game rules, scoring, or authoritative game state.

---

## 21. Report and Email Requirement

The server must generate machine-readable match reports after completed internal or inter-group matches.

If email sending is enabled, report delivery must use a configured recipient value from environment or configuration. No recipient email address may be hard-coded in the codebase or documentation.

Report and email requirements are defined in `PRD_email_report.md`.
