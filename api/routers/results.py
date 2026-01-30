"""
Results Router - API endpoints for parlay scoring and results

Exposes auto_scorer.py functionality via REST API
"""

from fastapi import APIRouter, HTTPException, Query, Path as PathParam
from pydantic import BaseModel, Field
from typing import Optional, List
from api.services.results_service import results_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ScoreWeekRequest(BaseModel):
    """Request body for scoring a week"""
    week: int = Field(..., ge=1, le=18, description="NFL week number (1-18)")
    dry_run: bool = Field(False, description="Preview scoring without saving to database")
    force: bool = Field(False, description="Re-score already scored parlays")


class ScoreWeekResponse(BaseModel):
    """Response for scoring a week"""
    success: bool
    week: int
    parlays_scored: int
    wins: int
    losses: int
    pending: int
    dry_run: bool = False
    message: Optional[str] = None
    error: Optional[str] = None
    results: List[dict] = []


class SyncParlayLeg(BaseModel):
    """Leg data from mobile app"""
    player_name: str
    team: str
    stat_type: str
    line: float
    bet_type: str
    confidence: float


class SyncParlayRequest(BaseModel):
    """Request body for syncing parlay from mobile"""
    id: str
    week: int
    legs: List[SyncParlayLeg]
    combined_confidence: float
    backend_id: Optional[str] = None


class SyncParlayResponse(BaseModel):
    """Response for syncing parlay"""
    success: bool
    parlay_id: str
    synced: bool
    legs_synced: int = 0
    message: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/score-week", response_model=ScoreWeekResponse)
async def score_week(request: ScoreWeekRequest):
    """
    Score all parlays for a specific week

    Triggers auto_scorer.py for the specified week. Loads CSV files,
    scores all pending parlays, and updates database with results.

    **Example:**
    ```json
    {
        "week": 17,
        "dry_run": false,
        "force": false
    }
    ```

    **Returns:**
    - `parlays_scored`: Number of parlays scored
    - `wins`: Number of winning parlays
    - `losses`: Number of losing parlays
    - `pending`: Number of parlays with partial scores
    - `results`: Detailed results for each parlay
    """
    try:
        logger.info(f"Scoring week {request.week} (dry_run={request.dry_run}, force={request.force})")

        result = results_service.score_week(
            week=request.week,
            dry_run=request.dry_run,
            force=request.force
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Failed to score week')
            )

        return ScoreWeekResponse(**result)

    except Exception as e:
        logger.error(f"Error scoring week {request.week}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parlay-results")
async def get_parlay_results(
    week: int = Query(..., ge=1, le=18, description="NFL week number (1-18)")
):
    """
    Get all graded parlays for a specific week

    Returns all parlays for the specified week with their legs and results.
    Useful for displaying results in mobile app.

    **Example:**
    ```
    GET /api/results/parlay-results?week=17
    ```

    **Returns:**
    ```json
    {
        "success": true,
        "week": 17,
        "parlay_count": 5,
        "parlays": [
            {
                "parlay_id": "uuid",
                "week": 17,
                "confidence_score": 82.5,
                "status": "won",
                "legs_hit": 3,
                "legs_total": 3,
                "legs": [...]
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"Fetching parlay results for week {week}")

        result = results_service.get_parlay_results_for_week(week)

        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch parlay results"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching parlay results for week {week}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parlay-result/{parlay_id}")
async def get_parlay_result(
    parlay_id: str = PathParam(..., description="Parlay ID")
):
    """
    Get result for a specific parlay

    Returns detailed information for a single parlay including all legs
    and their results.

    **Example:**
    ```
    GET /api/results/parlay-result/uuid-1234
    ```

    **Returns:**
    ```json
    {
        "success": true,
        "parlay_id": "uuid-1234",
        "week": 17,
        "confidence_score": 82.5,
        "status": "won",
        "legs_hit": 3,
        "legs_total": 3,
        "legs": [
            {
                "player": "Patrick Mahomes",
                "prop_type": "Pass Yds",
                "bet_type": "OVER",
                "line": 250.5,
                "actual_value": 320,
                "result": 1
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"Fetching result for parlay {parlay_id}")

        result = results_service.get_parlay_result(parlay_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Parlay {parlay_id} not found"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching parlay result {parlay_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-parlay", response_model=SyncParlayResponse)
async def sync_parlay(request: SyncParlayRequest):
    """
    Sync a parlay from mobile app to backend database

    Allows mobile app to sync placed parlays to backend for future scoring.
    Creates entry in backend database with status='pending'.

    **Example:**
    ```json
    {
        "id": "mobile-uuid-1234",
        "week": 17,
        "combined_confidence": 82.5,
        "legs": [
            {
                "player_name": "Patrick Mahomes",
                "team": "KC",
                "stat_type": "Pass Yds",
                "line": 250.5,
                "bet_type": "OVER",
                "confidence": 85.0
            }
        ]
    }
    ```

    **Returns:**
    ```json
    {
        "success": true,
        "parlay_id": "uuid",
        "synced": true,
        "legs_synced": 1
    }
    ```
    """
    try:
        logger.info(f"Syncing parlay from mobile: {request.id} (week {request.week})")

        # Convert request to dict for service
        parlay_data = request.dict()

        result = results_service.sync_parlay_from_mobile(parlay_data)

        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail="Failed to sync parlay"
            )

        return SyncParlayResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing parlay {request.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
