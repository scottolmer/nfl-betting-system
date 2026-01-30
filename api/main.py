"""NFL Betting Analysis API - FastAPI backend for mobile app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import props, parlays, results
from api.config import settings
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
    version="1.0.0",
    description="""
    FastAPI backend for mobile NFL betting analysis app.

    ## Features
    * 9-agent prop analysis system (95%+ code reuse from existing CLI)
    * Pre-built parlay generation
    * Real-time prop filtering and search
    * Minimal API key authentication (Phase 1)

    ## Authentication
    All endpoints require `X-API-Key` header.

    Development key: `dev_test_key_12345`

    ## Agents
    The analysis system uses 9 specialized agents:
    1. **DVOA** (weight 2.0) - Team efficiency analysis
    2. **Matchup** (weight 1.5) - Position-specific defensive matchups
    3. **Volume** (weight 1.5) - Player usage (snap/target share)
    4. **GameScript** (weight 2.2) - Game context (total, spread)
    5. **Variance** (weight 1.2) - Prop type reliability
    6. **Trend** (weight 1.0) - Recent performance trends
    7. **Injury** (weight 3.0) - Player health status
    8. **HitRate** (weight 2.0) - Historical accuracy vs line
    9. **Weather** (weight 0.0) - Weather impact (disabled)

    Each prop receives a confidence score (0-100) based on weighted agent analysis.
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
    logger.info("🏈 NFL BETTING ANALYSIS API - STARTING")
    logger.info("=" * 70)
    logger.info("FastAPI backend for mobile app")
    logger.info("95%+ code reuse from existing analysis engine")
    logger.info("Docs available at /docs")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("NFL Betting Analysis API - Shutting down")
