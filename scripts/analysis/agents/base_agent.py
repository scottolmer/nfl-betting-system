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
        'DVOAAgent': 3.5,        # Boosted from 2.0
        'MatchupAgent': 3.0,      # Boosted from 1.8
        'VolumeAgent': 2.5,       # Boosted from 1.2
        'InjuryAgent': 2.0,       # Boosted from 1.5
        'GameScriptAgent': 1.8,   # Boosted from 1.3
        'TrendAgent': 1.5,        # Boosted from 1.0
        'VarianceAgent': 1.2,     # Boosted from 0.8
        'WeatherAgent': 0.8,      # Boosted from 0.5
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
