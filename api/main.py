"""NFL Betting Analysis API - FastAPI backend for mobile app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import props, parlays, results, auth, players, odds
from api.config import settings
from api.database import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NFL Betting Analysis API",
    version="2.0.0",
    description="""
    Three-pillar NFL analysis platform: DFS, Props, and Fantasy.

    ## Authentication
    JWT Bearer tokens via `/api/auth/login` and `/api/auth/register`.
    Legacy `X-API-Key` still supported for existing endpoints.

    ## Calibrated 6-Agent Engine
    1. **Injury** (weight 4.7) - Player health status
    2. **DVOA** (weight 3.2) - Team efficiency analysis
    3. **Variance** (weight 2.4) - Prop reliability (inverted signal)
    4. **GameScript** (weight 0.82) - Game context (inverted signal)
    5. **Volume** (weight 0.75) - Player usage
    6. **Matchup** (weight 0.5) - Position-specific defense

    ## Key Endpoints
    - `/api/auth/*` - Registration, login, token refresh
    - `/api/players/*` - Player search, ESPN headshots, projections
    - `/api/odds/*` - Multi-book odds, best prices, line movement
    - `/api/props/*` - Prop analysis and filtering
    - `/api/parlays/*` - Pre-built parlay generation
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    props.router,
    prefix="/api/props",
    tags=["Props Analysis"]
)
app.include_router(
    parlays.router,
    prefix="/api/parlays",
    tags=["Parlays"]
)
app.include_router(
    results.router,
    prefix="/api/results",
    tags=["Results"]
)

# Sprint 1: New routers
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)
app.include_router(
    players.router,
    prefix="/api/players",
    tags=["Players"]
)
app.include_router(
    odds.router,
    prefix="/api/odds",
    tags=["Odds"]
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API info"""
    return {
        "message": "NFL Betting Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nfl-betting-api",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 70)
    logger.info("NFL BETTING ANALYSIS API - STARTING")
    logger.info("=" * 70)
    # Initialize database tables (creates new Sprint 1 tables if they don't exist)
    init_db()
    logger.info("Docs available at /docs")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("NFL Betting Analysis API - Shutting down")
