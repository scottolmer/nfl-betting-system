"""
Base Agent Class - All agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class BaseAgent(ABC):
    """Base class for all analysis agents"""
    
    def __init__(self, weight: float = 1.0):
        self.weight = weight
        self.name = self.__class__.__name__
    
    @abstractmethod
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        """
        Analyze a prop
        
        Returns:
            score: 0-100 confidence (>50 = OVER, <50 = UNDER)
            direction: "OVER" or "UNDER"
            rationale: List of explanation strings
        """
        pass
    
    def get_weighted_score(self, raw_score: float) -> float:
        """Apply agent weight to score"""
        centered = (raw_score - 50) * self.weight
        return max(0, min(100, 50 + centered))


class AgentConfig:
    """Configuration for agent weights"""
    
    WEIGHTS = {
        'DVOAAgent': 2.0,        # REDUCED from 4.0 - was overconfident (47.9% accuracy when confident)
        'MatchupAgent': 1.5,      # Unchanged - performing acceptably (50.6% accuracy)
        'VolumeAgent': 1.5,       # REDUCED from 2.5 - was overconfident (46.3% accuracy when confident)
        'GameScriptAgent': 2.2,   # Unchanged
        'TrendAgent': 1.0,        # REDUCED from 1.8 - was overconfident (40.6% accuracy when confident)
        'VarianceAgent': 1.2,     # Unchanged - performing acceptably (51.7% accuracy)
        'InjuryAgent': 3.0,       # Unchanged - CRITICAL data, not overconfident
        'WeatherAgent': 1.3,      # Unchanged
    }
    
    THRESHOLDS = {
        'STRONG_OVER': 70,
        'MODERATE_OVER': 60,
        'LEAN_OVER': 55,
        'AVOID': (45, 55),
        'LEAN_UNDER': 45,
        'MODERATE_UNDER': 40,
        'STRONG_UNDER': 30,
    }
    
    @classmethod
    def get_recommendation(cls, confidence: int, direction: str) -> str:
        """Convert confidence score to recommendation string"""
        if direction == 'AVOID':
            return 'AVOID'
        
        if direction == 'OVER':
            if confidence >= cls.THRESHOLDS['STRONG_OVER']:
                return 'STRONG OVER'
            elif confidence >= cls.THRESHOLDS['MODERATE_OVER']:
                return 'MODERATE OVER'
            elif confidence >= cls.THRESHOLDS['LEAN_OVER']:
                return 'LEAN OVER'
            else:
                return 'AVOID'
        else:
            if confidence <= cls.THRESHOLDS['STRONG_UNDER']:
                return 'STRONG UNDER'
            elif confidence <= cls.THRESHOLDS['MODERATE_UNDER']:
                return 'MODERATE UNDER'
            elif confidence <= cls.THRESHOLDS['LEAN_UNDER']:
                return 'LEAN UNDER'
            else:
                return 'AVOID'
