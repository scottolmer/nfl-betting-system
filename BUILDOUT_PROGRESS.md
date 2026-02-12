# Three-Pillar NFL App Buildout Progress

**Goal:** Transform the proven NFL betting analysis engine (55.7% win rate, +6.3% ROI) into a consumer-ready mobile app covering DFS, Props, and Fantasy — all powered by the same projection engine.

**Timeline:** Feb 2026 — Sep 2026 (7 sprints)

---

## Sprint 1: FEBRUARY — Foundation & Shared Infrastructure [COMPLETE]

### What was built

**Database layer** — 6 new SQLAlchemy models added to `api/database.py`:
- `Player` — NFL players with ESPN headshot URLs
- `User` — App users with subscription/trial tracking
- `UserBet` — Cross-mode bet storage (DFS, Props, Fantasy)
- `PlayerProjection` — Engine-generated projections with agent breakdowns
- `BookOdds` — Multi-book odds snapshots
- `LineMovement` — Historical line movement tracking

**JWT authentication** — Replaced single API key with proper user auth:
- `api/core/jwt_auth.py` — Token creation/validation, password hashing, FastAPI dependencies
- `api/routers/auth.py` — POST /register, /login, /refresh, GET /me
- 7-day free trial auto-granted on registration

**Player service** — ESPN integration for roster data:
- `api/services/player_service.py` — Roster sync from ESPN public API, search, headshot URLs
- `api/routers/players.py` — GET /search, /{id}, /{id}/projections, POST /sync/{team}, /sync-all

**Odds service** — The Odds API integration for multi-book odds:
- `api/services/odds_service.py` — Fetch player props, store odds, best price finder, line movement
- `api/routers/odds.py` — GET /player/{id}, /best-prices, /movement/{id}, POST /fetch-week

**Projection service** — The core engine (single source of truth for all pillars):
- `api/services/projection_service.py` — Derives implied projections from odds pricing, runs agent analysis against consensus lines, produces confidence scores and agent breakdowns

**Mobile foundation:**
- `mobile/src/services/authService.ts` — JWT storage, login/register/refresh
- `mobile/src/services/playerService.ts` — Player search, odds, projections
- `mobile/src/contexts/AuthContext.tsx` — Auth state with auto-refresh
- `mobile/src/contexts/ModeContext.tsx` — DFS / Props / Fantasy mode switcher
- Updated `mobile/src/types/index.ts` with all new TypeScript interfaces
- Updated `mobile/src/services/api.ts` with JWT auto-attach and 401 refresh

**Config & dependencies:**
- `api/config.py` — Added JWT settings
- `api/main.py` — Registered 3 new routers, v2.0 description, init_db on startup
- `api/dependencies.py` — Exports get_current_user alongside legacy get_api_key
- `requirements.txt` — Added python-jose, passlib, python-multipart, fastapi, uvicorn, httpx

### Key architecture decisions
- **ProjectionService is the single source of truth** — all three pillars consume the same projections
- **Betting lines are the baseline projection model** — odds pricing derives the implied mean, agents find where lines are wrong
- **JWT auth coexists with legacy API key** — backward compatible with existing endpoints

---

## Sprint 2: MARCH — Props Mode [NOT STARTED]

Full props experience: edge finder, multi-book odds comparison, bet sizing, server-synced bets, shared player/odds components reused by all pillars.

## Sprint 3: APRIL — DFS Mode [NOT STARTED]

DFS slip builder with correlation scoring, flex play optimization, platform line comparisons, engine-generated suggestions.

## Sprint 4: MAY — Fantasy Mode [NOT STARTED]

Sleeper API integration, start/sit rankings, waiver wire, matchup heatmap, trade analyzer.

## Sprint 5: JUNE — Polish & Cross-Pillar Integration [NOT STARTED]

Unified home feed, full player intelligence cards, universal search.

## Sprint 6: JULY — Subscription & Automated Pipeline [NOT STARTED]

Stripe payments, feature gating, automated odds/projection pipeline, push notifications.

## Sprint 7: AUGUST — Testing & App Store Launch [NOT STARTED]

Full test suite, performance optimization, App Store/Play Store submission, production infrastructure.
