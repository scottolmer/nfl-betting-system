"""
Data models for NFL betting analysis system
"""

from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
import numpy as np
import logging # Keep logging import if other parts use it

# logger = logging.getLogger(__name__) # REMOVE logger instance if only used for debug


@dataclass
class PlayerProp:
    """Represents a single player prop bet"""
    player_name: str
    team: str
    opponent: str
    position: str
    stat_type: str
    line: float

    game_total: Optional[float] = None
    spread: Optional[float] = None
    is_home: bool = True
    week: int = 7

    direction: Literal['OVER', 'UNDER', 'AVOID'] = 'OVER'
    bet_type: Literal['OVER', 'UNDER'] = 'OVER'
    confidence: int = 0
    agent_scores: dict = field(default_factory=dict)
    rationale_points: List[str] = field(default_factory=list)


@dataclass
class PropAnalysis:
    """Complete analysis result for a prop"""
    prop: PlayerProp
    final_confidence: int
    recommendation: str
    rationale: List[str]
    agent_breakdown: dict
    edge_explanation: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Parlay:
    """Represents a parlay bet"""
    legs: List[PropAnalysis]
    parlay_type: str
    risk_level: str
    rationale: str
    correlation_bonus: int = 0

    @property
    def combined_confidence(self) -> int:
        """Calculate combined confidence with bonus"""
        if not self.legs:
            return 50

        leg_confidences = [leg.final_confidence for leg in self.legs]

        # --- *** REMOVED DEBUGGING PRINT *** ---

        avg_conf = np.mean(leg_confidences) if leg_confidences else 50

        final_conf = avg_conf + self.correlation_bonus

        # --- *** REMOVED DEBUGGING PRINT *** ---

        capped_conf = int(max(0, min(100, final_conf)))

        # --- *** REMOVED DEBUGGING PRINT *** ---

        return capped_conf


    @property
    def expected_value(self) -> float:
        """Simple EV calculation"""
        return (self.combined_confidence - 50) * 2

    @property
    def recommended_units(self) -> float:
        """Get unit size based on risk and confidence"""
        conf = self.combined_confidence

        if self.risk_level == "HIGH":
            return 1.0 if conf >= 70 else 0.5
        if self.risk_level == "MODERATE":
            return 1.5 if conf >= 70 else 1.0
        if self.risk_level == "LOW":
            return 1.5 if conf >= 65 else 1.0

        return 0.5