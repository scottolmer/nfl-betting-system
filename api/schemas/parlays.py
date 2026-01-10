"""Pydantic schemas for parlay requests/responses"""

from pydantic import BaseModel, Field
from typing import List


class ParlayLegResponse(BaseModel):
    """Individual leg within a parlay"""

    player_name: str
    team: str
    stat_type: str
    bet_type: str = Field(..., description="OVER or UNDER")
    line: float
    confidence: float = Field(..., ge=0, le=100)


class ParlayResponse(BaseModel):
    """Response model for a parlay"""

    parlay_type: str = Field(..., description="Type of parlay (2-leg, 3-leg, etc.)")
    combined_confidence: float = Field(..., ge=0, le=100, description="Combined confidence score")
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    rationale: str = Field(..., description="Explanation of why this parlay was built")
    legs: List[ParlayLegResponse]

    model_config = {
        "json_schema_extra": {
            "example": {
                "parlay_type": "3-leg",
                "combined_confidence": 68.5,
                "risk_level": "MEDIUM",
                "rationale": "Balanced parlay with diverse positions and game contexts",
                "legs": [
                    {
                        "player_name": "patrick mahomes",
                        "team": "KC",
                        "stat_type": "Pass Yds",
                        "bet_type": "OVER",
                        "line": 275.5,
                        "confidence": 72.5
                    },
                    {
                        "player_name": "josh allen",
                        "team": "BUF",
                        "stat_type": "Pass TDs",
                        "bet_type": "OVER",
                        "line": 1.5,
                        "confidence": 67.0
                    },
                    {
                        "player_name": "travis kelce",
                        "team": "KC",
                        "stat_type": "Rec Yds",
                        "bet_type": "OVER",
                        "line": 56.5,
                        "confidence": 66.0
                    }
                ]
            }
        }
    }
