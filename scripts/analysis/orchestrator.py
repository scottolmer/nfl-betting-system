"""
Prop Analyzer Orchestrator - Combines all agents
"""

from typing import Dict, List
import logging
import numpy as np

from .models import PlayerProp, PropAnalysis
from .agents import (
    DVOAAgent,
    MatchupAgent,
    InjuryAgent,
    GameScriptAgent,
    VolumeAgent,
    TrendAgent,
    VarianceAgent,
    WeatherAgent,
    AgentConfig,
)


class PropAnalyzer:
    """Main analysis orchestrator"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.agents = {
            'DVOA': DVOAAgent(),
            'Matchup': MatchupAgent(),
            'Injury': InjuryAgent(),
            'GameScript': GameScriptAgent(),
            'Volume': VolumeAgent(),
            'Trend': TrendAgent(),
            'Variance': VarianceAgent(),
            'Weather': WeatherAgent(),
        }

        self.logger.info("🧠 PropAnalyzer initialized with 8 agents (including Injury, Matchup, Weather)")

    def analyze_prop(self, prop_data: Dict, context: Dict) -> PropAnalysis:
        """Analyze a single prop bet"""
        prop = self._create_prop_object(prop_data)
        prop_log_id = f"{prop.player_name} ({prop.team}) {prop.stat_type} O{prop.line}"

        agent_results = {}
        all_rationale = []

        for agent_name, agent in self.agents.items():
            try:
                analysis_result = agent.analyze(prop, context)
                if analysis_result is None:
                     score, direction, rationale = 50, "AVOID", [f"⚠️ {agent_name} returned None"]
                else:
                    score, direction, rationale = analysis_result
                score = max(0, min(100, score if score is not None else 50))
                weight = agent.weight
                agent_results[agent_name] = {
                    'raw_score': score, 'direction': direction,
                    'rationale': rationale if rationale else [], 'weight': weight,
                }
                if rationale: all_rationale.extend(rationale)

            except Exception as e:
                self.logger.error(f"❌ {agent_name} failed for {prop_log_id}: {e}", exc_info=False)
                agent_results[agent_name] = {
                    'raw_score': 50, 'direction': 'AVOID',
                    'rationale': [f"⚠️ {agent_name} execution failed"], 'weight': 0,
                }

        final_confidence = self._calculate_final_confidence(agent_results)
        final_direction = "OVER" if final_confidence >= 50 else "UNDER"
        recommendation = AgentConfig.get_recommendation(final_confidence, final_direction)
        edge_explanation = self._build_edge_explanation(prop, final_confidence, agent_results)

        analysis = PropAnalysis(
            prop=prop, final_confidence=final_confidence, recommendation=recommendation,
            rationale=all_rationale, agent_breakdown=agent_results, edge_explanation=edge_explanation,
        )
        return analysis

    def analyze_all_props(self, context: Dict, min_confidence: int = 50) -> List[PropAnalysis]:
        """Analyze all props generating OVER and UNDER"""
        props = context.get('props', [])
        if not props:
            self.logger.error("No props found in context!"); return []

        self.logger.info(f"📊 Analyzing {len(props)} props (OVER + UNDER)...")
        results = []; skipped_count = 0
        
        for i, prop_data in enumerate(props):
            try:
                if not prop_data.get('player_name') or not prop_data.get('stat_type'):
                     skipped_count += 1; continue
                
                # Analyze OVER
                analysis = self.analyze_prop(prop_data, context)
                if analysis and hasattr(analysis, 'final_confidence'):
                    if analysis.final_confidence >= min_confidence:
                        results.append(analysis)
                    
                    # Generate UNDER (inverted)
                    under_analysis = self._create_under_variation(analysis)
                    if under_analysis.final_confidence >= min_confidence:
                        results.append(under_analysis)
                        
            except Exception as e:
                player = prop_data.get('player_name', '?'); stat = prop_data.get('stat_type', '?')
                self.logger.error(f"❌ Analysis failed for prop: {player} {stat} - {e}", exc_info=False)
                skipped_count += 1
        
        results.sort(key=lambda x: x.final_confidence, reverse=True)
        self.logger.info(f"✅ Found {len(results)} props (OVER+UNDER)")
        return results
    
    def _create_under_variation(self, over_analysis: PropAnalysis) -> PropAnalysis:
        """Create UNDER by inverting confidence"""
        import copy
        
        inverted_confidence = 100 - over_analysis.final_confidence
        
        under_prop = copy.deepcopy(over_analysis.prop)
        under_prop.bet_type = "UNDER"
        
        inverted_breakdown = {}
        for agent_name, result in over_analysis.agent_breakdown.items():
            inverted_score = 100 - result.get('raw_score', 50)
            inverted_breakdown[agent_name] = {
                'raw_score': inverted_score,
                'direction': 'UNDER' if result.get('direction') == 'OVER' else 'OVER',
                'rationale': result.get('rationale', []),
                'weight': result.get('weight', 0),
            }
        
        recommendation = AgentConfig.get_recommendation(inverted_confidence, "UNDER")
        
        under_analysis = PropAnalysis(
            prop=under_prop,
            final_confidence=inverted_confidence,
            recommendation=recommendation,
            rationale=over_analysis.rationale,
            agent_breakdown=inverted_breakdown,
            edge_explanation=f"UNDER bet (inverse of OVER: {100-inverted_confidence}%)"
        )
        
        return under_analysis

    def _create_prop_object(self, prop_data: Dict) -> PlayerProp:
        """Convert dict to PlayerProp object"""
        try: line = float(prop_data.get('line', 0))
        except (ValueError, TypeError): line = 0.0
        try: game_total = float(t) if (t := prop_data.get('game_total')) is not None else None
        except (ValueError, TypeError): game_total = None
        try: spread = float(s) if (s := prop_data.get('spread')) is not None else None
        except (ValueError, TypeError): spread = None

        return PlayerProp(
            player_name=prop_data.get('player_name', ''), team=prop_data.get('team', ''),
            opponent=prop_data.get('opponent', ''), position=prop_data.get('position', ''),
            stat_type=prop_data.get('stat_type', ''), line=line,
            game_total=game_total, spread=spread,
            is_home=prop_data.get('is_home', True), week=prop_data.get('week', 8),
        )

    def _calculate_final_confidence(self, agent_results: Dict) -> int:
        """Combine agent scores using weighted average"""
        total_weighted_score = 0.0
        total_weight = 0.0

        for agent_name, result in agent_results.items():
            weight = result.get('weight', 0)
            if weight > 0:
                raw_score = result.get('raw_score', 50)
                total_weighted_score += raw_score * weight
                total_weight += weight

        if total_weight == 0:
            for agent_name, result in agent_results.items():
                raw_score = result.get('raw_score', 50)
                total_weighted_score += raw_score
                total_weight += 1

        if total_weight == 0:
            return 50

        weighted_avg = total_weighted_score / total_weight
        final_score_int = int(round(max(0, min(100, weighted_avg))))
        return final_score_int

    def get_agent_breakdown_dict(self, agent_results: Dict) -> Dict:
        """
        Extract just agent names, scores, and weights for storage/logging.
        Used by parlay_tracker to store agent data for calibration analysis.
        
        Returns:
        {
            'DVOA': {'raw_score': 78, 'weight': 0.20},
            'Matchup': {'raw_score': 72, 'weight': 0.15},
            ...
        }
        """
        return {
            agent_name: {
                'raw_score': result.get('raw_score', 50),
                'weight': result.get('weight', 0),
            }
            for agent_name, result in agent_results.items()
        }

    def _build_edge_explanation(self, prop: PlayerProp, confidence: int, agent_results: Dict) -> str:
        """Build explanation of the edge based on raw scores and weights"""
        direction = "OVER" if confidence >= 50 else "UNDER"
        contributions = []
        for name, res in agent_results.items():
            raw_score = res.get('raw_score', 50); weight = res.get('weight', 0)
            if weight > 0:
                 contribution_score = (raw_score - 50) * weight
                 contributions.append((name, abs(contribution_score), contribution_score))
        contributions.sort(key=lambda x: x[1], reverse=True)
        top_3 = contributions[:3]
        if not top_3 or all(c[2] == 0 for c in top_3): return "Neutral - no clear edge identified."
        main_drivers = ", ".join(f"{name} ({cont:.1f})" for name, _, cont in top_3 if cont != 0)
        if not main_drivers: return f"Conf {confidence}, but top contributions neutral."

        if abs(confidence - 50) >= 25: strength = "🔥 STRONG"
        elif abs(confidence - 50) >= 15: strength = "✅ GOOD"
        elif abs(confidence - 50) >= 8: strength = "📊 MODERATE"
        else: strength = "SLIGHT"
        return f"{strength} {direction} edge primarily driven by: {main_drivers}"
