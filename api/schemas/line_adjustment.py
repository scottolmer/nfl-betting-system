"""Pydantic schemas for line adjustment (Pick 6 support)"""

from pydantic import BaseModel, Field


class LineAdjustmentRequest(BaseModel):
    """Request to adjust line and recalculate confidence"""

    week: int = Field(..., ge=1, le=18, description="NFL week number")
    player_name: str = Field(..., description="Player name (e.g., 'travis kelce')")
    stat_type: str = Field(..., description="Stat type (e.g., 'Rec Yds', 'Pass Yds')")
    bet_type: str = Field(..., description="OVER or UNDER")
    original_line: float = Field(..., description="Original line from regular props")
    new_line: float = Field(..., description="New line from Pick 6 or other platform")

    model_config = {
        "json_schema_extra": {
            "example": {
                "week": 9,
                "player_name": "travis kelce",
                "stat_type": "Rec Yds",
                "bet_type": "OVER",
                "original_line": 56.5,
                "new_line": 58.5
            }
        }
    }


class LineAdjustmentResponse(BaseModel):
    """Response with recalculated confidence for adjusted line"""

    player_name: str
    team: str
    stat_type: str
    bet_type: str
    original_line: float
    new_line: float
    original_confidence: float = Field(..., description="Confidence at original line")
    adjusted_confidence: float = Field(..., description="Confidence at new line")
    confidence_change: float = Field(..., description="Change in confidence (new - original)")
    recommendation: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "player_name": "travis kelce",
                "team": "KC",
                "stat_type": "Rec Yds",
                "bet_type": "OVER",
                "original_line": 56.5,
                "new_line": 58.5,
                "original_confidence": 66.0,
                "adjusted_confidence": 62.5,
                "confidence_change": -3.5,
                "recommendation": "MODERATE OVER"
            }
        }
    }
