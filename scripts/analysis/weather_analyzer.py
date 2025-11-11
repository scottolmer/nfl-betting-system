"""
Weather Impact Analyzer - Claude API integration for weather analysis
"""

import os
from anthropic import Anthropic
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class WeatherImpactAnalyzer:
    """Analyzes weather impact on NFL props using Claude API"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_weather_impact(self, team: str, opponent: str, stat_type: str, 
                              weather_data: Dict) -> Dict:
        """
        Analyze how weather affects specific prop
        
        Returns: {
            'passing_impact': -20 to +15 (negative = harder to pass),
            'rushing_impact': -15 to +20 (negative = harder to rush),
            'catching_impact': -20 to +10 (negative = harder to catch),
            'overall_adjustment': -15 to +10 (overall confidence adjustment),
            'reasoning': str
        }
        """
        if not weather_data or not weather_data.get('conditions'):
            return {
                'passing_impact': 0,
                'rushing_impact': 0,
                'catching_impact': 0,
                'overall_adjustment': 0,
                'reasoning': 'No weather data available'
            }
        
        weather_str = self._format_weather(weather_data)
        
        prompt = f"""Analyze how weather affects NFL prop betting.

GAME: {team} @ {opponent}
STAT TYPE: {stat_type}

WEATHER:
{weather_str}

Provide JSON response:
{{
  "passing_impact": <-20 to +15. Heavy rain/snow/wind hurts passing. Negatives mean harder to hit over.>,
  "rushing_impact": <-15 to +20. Cold/snow helps rushing. Mud hurts. Positive = better for rushing.>,
  "catching_impact": <-20 to +10. Wind/rain/snow hurts catching. Cold/clear helps.>,
  "overall_adjustment": <-15 to +10. Net confidence adjustment for this specific stat type.>,
  "reasoning": "<1-2 sentences explaining primary weather factor and impact on {stat_type}>"
}}

Consider:
- Wind speed (>15mph significantly impacts passing)
- Precipitation (snow > rain for rushing benefits)
- Temperature (extreme cold helps running game)
- Humidity (high humidity hurts ball flight)
- Forecast (in-game changes?)

CRITICAL: Respond ONLY with valid JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            import json
            result = json.loads(response_text)
            
            # Validate ranges
            result['passing_impact'] = max(-20, min(15, result.get('passing_impact', 0)))
            result['rushing_impact'] = max(-15, min(20, result.get('rushing_impact', 0)))
            result['catching_impact'] = max(-20, min(10, result.get('catching_impact', 0)))
            result['overall_adjustment'] = max(-15, min(10, result.get('overall_adjustment', 0)))
            
            logger.info(f"Weather analysis for {stat_type}: {result['overall_adjustment']:+d} adjustment")
            return result
            
        except Exception as e:
            logger.error(f"Weather analysis failed: {e}")
            return {
                'passing_impact': 0,
                'rushing_impact': 0,
                'catching_impact': 0,
                'overall_adjustment': 0,
                'reasoning': f'Could not analyze weather: {str(e)}'
            }
    
    def _format_weather(self, weather_data: Dict) -> str:
        """Format weather data for prompt"""
        lines = []
        
        if weather_data.get('conditions'):
            lines.append(f"Conditions: {weather_data['conditions']}")
        if weather_data.get('temp_f'):
            lines.append(f"Temperature: {weather_data['temp_f']}°F")
        if weather_data.get('wind_mph'):
            lines.append(f"Wind: {weather_data['wind_mph']}mph")
        if weather_data.get('wind_direction'):
            lines.append(f"Wind Direction: {weather_data['wind_direction']}")
        if weather_data.get('precipitation_chance'):
            lines.append(f"Rain/Snow Chance: {weather_data['precipitation_chance']}%")
        if weather_data.get('humidity_pct'):
            lines.append(f"Humidity: {weather_data['humidity_pct']}%")
        if weather_data.get('forecast'):
            lines.append(f"Forecast: {weather_data['forecast']}")
        
        return '\n'.join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = WeatherImpactAnalyzer()
    
    # Test
    sample_weather = {
        'conditions': 'Heavy snow expected',
        'temp_f': 28,
        'wind_mph': 18,
        'wind_direction': 'NW',
        'precipitation_chance': 85,
        'forecast': 'Snow continues through 3rd quarter'
    }
    
    result = analyzer.analyze_weather_impact(
        "GB", "CHI", "Pass Yds", sample_weather
    )
    
    print(f"Passing impact: {result['passing_impact']:+d}")
    print(f"Overall adjustment: {result['overall_adjustment']:+d}")
    print(f"Reasoning: {result['reasoning']}")
