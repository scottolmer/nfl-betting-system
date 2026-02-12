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

## Sprint 2: MARCH — Props Mode [COMPLETE]

### What was built

**Edge service** — Finds where engine confidence exceeds market-implied probability:
- `api/services/edge_service.py` — Kelly Criterion bet sizing, edge detection, implied probability conversion
- Added `GET /api/props/edge-finder` — Find biggest edges across all props for a week
- Added `GET /api/props/bet-sizing` — Kelly-based unit recommendations for any prop

**Bets router** — Server-synced bet tracking (replaces local AsyncStorage):
- `api/routers/bets.py` — POST /save, GET /mine (filtered by mode/week/status), PUT /{id}/status, GET /analytics
- Analytics endpoint returns win rate, breakdowns by mode and week

**7 shared components** (reused across all three pillars):
- `components/player/PlayerCard.tsx` — Headshot (or initials fallback), name, team, position
- `components/player/AgentBreakdownCard.tsx` — Color-coded bars for each agent's score, weight, direction
- `components/player/StatTrendRow.tsx` — L5/L10 stats with mini sparkline and trend arrows
- `components/odds/MultiBookOddsTable.tsx` — Book comparison table, best price highlighted in green
- `components/odds/LineMovementChart.tsx` — Horizontal bar chart of line changes over time
- `components/game/GameEnvironmentCard.tsx` — Implied total, spread, pace, venue pills
- `components/betting/BetSizeSuggestion.tsx` — Unit recommendation box with Kelly %, edge, risk level

**4 Props mode screens:**
- `screens/props/PropsHomeScreen.tsx` — Top picks feed, stat category filters, player search, pull-to-refresh, edge finder button
- `screens/props/PropDetailScreen.tsx` — Full player card + prop line + bet sizing + agent breakdown + multi-book odds + line chart + top reasons
- `screens/props/EdgeFinderScreen.tsx` — Sorted list of biggest edges with unit recommendations
- `screens/props/BetSlipScreen.tsx` — Filtered bet history (all/pending/placed/graded), server-synced, auth-gated

**Navigation overhaul:**
- `components/navigation/ModeSwitcher.tsx` — DFS | Props | Fantasy pill toggle at top of app
- `navigation/PropsNavigator.tsx` — Stack navigator for Props screens
- `navigation/DFSNavigator.tsx` — "Coming Soon" placeholder
- `navigation/FantasyNavigator.tsx` — "Coming Soon" placeholder
- Rewrote `navigation/AppNavigator.tsx` — Mode switcher at top, bottom tabs (Home / My Bets / Profile), mode-aware Home tab
- Rewrote `App.tsx` — Wrapped in AuthProvider + ModeProvider

**Dependencies added:**
- `@react-navigation/native-stack` for stack navigation
- `api/routers/bets.py` registered in `api/main.py`

### Key decisions
- **Shared components first** — PlayerCard, AgentBreakdownCard, MultiBookOddsTable are designed to be reused by DFS and Fantasy modes without modification
- **Edge = engine confidence minus implied probability** — props with >2% edge surface in EdgeFinder
- **Quarter-Kelly sizing** — conservative bet sizing, capped at 3 units max
- **Server-synced bets** — UserBet table replaces AsyncStorage, enabling cross-device sync and analytics

## Sprint 3: APRIL — DFS Mode [COMPLETE]

### What was built

**DFS service** — Wraps the existing CorrelationAnalyzer for DFS-specific use:
- `api/services/dfs_service.py` — Platform line mapping (PrizePicks/Underdog stat names), correlation scoring via CorrelationAnalyzer, flex play optimization (highest confidence + lowest correlation impact), greedy slip suggestion generator, line comparison (platform vs sportsbook consensus)
- `api/routers/dfs.py` — 5 endpoints:
  - `GET /lines` — DFS lines filtered by week, platform, position, stat type
  - `POST /correlation-score` — Real-time correlation scoring for a set of picks
  - `POST /optimize-flex` — Find optimal flex pick designation
  - `GET /suggestions` — Engine-generated optimal slips
  - `GET /line-comparison/{player_id}` — Platform line vs sportsbook consensus with discrepancy notes

**5 DFS components:**
- `components/dfs/SlipSummaryBar.tsx` — Floating bottom bar: pick count, correlation risk badge (color-coded), adjusted confidence, Review button
- `components/dfs/CorrelationIndicator.tsx` — Full mode: visual gauge bar + risk badge + penalty text + expandable warnings. Compact mode: dot + label + penalty for inline use
- `components/dfs/PlatformLineBadge.tsx` — Platform line vs sportsbook consensus comparison, shows difference and directional lean hint
- `components/dfs/AgentReasoningCard.tsx` — "Why this pick?" card with top 3 agents ranked by impact (weight * |score - 50|), includes human-readable agent descriptions
- `components/dfs/FlexPlayOptimizer.tsx` — Recommended flex pick with FLEX badge, flex score, reason text, and alternative candidates list

**4 DFS screens:**
- `screens/dfs/DFSHomeScreen.tsx` — Platform selector (PrizePicks/Underdog), "Build a Slip" CTA, Suggested Slips card, How It Works feature grid
- `screens/dfs/SlipBuilderScreen.tsx` — Two modes: (1) Browse mode with search bar, player list with checkmark toggles, compact correlation indicator, SlipSummaryBar; (2) Review mode showing picked players, full CorrelationIndicator, FlexPlayOptimizer, AgentReasoningCard
- `screens/dfs/DFSPlayerDetailScreen.tsx` — PlayerCard + PlatformLineBadge + engine projection + sportsbook comparison + AgentBreakdownCard + AgentReasoningCard
- `screens/dfs/SuggestedSlipsScreen.tsx` — FlatList of engine-generated slips, each showing ranked picks with FLEX tags, correlation indicator, combined confidence score

**Navigation update:**
- Rewrote `navigation/DFSNavigator.tsx` — Real stack navigator with DFSHome, SlipBuilder, DFSPlayerDetail, SuggestedSlips screens (replaced "Coming Soon" placeholder)
- Registered `api/routers/dfs.py` in `api/main.py`

### Key decisions
- **Reuses CorrelationAnalyzer** — DFS correlation scoring wraps the existing proven correlation detection logic, no duplication
- **Greedy slip generation** — Suggestions built by iteratively selecting highest-confidence picks that don't create high correlation with existing picks
- **Flex optimization** — Flex candidate scored by confidence minus correlation penalty, balancing individual strength with slip-level risk
- **Platform-aware stat mapping** — Each DFS platform (PrizePicks, Underdog) has its own stat name conventions mapped to internal types

## Sprint 4: MAY — Fantasy Mode [NOT STARTED]

Sleeper API integration, start/sit rankings, waiver wire, matchup heatmap, trade analyzer.

## Sprint 5: JUNE — Polish & Cross-Pillar Integration [NOT STARTED]

Unified home feed, full player intelligence cards, universal search.

## Sprint 6: JULY — Subscription & Automated Pipeline [NOT STARTED]

Stripe payments, feature gating, automated odds/projection pipeline, push notifications.

## Sprint 7: AUGUST — Testing & App Store Launch [NOT STARTED]

Full test suite, performance optimization, App Store/Play Store submission, production infrastructure.
