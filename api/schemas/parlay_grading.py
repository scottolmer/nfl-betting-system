from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ParlayLegRequest(BaseModel):
    """A single leg in a parlay to be graded."""
    player_name: str
    team: str
    opponent: str
    stat_type: str
    bet_type: str  # OVER or UNDER
    line: float
    confidence: float = Field(..., ge=0, le=100)
    position: Optional[str] = None

class ParlayGradeRequest(BaseModel):
    """Request to grade a parlay (list of legs)."""
    legs: List[ParlayLegRequest]

class SwapSuggestion(BaseModel):
    """A suggested replacement leg."""
    original_leg_index: int
    new_leg: ParlayLegRequest
    reason: str

class ParlayGradeResponse(BaseModel):
    """The result of grading a parlay."""
    grade: str = Field(..., description="Letter grade (A+/A/B/C/D/F)")
    adjusted_confidence: float = Field(..., ge=0, le=100, description="Confidence adjusted for correlation")
    original_confidence: float = Field(..., ge=0, le=100)
    recommendation: str = Field(..., description="ACCEPT / MODIFY / AVOID")
    analysis: str = Field(..., description="Detailed AI analysis text")
    risk_factors: List[str] = Field(default_factory=list, description="Specific identified risks")
    
    # Value Analysis
    implied_probability: float = Field(..., ge=0, le=100, description="Probability implied by book odds")
    true_probability: float = Field(..., ge=0, le=100, description="Our estimated probability")
    value_edge: float = Field(..., description="Difference (True - Implied). Positive is good value.")
    
    # Smart Swaps
    suggestions: List[SwapSuggestion] = Field(default_factory=list)
