"""
Matchup Narrative Generator using Gemini API
"""

import os
import logging
from typing import Dict
from ..core.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class MatchupNarrativeGenerator:
    """Generates human-readable matchup analysis using Gemini API"""
    
    def __init__(self):
        # Initialize Gemini instead of Claude
        try:
            self.client = GeminiClient(model_name="gemini-2.0-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    def generate_prop_narrative(self, prop: Dict, agent_breakdown: Dict, 
                                confidence: int, context: Dict) -> str:
        """
        Generate compelling narrative for a specific prop
        """
        if not self.client or not self.client.is_available:
             return f"Analysis: {confidence}% confidence on {prop.get('player_name')} {prop.get('stat_type')} {prop.get('bet_type')} {prop.get('line')}"

        # Extract key data
        player = prop.get('player_name', 'Unknown')
        team = prop.get('team', '')
        opponent = prop.get('opponent', '')
        stat = prop.get('stat_type', '')
        line = prop.get('line', 0)
        bet_type = prop.get('bet_type', 'OVER')
        
        # Build context summary
        dvoa_summary = self._summarize_dvoa(team, opponent, context)
        injury_summary = self._summarize_injuries(context.get('injuries', ''))
        
        prompt = f"""Write a 2-3 paragraph betting narrative for this NFL prop.

PROP: {player} ({team}) - {stat} {bet_type} {line} vs {opponent}
CONFIDENCE: {confidence}%
RECOMMENDATION: {"BET" if confidence >= 65 else "LEAN" if confidence >= 55 else "AVOID"}

AGENT SCORES:
{self._format_agent_scores(agent_breakdown)}

CONTEXT:
{dvoa_summary}
{injury_summary}

Write a compelling narrative that:
1. Opens with the key insight (why bet or avoid)
2. Explains 2-3 main factors driving the confidence score
3. Mentions any counterpoints or risks
4. Ends with actionable takeaway

Style: Conversational but analytical. Like ESPN insider analysis.
Length: 2-3 paragraphs, ~150-200 words total.
Avoid: Clichés, empty phrases, excessive hedging."""

        try:
            # Use generate_content for unstructured text
            narrative = self.client.generate_content(prompt)
            if not narrative:
                raise ValueError("Empty response from Gemini")

            logger.info(f"Generated narrative for {player} ({len(narrative)} chars)")
            return narrative.strip()
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            return f"Analysis: {confidence}% confidence on {player} {stat} {bet_type} {line}"
    
    def generate_game_overview(self, home_team: str, away_team: str, 
                               game_total: float, spread: float, context: Dict) -> str:
        """Generate game environment narrative"""
        if not self.client or not self.client.is_available:
            return f"{away_team} @ {home_team} | Total: {game_total} | Spread: {spread}"
        
        prompt = f"""Write a 1-paragraph game environment analysis.

GAME: {away_team} @ {home_team}
TOTAL: {game_total}
SPREAD: {home_team} {spread:+.1f}

DVOA Context:
{self._summarize_dvoa(home_team, away_team, context)}

Focus on: Game script expectations, pace, pass/run balance.
Length: 80-100 words."""

        try:
            overview = self.client.generate_content(prompt)
            return overview.strip() if overview else f"{away_team} @ {home_team}"
            
        except Exception as e:
            logger.error(f"Game overview failed: {e}")
            return f"{away_team} @ {home_team} | Total: {game_total} | Spread: {spread}"
    
    def _format_agent_scores(self, agent_breakdown: Dict) -> str:
        """Format agent scores for prompt"""
        lines = []
        for name, data in sorted(agent_breakdown.items(), 
                                key=lambda x: x[1].get('raw_score', 50), 
                                reverse=True):
            score = data.get('raw_score', 50)
            rationale = data.get('rationale', [])
            if rationale:
                lines.append(f"- {name}: {score}/100 - {rationale[0]}")
            else:
                lines.append(f"- {name}: {score}/100")
        return '\n'.join(lines[:5])  # Top 5 agents
    
    def _summarize_dvoa(self, team: str, opponent: str, context: Dict) -> str:
        """Summarize DVOA for prompt"""
        dvoa_off = context.get('dvoa_offensive', {})
        dvoa_def = context.get('dvoa_defensive', {})
        
        team_off = dvoa_off.get(team, {})
        opp_def = dvoa_def.get(opponent, {})
        
        return f"""Team Offense DVOA: {team_off.get('offense_dvoa', 'N/A')}%
Opponent Defense DVOA: {opp_def.get('defense_dvoa', 'N/A')}%"""
    
    def _summarize_injuries(self, injury_report: str) -> str:
        """Extract key injuries for prompt"""
        if not injury_report:
            return "Injuries: None reported"
        # Limit to first 300 chars
        return f"Injuries: {injury_report[:300]}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    generator = MatchupNarrativeGenerator()
    
    # Test
    test_prop = {
        'player_name': 'Patrick Mahomes',
        'team': 'KC',
        'opponent': 'BUF',
        'stat_type': 'Pass Yds',
        'line': 275.5,
        'bet_type': 'OVER'
    }
    
    test_agents = {
        'DVOA': {'raw_score': 72, 'rationale': ['Elite offense vs average defense']},
        'Matchup': {'raw_score': 68, 'rationale': ['Favorable pass defense matchup']},
        'Volume': {'raw_score': 65, 'rationale': ['High snap share, trending up']},
    }
    
    # Needs GEMINI_API_KEY env var set
    narrative = generator.generate_prop_narrative(
        test_prop, test_agents, 70, {}
    )
    
    print(narrative)
