"""
Claude Query Handler - Enhanced with weather, CSV normalization, and calibration
Weather only applied when real data provided to prevent hallucination
"""

import json
import logging
from typing import Dict
from anthropic import Anthropic
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.injury_analyzer import InjuryAnalyzer
from scripts.analysis.matchup_narrative import MatchupNarrativeGenerator
from scripts.analysis.weather_analyzer import WeatherImpactAnalyzer
from scripts.analysis.csv_normalizer import CSVNormalizer
from scripts.analysis.agent_calibrator import AgentCalibrator

logger = logging.getLogger(__name__)


class ClaudeQueryHandler:
    """Natural language interface with all Claude enhancements"""
    
    def __init__(self):
        self.client = Anthropic()
        self.model = "claude-sonnet-4-20250514"
        self.data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
        self.analyzer = PropAnalyzer()
        self.injury_analyzer = InjuryAnalyzer()
        self.narrative_generator = MatchupNarrativeGenerator()
        self.weather_analyzer = WeatherImpactAnalyzer()
        self.csv_normalizer = CSVNormalizer()
        self.calibrator = AgentCalibrator(db_path=str(project_root / "bets.db"))
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse_query(self, user_query: str) -> Dict:
        """Parse natural language query to extract player/stat/line."""
        
        prompt = f"""Parse this betting query and return ONLY valid JSON:

QUERY: "{user_query}"

Return JSON:
{{"player_name": "jordan love", "stat_type": "Pass Yds", "line": 250.5, "direction": "OVER", "parsing_valid": true}}"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            parsed = json.loads(response_text)
            if not parsed.get('parsing_valid'):
                return None
            return parsed
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Parse error: {e}")
            return None
    
    def run_analysis_for_query(self, parsed_query: Dict, week: int = 9, 
                              weather: Dict = None) -> Dict:
        """Run analysis with enhancements: injury, weather (if provided), narrative, calibration."""
        player_name = parsed_query.get('player_name')
        stat_type = parsed_query.get('stat_type')
        line = parsed_query.get('line')
        direction = parsed_query.get('direction', 'OVER')
        
        try:
            context = self.data_loader.load_all_data(week=week)
            
            prop_data = {
                'player_name': player_name,
                'stat_type': stat_type,
                'line': line,
                'direction': direction,
                'team': self._infer_team(player_name, context),
                'opponent': self._infer_opponent(player_name, context),
                'position': self._infer_position(stat_type),
                'game_total': self._get_game_total(player_name, context),
                'spread': self._get_spread(player_name, context),
                'is_home': self._is_home(player_name, context),
                'week': week,
            }
            
            # 1. Run agent analysis
            analysis = self.analyzer.analyze_prop(prop_data, context)
            
            # 2. Injury analysis
            injury_report = context.get('injury_report', {}).get(player_name, '')
            injury_analysis = self.injury_analyzer.analyze_player_injury_context(
                player_name, prop_data.get('team'), prop_data.get('position'), injury_report
            )
            
            # 3. Weather analysis - ONLY if real weather data provided
            weather_impact = {'overall_adjustment': 0, 'reasoning': ''}
            if weather and weather.get('conditions'):
                weather_impact = self.weather_analyzer.analyze_weather_impact(
                    prop_data.get('team'), prop_data.get('opponent'), stat_type, weather
                )
            
            # Combine adjustments
            total_adjustment = (
                injury_analysis.get('confidence_adjustment', 0) +
                weather_impact.get('overall_adjustment', 0)
            )
            
            adjusted_confidence = max(0, min(100, 
                analysis.final_confidence + total_adjustment
            ))
            
            # 4. Generate narrative
            narrative = self.narrative_generator.generate_prop_narrative(
                prop_data, analysis.agent_breakdown, adjusted_confidence, context
            )
            
            return {
                'success': True,
                'player': player_name,
                'stat': stat_type,
                'line': line,
                'direction': direction,
                'confidence': adjusted_confidence,
                'original_confidence': analysis.final_confidence,
                'injury_adjustment': injury_analysis.get('confidence_adjustment', 0),
                'weather_adjustment': weather_impact.get('overall_adjustment', 0),
                'recommendation': analysis.recommendation,
                'agent_breakdown': analysis.agent_breakdown,
                'rationale': analysis.rationale,
                'narrative': narrative,
                'injury_status': injury_analysis.get('reasoning', ''),
                'weather_status': weather_impact.get('reasoning', ''),
            }
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_response(self, result: Dict) -> str:
        """Format response with all enhancements."""
        if not result.get('success'):
            return f"❌ Error: {result.get('error')}"
        
        player = result['player']
        stat = result['stat']
        line = result['line']
        confidence = result['confidence']
        original_conf = result.get('original_confidence', confidence)
        injury_adj = result.get('injury_adjustment', 0)
        weather_adj = result.get('weather_adjustment', 0)
        
        emoji = "🔥" if confidence >= 75 else "⭐" if confidence >= 70 else "✅" if confidence >= 65 else "📊"
        
        response = f"{emoji} **{player.upper()}** • {stat} {result['direction']} {line}\n"
        response += f"**Confidence: {confidence}** / 100"
        
        adjustments = []
        if injury_adj != 0:
            adjustments.append(f"Injury: {injury_adj:+d}")
        if weather_adj != 0:
            adjustments.append(f"Weather: {weather_adj:+d}")
        
        if adjustments:
            response += f" ({original_conf} → {confidence})\n"
            response += f"*Adjustments: {', '.join(adjustments)}*\n"
        else:
            response += "\n"
        
        if result.get('injury_status'):
            response += f"*{result['injury_status']}*\n"
        if result.get('weather_status'):
            response += f"*{result['weather_status']}*\n"
        
        response += "\n**📖 Analysis:**\n"
        response += result.get('narrative', 'No narrative available') + "\n"
        
        response += "\n**Agent Breakdown:**\n"
        for agent_name, agent_data in sorted(result['agent_breakdown'].items(), 
                                             key=lambda x: x[1].get('raw_score', 50), reverse=True):
            score = agent_data.get('raw_score', 50)
            emoji_agent = "📈" if score >= 55 else "📉" if score <= 45 else "➡️"
            response += f"{emoji_agent} {agent_name}: {score}\n"
        
        return response
    
    def query(self, user_input: str, week: int = 9, weather: Dict = None) -> str:
        """Main entry point."""
        parsed = self.parse_query(user_input)
        if not parsed:
            return "❌ Parse failed. Try: 'Jordan Love 250 pass yards'"
        
        result = self.run_analysis_for_query(parsed, week, weather)
        if not result.get('success'):
            return result.get('error', 'Analysis failed')
        
        return self.format_response(result)
    
    def _infer_team(self, player_name: str, context: Dict) -> str:
        for prop in context.get('props', []):
            if player_name.lower() in prop.get('player_name', '').lower():
                return prop.get('team', 'UNK')
        return 'UNK'
    
    def _infer_opponent(self, player_name: str, context: Dict) -> str:
        for prop in context.get('props', []):
            if player_name.lower() in prop.get('player_name', '').lower():
                return prop.get('opponent', 'UNK')
        return 'UNK'
    
    def _infer_position(self, stat_type: str) -> str:
        stat_lower = stat_type.lower()
        if 'pass' in stat_lower:
            return 'QB'
        if 'rush' in stat_lower:
            return 'RB'
        if 'rec' in stat_lower:
            return 'WR'
        return 'UNK'
    
    def _get_game_total(self, player_name: str, context: Dict) -> float:
        for prop in context.get('props', []):
            if player_name.lower() in prop.get('player_name', '').lower():
                return prop.get('game_total', 44.5)
        return 44.5
    
    def _get_spread(self, player_name: str, context: Dict) -> float:
        for prop in context.get('props', []):
            if player_name.lower() in prop.get('player_name', '').lower():
                return prop.get('spread', 0.0)
        return 0.0
    
    def _is_home(self, player_name: str, context: Dict) -> bool:
        for prop in context.get('props', []):
            if player_name.lower() in prop.get('player_name', '').lower():
                return prop.get('is_home', True)
        return True


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    handler = ClaudeQueryHandler()
    query = "Jordan Love 250 pass yards"
    response = handler.query(query, week=9)
    print(response)
