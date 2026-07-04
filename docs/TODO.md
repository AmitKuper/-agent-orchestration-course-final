# TODO — Cop & Thief Project Progress

## Milestone 1 — Backend skeleton ✅ Complete (commit: TBD)

- [x] Create `src/cop_thief/` package with full directory structure
- [x] `pyproject.toml` (uv, hatchling, ruff, pytest)
- [x] `.env.example`, `.gitignore`
- [x] `config/setup.json`, `config/rate_limits.json`, `config/game_defaults.json`
- [x] `src/cop_thief/constants.py` — all magic strings/numbers
- [x] `src/cop_thief/shared/version.py` — single version source
- [x] `src/cop_thief/shared/errors.py` — domain error hierarchy
- [x] `src/cop_thief/shared/security.py` — password hashing + JWT
- [x] `src/cop_thief/shared/gatekeeper.py` — LLM gatekeeper stub
- [x] `src/cop_thief/sdk/sdk.py` — SDK entry point stub
- [x] `src/cop_thief/db/base.py` — SQLAlchemy declarative base
- [x] `src/cop_thief/db/session.py` — async engine + session factory
- [x] `src/cop_thief/db/models/` — User, Match, SubGame, GameEvent
- [x] `src/cop_thief/db/repositories.py` — MatchRepository, UserRepository
- [x] `src/cop_thief/schemas/api.py` — Health, Auth, Pagination schemas
- [x] `src/cop_thief/schemas/game.py` — Match, SubGame Pydantic schemas
- [x] `src/cop_thief/webserver/config.py` — Settings (pydantic-settings)
- [x] `src/cop_thief/webserver/main.py` — FastAPI app factory
- [x] `src/cop_thief/api/deps.py` — shared FastAPI dependencies
- [x] `src/cop_thief/api/routes_health.py` — GET /api/health
- [x] `src/cop_thief/api/routes_auth.py` — login/logout/me stubs
- [x] `src/cop_thief/api/routes_games.py` — public history endpoints
- [x] `alembic/` — migration scaffolding
- [x] `tests/unit/test_version.py` — version consistency checks
- [x] `tests/integration/test_health.py` — health endpoint smoke test

---

## Milestone 2 — Game engine integration 🚧 Not started

- [ ] Implement game engine (rules, movement, barriers, observation)
- [ ] `src/cop_thief/game_engine/` package
- [ ] Game orchestrator (`src/cop_thief/game/orchestrator.py`)
- [ ] Player adapters (human, local bot, MCP)
- [ ] Event persistence on every action
- [ ] Replay data generation from events
- [ ] Unit tests for engine rules
- [ ] Integration test: full local game from start to finish

---

## Milestone 3 — Public history and replay 🚧 Not started

- [ ] History API with filters and pagination
- [ ] Game detail and sub-game API
- [ ] Replay frame API
- [ ] Frontend scaffold (Next.js)
- [ ] Board replay component

---

## Milestone 4 — Authentication and human-vs-server 🚧 Not started

- [ ] JWT middleware in `deps.py`
- [ ] Login/logout fully implemented
- [ ] Authenticated new game page
- [ ] Live human game page
- [ ] Action submission
- [ ] Local bot adapter
- [ ] WebSocket live updates (`/ws/games/{match_id}`)

---

## Milestone 5 — MCP server endpoint 🚧 Not started

- [ ] `/mcp` endpoint with MCP tools
- [ ] Guest MCP game initiation
- [ ] MCP observation/action flow
- [ ] Rate limiting for guest MCP

---

## Milestone 6 — External MCP server games 🚧 Not started

- [ ] MCP client adapter
- [ ] SSRF URL validation
- [ ] Capability discovery
- [ ] Propose/accept match flow

---

## Milestone 7 — Hardening and polish 🚧 Not started

- [ ] Responsive UI polish
- [ ] Security hardening
- [ ] Admin / technical-failure view
- [ ] Load testing
