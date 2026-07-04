# TODO — Cop & Thief Project Progress

> Updated after every session. Completed items carry the commit hash.
> Status key: ✅ Complete · 🚧 In Progress · ⬜ Not Started

---

## Phase 1 — Foundation ✅ Complete (commit: bdb4001)

### Project layout & tooling
- [x] `src/cop_thief/` package with full directory structure
- [x] `pyproject.toml` — uv, hatchling, ruff, pytest, all deps
- [x] `uv.lock` committed alongside `pyproject.toml`
- [x] `.env.example` — template for all required environment variables
- [x] `.gitignore` — excludes `.env`, `*.db`, `.venv`, `node_modules`, model artifacts

### Configuration files
- [x] `config/setup.json` — app-level defaults (prefixes, pagination, timeouts)
- [x] `config/rate_limits.json` — LLM and guest-MCP rate limits (read by Gatekeeper only)
- [x] `config/game_defaults.json` — default game rules and board settings

### Shared utilities
- [x] `src/cop_thief/constants.py` — all magic strings and numeric literals
- [x] `src/cop_thief/shared/version.py` — single version source (`0.1.0`)
- [x] `src/cop_thief/shared/errors.py` — domain error hierarchy
- [x] `src/cop_thief/shared/security.py` — bcrypt password hashing + JWT creation/verification
- [x] `src/cop_thief/shared/gatekeeper.py` — LLM gatekeeper stub (full impl in Phase 6)

### SDK entry point
- [x] `src/cop_thief/sdk/sdk.py` — `CopThiefSDK` facade; all external callers go through here

### Database layer
- [x] `src/cop_thief/db/base.py` — SQLAlchemy `DeclarativeBase`
- [x] `src/cop_thief/db/session.py` — async engine, session factory, `init_db()` for dev
- [x] `src/cop_thief/db/models/user.py` — `User` ORM model
- [x] `src/cop_thief/db/models/match.py` — `Match` ORM model
- [x] `src/cop_thief/db/models/sub_game.py` — `SubGame` ORM model
- [x] `src/cop_thief/db/models/game_event.py` — `GameEvent` ORM model (canonical replay log)
- [x] `src/cop_thief/db/repositories.py` — `MatchRepository`, `UserRepository`

### Pydantic schemas
- [x] `src/cop_thief/schemas/api.py` — `HealthResponse`, `LoginRequest`, `TokenResponse`, `UserResponse`, `PaginatedResponse`
- [x] `src/cop_thief/schemas/game.py` — `MatchSummary`, `MatchDetail`, `SubGameSummary`, enums

### FastAPI application
- [x] `src/cop_thief/webserver/config.py` — `Settings` loaded from env / `.env`
- [x] `src/cop_thief/webserver/main.py` — FastAPI factory, CORS middleware, lifespan
- [x] `src/cop_thief/api/deps.py` — shared FastAPI dependencies (`SessionDep`, `SettingsDep`)
- [x] `src/cop_thief/api/routes_health.py` — `GET /api/health` (unauthenticated, live)
- [x] `src/cop_thief/api/routes_auth.py` — login / logout / me stubs (full impl in Phase 4)
- [x] `src/cop_thief/api/routes_games.py` — `GET /api/games`, `GET /api/games/{id}` (public)

### Migrations
- [x] `alembic.ini` + `alembic/env.py` + `alembic/script.py.mako` — Alembic scaffold

### Tests (4/4 passing, 0 ruff violations)
- [x] `tests/unit/test_version.py` — version consistency: `version.py` ↔ `pyproject.toml` ↔ `rate_limits.json`
- [x] `tests/integration/test_health.py` — health endpoint returns `200 ok` with correct version

### Documentation
- [x] `docs/TODO.md` — this file
- [x] `docs/cost.md` — token usage tracking

---

## Phase 2 — Game Engine ✅ Complete (commit: d201876)

### Core engine package (`src/cop_thief/game_engine/`)
- [x] `errors.py` — `ConfigError`, `ActionOwnershipError`, `EngineStateError`
- [x] `coordinates.py` — `Pos` type, direction deltas, grid helpers, Chebyshev distance
- [x] `config.py` — `GameConfig` dataclass with validation and `from_dict()`
- [x] `state.py` — mutable `GameState` dataclass with actor helpers
- [x] `actions.py` — `Action`, `ActionResult`, all result-type constants
- [x] `transitions.py` — `apply_action` dispatcher: move, stay, barrier, forfeit
- [x] `win_conditions.py` — post-action win checks (survival, trapped, capture)
- [x] `crumbtrails.py` — trail updates and visibility filtering
- [x] `observations.py` — `build_observation` (observation-safe, no hidden state)
- [x] `hashing.py` — SHA-256 canonical state hash + sub-game seed derivation
- [x] `scoring.py` — `score_subgame` producing `SubGameScore`
- [x] `role_schedule.py` — role alternation across sub-games
- [x] `engine.py` — `GameEngine` public API (initialize, apply, observe, hash, score)

### Tests (27/27 passing, 0 ruff violations)
- [x] `tests/unit/game_engine/test_movement.py` — 8 tests: directions, OOB, capture, survival
- [x] `tests/unit/game_engine/test_barriers.py` — 6 tests: placement, limit, collision
- [x] `tests/unit/game_engine/test_win_conditions.py` — 5 tests: forfeit, trapped, capture
- [x] `tests/unit/game_engine/test_observation.py` — 8 tests: visibility, leak-safety, hashing

---

## Phase 3 — Actor System ✅ Complete (commit: see git log)

### Actor package (`src/cop_thief/actors/`)
- [x] `base.py` — `Actor` abstract base class + `ALL_ACTION_TOKENS` vocabulary
- [x] `random_actor.py` — `RandomLegalActor` (uniform random, avoids forfeit)
- [x] `heuristic_actor.py` — greedy Chebyshev heuristic (cop chases, thief flees)
- [x] `model_bank.py` — `ModelBank` + `ModelMetadata` registry (no weights committed)
- [x] `model_actor.py` — `ModelActor` stub with `_infer` override point (Phase 9)
- [x] `action_mask.py` — 10-slot binary mask (8 dirs + stay + forfeit)

### Tests (26/26 passing, 0 ruff violations)
- [x] `tests/unit/actors/test_random_actor.py` — 6 tests: legality, determinism, forfeit edge
- [x] `tests/unit/actors/test_action_mask.py` — 8 tests: slot mapping, edge cases
- [x] `tests/unit/actors/test_heuristic_actor.py` — 5 tests: direction optimality, fallback
- [x] `tests/unit/actors/test_model_bank.py` — 7 tests: register, get, filter, best

---

## Phase 4 — Game Loop & Authenticated API ✅ Complete (commit: see git log)

### Game package (`src/cop_thief/game/`)
- [x] `state_serializer.py` — `state_to_dict` / `state_from_dict` round-trip
- [x] `action_parser.py` — `action_from_dict` / `action_to_dict`
- [x] `bot_runner.py` — `run_bot_turns` until human's turn or game over
- [x] `orchestrator.py` — `GameOrchestrator`: create match, apply human action

### Database
- [x] `sub_game.current_state_json` — live game state persisted per request
- [x] `session.py` — `StaticPool` for in-memory SQLite (test stability)

### Authentication (complete the stubs from Phase 1)
- [x] JWT bearer middleware in `deps.py` — `CurrentUserDep`
- [x] `POST /api/auth/login` — verify password, return token (was already real)
- [x] `GET /api/me` — return authenticated user profile

### Authenticated game endpoints
- [x] `POST /api/games/human-vs-server` — create match, run bot turns, return first obs
- [x] `POST /api/games/{id}/human-action` — apply move, run bot turns, return observation
- [ ] `POST /api/games/{id}/cancel` — cancel own active match (deferred)

### Public game endpoints
- [x] `GET /api/games` — paginated list (from Phase 1)
- [x] `GET /api/games/{id}` — match detail (from Phase 1)
- [ ] Sub-game and replay endpoints — deferred to later phase

### Frontend, WebSocket, Playwright — deferred

### Tests (20/20 passing, 0 ruff violations)
- [x] `tests/integration/conftest.py` — shared in-memory DB fixture, `client` fixture
- [x] `tests/integration/test_game_endpoints.py` — auth guard, public list/404 tests
- [x] `tests/unit/game/test_state_serializer.py` — 6 round-trip tests
- [x] `tests/unit/game/test_action_parser.py` — 10 parse/serialise tests

---

## Phase 5 — MCP Inter-Group Play ✅ Complete (commit: see git log)

### MCP server (`src/cop_thief/mcp/`)
- [x] `server.py` — HTTP MCP server mounted at `/mcp` (GET info + POST dispatch)
- [x] `tools.py` — `list_supported_rules`, `start_game_vs_server`, `get_observation`, `submit_action`, `get_game_status`, `get_game_history`
- [x] `schemas.py` — `McpRequest`, `McpResponse`, `McpError`, per-tool param models
- [x] `rate_limiter.py` — per-IP sliding-window: games/hour + concurrent limit

### MCP client (`src/cop_thief/mcp/client.py`)
- [x] `RemoteMcpClient` — SSRF-validated HTTP client with DNS re-check
- [x] SSRF blocks localhost, RFC-1918, 169.254.x.x, non-http/https
- [x] Configurable timeout from `config/setup.json`

### Tests (18/18 new, 95 total, 0 ruff violations)
- [x] `tests/unit/mcp/test_rate_limiter.py` — 5 rate limiter tests
- [x] `tests/unit/mcp/test_ssrf.py` — 8 SSRF validation tests
- [x] `tests/integration/test_mcp_endpoint.py` — 5 MCP endpoint integration tests

---

## Phase 6 — Built-In LLM Agent ✅ Complete (commit: see git log)

### Agent package (`src/cop_thief/agents/`)
- [x] `communication_agent.py` — top-level agent: on_action_taken, on_message_received
- [x] `message_generator.py` — actor decision → natural-language message via Gatekeeper
- [x] `message_parser.py` — opponent message → concise summary via Gatekeeper
- [x] `hidden_state_filter.py` — allowlist filter + assert_no_hidden_state guard
- [x] `prompts/game_turn_message.md` — in-character turn message prompt template

### Gatekeeper (full implementation)
- [x] `shared/gatekeeper.py` — RPM rate limit, asyncio queue, exponential backoff
- [x] Per-call logging: model, input tokens, attempt number
- [x] Anthropic SDK integration (`anthropic.AsyncAnthropic`)

### Tests (10/10 new, 105 total, 0 ruff violations)
- [x] `tests/unit/agents/test_hidden_state_filter.py` — 6 filter/assert tests
- [x] `tests/unit/agents/test_gatekeeper.py` — 4 rate-limit/error tests

---

## Phase 7 — Negotiation Strategy ✅ Complete (commit: see git log)

### Negotiation package (`src/cop_thief/negotiation/`)
- [x] `base.py` — `NegotiationStrategy` abstract base class (propose/evaluate/on_result)
- [x] `rule_based.py` — `RuleBasedNegotiator` (preference list + range-based acceptance)
- [x] `performance_table.py` — `PerformanceTable` win/loss tracking by config fingerprint

### Tests (13/13 new, 118 total, 0 ruff violations)
- [x] `tests/unit/negotiation/test_rule_based.py` — 6 tests: validity, accept/reject rules
- [x] `tests/unit/negotiation/test_performance_table.py` — 7 tests: tracking, best_config

---

## Phase 8 — Reports and Email ✅ Complete (commit: see git log)

### Reports package (`src/cop_thief/reports/`)
- [x] `report_schema.py` — `MatchReport` + `SubGameReport` Pydantic schemas
- [x] `report_builder.py` — `build_report(match, sub_games)` → `MatchReport`

### Email package (`src/cop_thief/email_sender/`)
- [x] `email_sender.py` — `EmailSender` with SMTP; no-op when `EMAIL_RECIPIENT` empty
- [x] No hard-coded email addresses (verified by test + automated scan)

### Security checks
- [x] `EMAIL_RECIPIENT` from environment only — confirmed in `email_sender.py`
- [x] Automated test scans module source for literal `@` patterns

### Tests (9/9 new, 127 total, 0 ruff violations)
- [x] `tests/unit/reports/test_report_builder.py` — 5 schema/build tests
- [x] `tests/unit/reports/test_email_sender.py` — 4 no-op/configured/security tests

---

## Phase 9 — Neural Actor Training ✅ Complete (commit: see git log)

### RL environment (`src/cop_thief/actors/`)
- [x] `rl_env.py` — `CopThiefEnv`: Gym-like reset/step with action masking
- [x] `self_play_runner.py` — `SelfPlayRunner` collecting `Trajectory` objects
- [x] `training_config.py` — `TrainingConfig` from dict (no hard-coded values)
- [x] `model_bank.py` — `ModelBank` + `ModelMetadata` (from Phase 3, already committed)

### Training scripts — deferred (need PyTorch/ONNX; not installed by default)

### Tests (12/12 new, 139 total, 0 ruff violations)
- [x] `tests/unit/rl/test_rl_env.py` — 7 env tests: reset/step/reward/termination
- [x] `tests/unit/rl/test_self_play.py` — 5 trajectory tests: alignment, binary masks

---

## Ongoing / Cross-Cutting

- [ ] `docker-compose.yml` — services: backend, frontend, postgres, redis (optional)
- [ ] `Dockerfile` for backend (FastAPI + uvicorn)
- [ ] `Dockerfile` for frontend (Next.js)
- [ ] Admin endpoints: `GET /api/admin/technical-failures`, `POST /api/admin/games/{id}/void`
- [ ] Alembic initial migration (run after Phase 2 models are finalised)
- [ ] CI workflow (GitHub Actions): ruff, pytest, build check
- [ ] Live game publicly visible option (open product question from PRD)
- [ ] Actor-perspective replay labelling in UI (open product question)
- [ ] External MCP opponent allowlist (open engineering decision)
