"""
Prop Analyzer Orchestrator - Combines all agents
"""

from typing import Dict, List
import logging
import numpy as np # Import numpy for potential future adjustments

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

        self.logger.info("🧠 PropAnalyzer initialized with 8 agents")

    def analyze_prop(self, prop_data: Dict, context: Dict) -> PropAnalysis:
        """Analyze a single prop bet"""
        prop = self._create_prop_object(prop_data)
        prop_log_id = f"{prop.player_name} ({prop.team}) {prop.stat_type} O{prop.line}" # Keep for error logging

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
                # Keep error logging concise
                self.logger.error(f"❌ {agent_name} failed for {prop_log_id}: {e}", exc_info=False)
                agent_results[agent_name] = {
                    'raw_score': 50, 'direction': 'AVOID',
                    'rationale': [f"⚠️ {agent_name} execution failed"], 'weight': 0,
                }

        final_confidence = self._calculate_final_confidence(agent_results) # Remove prop_log_id
        final_direction = "OVER" if final_confidence >= 50 else "UNDER"
        recommendation = AgentConfig.get_recommendation(final_confidence, final_direction)
        edge_explanation = self._build_edge_explanation(prop, final_confidence, agent_results)

        analysis = PropAnalysis(
            prop=prop, final_confidence=final_confidence, recommendation=recommendation,
            rationale=all_rationale, agent_breakdown=agent_results, edge_explanation=edge_explanation,
        )
        return analysis

    def analyze_all_props(self, context: Dict, min_confidence: int = 50) -> List[PropAnalysis]:
        """Analyze all props"""
        props = context.get('props', [])
        if not props:
            self.logger.error("No props found in context!"); return []

        self.logger.info(f"📊 Analyzing {len(props)} props...")
        results = []; skipped_count = 0
        for i, prop_data in enumerate(props):
            try:
                if not prop_data.get('player_name') or not prop_data.get('stat_type'):
                     skipped_count += 1; continue
                analysis = self.analyze_prop(prop_data, context)
                if analysis and hasattr(analysis, 'final_confidence') and analysis.final_confidence >= min_confidence:
                    results.append(analysis)
            except Exception as e:
                player = prop_data.get('player_name', '?'); stat = prop_data.get('stat_type', '?')
                self.logger.error(f"❌ Analysis failed for prop: {player} {stat} - {e}", exc_info=False)
                skipped_count += 1
        results.sort(key=lambda x: x.final_confidence, reverse=True)
        self.logger.info(f"✅ Found {len(results)} props >= {min_confidence} conf (skipped {skipped_count})")
        return results

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
        """
        Combine agent scores using weighted average.
        ONLY includes agents with meaningful opinions (non-neutral 50 scores without rationale).
        """
        total_weighted_score = 0.0; total_weight = 0.0; contributing_agents = 0
        # contributing_agent_details = [] # REMOVED DEBUG

        for agent_name, result in agent_results.items():
            raw_score = result.get('raw_score', 50); weight = result.get('weight', 0)
            rationale = result.get('rationale', [])
            should_contribute = weight > 0 and (raw_score != 50 or (rationale and len(rationale) > 0))

            if should_contribute:
                total_weighted_score += raw_score * weight
                total_weight += weight
                contributing_agents += 1
                # REMOVED DEBUG APPEND

        if total_weight == 0: # Fallback if all were neutral
             # REMOVED DEBUG RESET
             for agent_name, result in agent_results.items():
                 weight = result.get('weight', 0)
                 if weight > 0:
                    raw_score = result.get('raw_score', 50)
                    total_weighted_score += raw_score * weight
                    total_weight += weight
                    # REMOVED DEBUG APPEND

        if total_weight == 0:
             # REMOVED DEBUG WARNING
             return 50

        weighted_avg = total_weighted_score / total_weight

        # REMOVED DEBUG LOGS

        final_score_int = int(round(max(0, min(100, weighted_avg))))

        # REMOVED DEBUG LOG

        return final_score_int


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

        if abs(confidence - 50) >= 25: strength = "🔥 STRONG"    # 75+ or 25-
        elif abs(confidence - 50) >= 15: strength = "✅ GOOD"     # 65-74 or 26-35
        elif abs(confidence - 50) >= 8: strength = "📊 MODERATE" # 58-64 or 36-42
        else: strength = "SLIGHT"                               # 51-57 or 43-49
        return f"{strength} {direction} edge primarily driven by: {main_drivers}"