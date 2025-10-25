"""
Weather Agent - Weather impact analysis
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


class WeatherAgent(BaseAgent):
    """Analyzes weather impact (extreme conditions only)"""
    
    def __init__(self):
        super().__init__(weight=0.5)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        weather = context.get('weather', {})
        
        game_key = f"{prop.team}_vs_{prop.opponent}"
        game_weather = weather.get(game_key, {})
        
        if not game_weather:
            game_key = f"{prop.opponent}_vs_{prop.team}"
            game_weather = weather.get(game_key, {})
        
        if not game_weather:
            return (50, "OVER", [])
        
        temp = game_weather.get('temperature', 70)
        wind = game_weather.get('wind_mph', 0)
        venue = game_weather.get('venue_type', 'outdoor')
        
        if venue == 'dome':
            return (50, "OVER", [])
        
        if temp <= 20 and prop.position in ['QB', 'WR', 'TE']:
            score -= 10
            rationale.append(f"⚠️ EXTREME COLD: {temp}°F affects passing")
        
        if wind >= 20 and prop.position in ['QB', 'WR', 'TE']:
            score -= 12
            rationale.append(f"⚠️ HIGH WIND: {wind} mph")
        
        direction = "OVER" if score >= 50 else "UNDER"
        return (score, direction, rationale)
