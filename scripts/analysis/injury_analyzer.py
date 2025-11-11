"""
Enhanced Injury Analysis using Claude API
"""

import os
from anthropic import Anthropic
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class InjuryAnalyzer:
    """Analyzes injury reports using Claude API for nuanced context"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_player_injury_context(self, player_name: str, team: str, position: str, 
                                     injury_report: str) -> Dict:
        """
        Analyze injury impact for a specific player
        Returns: {
            'severity_score': 0-100 (100 = no concern, 0 = definitely out),
            'confidence_adjustment': -20 to +5 (how much to adjust prop confidence),
            'reasoning': str
        }
        """
        if not injury_report:
            return {
                'severity_score': 100,
                'confidence_adjustment': 0,
                'reasoning': 'No injury report available'
            }
        
        prompt = f"""Analyze injury impact for NFL player prop betting.

Player: {player_name} ({position}, {team})

Injury Report:
{injury_report[:2000]}  # Limit to avoid token limits

Provide JSON response:
{{
  "severity_score": <0-100, where 100=fully healthy, 75=questionable but likely plays, 50=true toss-up, 25=doubtful, 0=ruled out>,
  "confidence_adjustment": <-20 to +5, how much to adjust betting confidence. -20 for major concerns, -10 for moderate, -5 for minor, 0 for no impact, +5 if injury helps prop (e.g. WR1 out helps WR2)>,
  "reasoning": "<2-3 sentences explaining severity, practice participation trends, and betting impact>"
}}

Consider:
- Injury designation (Out/Doubtful/Questionable/Probable)
- Practice participation (DNP/Limited/Full)
- Injury type and position impact
- Historical return timelines
- Whether injury limits mobility/catching/throwing

CRITICAL: Respond ONLY with valid JSON. No other text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            import json
            result = json.loads(response_text)
            
            # Validate
            result['severity_score'] = max(0, min(100, result.get('severity_score', 100)))
            result['confidence_adjustment'] = max(-20, min(5, result.get('confidence_adjustment', 0)))
            
            logger.info(f"Injury analysis for {player_name}: {result['severity_score']}% healthy, {result['confidence_adjustment']:+d} adjustment")
            return result
            
        except Exception as e:
            logger.error(f"Injury analysis failed for {player_name}: {e}")
            return {
                'severity_score': 85,  # Conservative default
                'confidence_adjustment': -5,
                'reasoning': 'Could not parse injury context, applying conservative adjustment'
            }
    
    def analyze_team_injury_impact(self, team: str, opponent: str, injury_report: str) -> Dict:
        """
        Analyze how injuries affect team's offensive/defensive efficiency
        Returns: {
            'offensive_impact': -15 to +10,
            'defensive_impact': -15 to +10,
            'key_injuries': List[str]
        }
        """
        if not injury_report:
            return {'offensive_impact': 0, 'defensive_impact': 0, 'key_injuries': []}
        
        prompt = f"""Analyze how injuries affect {team}'s team performance vs {opponent}.

Injury Report:
{injury_report[:2000]}

Provide JSON:
{{
  "offensive_impact": <-15 to +10. Negative if injuries hurt offense. Positive if opponent defensive injuries help offense.>,
  "defensive_impact": <-15 to +10. Negative if injuries hurt defense. Positive if opponent offensive injuries help defense.>,
  "key_injuries": ["Player1 (impact)", "Player2 (impact)"]
}}

Focus on: OL injuries (hurt QB/RB props), WR1 out (helps WR2), key defenders out (helps opposing offense).

RESPOND ONLY WITH JSON."""

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
            
            result['offensive_impact'] = max(-15, min(10, result.get('offensive_impact', 0)))
            result['defensive_impact'] = max(-15, min(10, result.get('defensive_impact', 0)))
            
            return result
            
        except Exception as e:
            logger.error(f"Team injury analysis failed: {e}")
            return {'offensive_impact': 0, 'defensive_impact': 0, 'key_injuries': []}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = InjuryAnalyzer()
    
    # Test with sample
    sample_report = """
    Tua Tagovailoa (QB) - Ankle - Questionable
    - Wednesday: Limited
    - Thursday: Limited
    - Friday: Full
    
    Tyreek Hill (WR) - Wrist - Probable
    - Wednesday: Full
    - Thursday: Full
    - Friday: Full
    """
    
    result = analyzer.analyze_player_injury_context(
        "Tua Tagovailoa", "MIA", "QB", sample_report
    )
    
    print(f"Severity: {result['severity_score']}")
    print(f"Adjustment: {result['confidence_adjustment']:+d}")
    print(f"Reasoning: {result['reasoning']}")
