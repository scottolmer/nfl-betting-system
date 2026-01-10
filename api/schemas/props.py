"""Pydantic schemas for prop analysis requests/responses"""

from pydantic import BaseModel, Field
from typing import Dict, Any


class PropAnalysisResponse(BaseModel):
    """Response model for individual prop analysis"""

    player_name: str
    team: str
    opponent: str
    position: str
    stat_type: str
    bet_type: str = Field(..., description="OVER or UNDER")
    line: float
    confidence: float = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    recommendation: str = Field(..., description="STRONG/MODERATE/LEAN OVER/UNDER or AVOID")
    edge_explanation: str = Field(..., description="Explanation of the edge")
    agent_breakdown: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Agent scores: {agent_name: {score, weight, direction}}"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "player_name": "patrick mahomes",
                "team": "KC",
                "opponent": "BUF",
                "position": "QB",
                "stat_type": "Pass Yds",
                "bet_type": "OVER",
                "line": 275.5,
                "confidence": 72.5,
                "recommendation": "STRONG OVER",
                "edge_explanation": "STRONG OVER edge primarily driven by: GameScript (8.2), DVOA (6.5), Matchup (4.1)",
                "agent_breakdown": {
                    "GameScript": {"score": 78, "weight": 2.2, "direction": "OVER"},
                    "DVOA": {"score": 75, "weight": 2.0, "direction": "OVER"},
                    "Matchup": {"score": 70, "weight": 1.5, "direction": "OVER"}
                }
            }
        }
    }


class PropAnalysisMetadata(BaseModel):
    """Metadata about prop analysis results"""

    week: int
    total_analyzed: int
    filters_applied: Dict[str, Any]
    min_confidence: int
