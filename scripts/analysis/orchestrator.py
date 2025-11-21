"""
Prop Analyzer Orchestrator - Combines all agents
"""

from typing import Dict, List
import logging
import numpy as np

from .models import PlayerProp, PropAnalysis
from .props_validator import PropsValidator
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
        """Analyze a single prop bet - forcing OVER analysis then inverting for UNDER"""
        prop = self._create_prop_object(prop_data)
        bet_indicator = prop.bet_type[0]  # 'O' for OVER, 'U' for UNDER
        prop_log_id = f"{prop.player_name} ({prop.team}) {prop.stat_type} {bet_indicator}{prop.line}"

        agent_results = {}
        all_rationale = []
        
        # Store original bet type and force OVER for analysis
        original_bet_type = prop.bet_type
        prop.bet_type = 'OVER'  # Force OVER for consistent agent analysis

        skipped_agents = []
        
        for agent_name, agent in self.agents.items():
            try:
                analysis_result = agent.analyze(prop, context)
                # PROJECT 1 FIX: Skip agents that return None instead of including them as 50
                if analysis_result is None:
                     self.logger.info(f"  ⏭️  {agent_name} returned None (missing data) - SKIPPING")
                     skipped_agents.append(agent_name)
                     continue
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
                skipped_agents.append(agent_name)
                continue
        
        # Log skipped agents
        if skipped_agents:
            self.logger.info(f"⏭️  Skipped agents: {', '.join(skipped_agents)}")

        final_confidence = self._calculate_final_confidence(agent_results)
        
        # Restore original bet type and invert if needed
        prop.bet_type = original_bet_type
        if original_bet_type == 'UNDER':
            final_confidence = 100 - final_confidence
        
        final_direction = "OVER" if final_confidence >= 50 else "UNDER"
        recommendation = AgentConfig.get_recommendation(final_confidence, final_direction)
        edge_explanation = self._build_edge_explanation(prop, final_confidence, agent_results)
        
        # PROJECT 3: Calculate top contributing agents for correlation detection
        top_contributing_agents = self._calculate_top_contributing_agents(agent_results)

        analysis = PropAnalysis(
            prop=prop, final_confidence=final_confidence, recommendation=recommendation,
            rationale=all_rationale, agent_breakdown=agent_results, edge_explanation=edge_explanation,
            top_contributing_agents=top_contributing_agents,
        )
        return analysis

    def analyze_all_props(self, context: Dict, min_confidence: int = 50) -> List[PropAnalysis]:
        """Analyze all props - each prop is analyzed AS-IS (OVER or UNDER as labeled in data)
        PLUS generate complementary UNDER/OVER variants for fair consideration"""
        props = context.get('props', [])
        if not props:
            self.logger.error("No props found in context!"); return []

        self.logger.info(f"📊 Analyzing {len(props)} props (each as OVER or UNDER)...")
        results = []; skipped_count = 0
        complementary_count = 0
        
        for i, prop_data in enumerate(props):
            try:
                if not prop_data.get('player_name') or not prop_data.get('stat_type'):
                     skipped_count += 1; continue
                
                # Analyze EACH PROP as-is (OVER or UNDER - not inverted)
                analysis = self.analyze_prop(prop_data, context)
                if analysis and hasattr(analysis, 'final_confidence'):
                    # ✅ NEW: Validate that prop is a PlayerProp object (not dict)
                    analysis = PropsValidator.validate_prop_analysis(analysis)
                    
                    if analysis.final_confidence >= min_confidence:
                        results.append(analysis)
                        
                        # ✅ NEW: Generate complementary UNDER/OVER variant with SAME confidence
                        # This ensures UNDER bets get fair competition at full confidence values
                        # IMPORTANT: Don't invert! Keep same confidence as original
                        complementary_analysis = self._create_complementary_bet_same_confidence(analysis)
                        results.append(complementary_analysis)
                        complementary_count += 1
                        
            except Exception as e:
                player = prop_data.get('player_name', '?'); stat = prop_data.get('stat_type', '?')
                label = prop_data.get('label', '?')
                self.logger.error(f"❌ Analysis failed for prop: {player} {stat} ({label}) - {e}", exc_info=False)
                skipped_count += 1
        
        # ✅ NEW: Final validation - ensure ALL props are PlayerProp objects
        results = PropsValidator.validate_all_analyses(results)
        
        results.sort(key=lambda x: x.final_confidence, reverse=True)
        self.logger.info(f"✅ Found {len(results)} props analyzed ({complementary_count} complementary variants added)")
        return results
    
    def _create_complementary_bet(self, analysis: PropAnalysis) -> PropAnalysis:
        """Create complementary bet by inverting confidence (OVER->UNDER or UNDER->OVER)"""
        import copy
        
        # Get the complementary confidence
        complementary_confidence = 100 - analysis.final_confidence
        
        # Create prop with opposite bet type
        comp_prop = copy.deepcopy(analysis.prop)
        comp_prop.bet_type = "UNDER" if analysis.prop.bet_type == "OVER" else "OVER"
        
        # Invert agent scores
        inverted_breakdown = {}
        for agent_name, result in analysis.agent_breakdown.items():
            inverted_score = 100 - result.get('raw_score', 50)
            inverted_breakdown[agent_name] = {
                'raw_score': inverted_score,
                'direction': 'UNDER' if result.get('direction') == 'OVER' else 'OVER',
                'rationale': result.get('rationale', []),
                'weight': result.get('weight', 0),
            }
        
        recommendation = AgentConfig.get_recommendation(complementary_confidence, comp_prop.bet_type)
        
        # Create complementary analysis
        complementary_analysis = PropAnalysis(
            prop=comp_prop,
            final_confidence=complementary_confidence,
            recommendation=recommendation,
            rationale=analysis.rationale,
            agent_breakdown=inverted_breakdown,
            edge_explanation=f"{comp_prop.bet_type} bet (complement of {analysis.prop.bet_type} at {analysis.final_confidence}%)",
            top_contributing_agents=analysis.top_contributing_agents,
        )
        
        return complementary_analysis
    
    def _create_complementary_bet_same_confidence(self, analysis: PropAnalysis) -> PropAnalysis:
        """Create complementary bet with SAME confidence (not inverted)
        
        CRITICAL FIX: Instead of inverting confidence (70% OVER -> 30% UNDER),
        create the complementary at the SAME confidence (70% OVER -> 70% UNDER).
        This ensures fair competition and UNDER bets actually appear in parlays.
        """
        import copy
        
        # Create prop with opposite bet type
        comp_prop = copy.deepcopy(analysis.prop)
        comp_prop.bet_type = "UNDER" if analysis.prop.bet_type == "OVER" else "OVER"
        
        # CRITICAL: Keep same confidence, don't invert!
        complementary_confidence = analysis.final_confidence
        
        # Invert agent scores for symmetry
        inverted_breakdown = {}
        for agent_name, result in analysis.agent_breakdown.items():
            inverted_score = 100 - result.get('raw_score', 50)
            inverted_breakdown[agent_name] = {
                'raw_score': inverted_score,
                'direction': 'UNDER' if result.get('direction') == 'OVER' else 'OVER',
                'rationale': result.get('rationale', []),
                'weight': result.get('weight', 0),
            }
        
        recommendation = AgentConfig.get_recommendation(complementary_confidence, comp_prop.bet_type)
        
        # Create complementary analysis with SAME confidence
        complementary_analysis = PropAnalysis(
            prop=comp_prop,
            final_confidence=complementary_confidence,  # NOT inverted!
            recommendation=recommendation,
            rationale=analysis.rationale,
            agent_breakdown=inverted_breakdown,
            edge_explanation=f"{comp_prop.bet_type} bet (equal confidence alternative to {analysis.prop.bet_type} at {analysis.final_confidence}%)",
            top_contributing_agents=analysis.top_contributing_agents,
        )
        
        return complementary_analysis

    def _create_prop_object(self, prop_data: Dict) -> PlayerProp:
        """Convert dict to PlayerProp object"""
        try: line = float(prop_data.get('line', 0))
        except (ValueError, TypeError): line = 0.0
        try: game_total = float(t) if (t := prop_data.get('game_total')) is not None else None
        except (ValueError, TypeError): game_total = None
        try: spread = float(s) if (s := prop_data.get('spread')) is not None else None
        except (ValueError, TypeError): spread = None

        # Preserve bet_type from 'bet_type' field in data (data_loader stores label as bet_type)
        # Also check 'label' as fallback for compatibility
        label = prop_data.get('bet_type') or prop_data.get('label', 'Over')
        bet_type = 'UNDER' if str(label).lower() == 'under' else 'OVER'

        return PlayerProp(
            player_name=prop_data.get('player_name', ''), team=prop_data.get('team', ''),
            opponent=prop_data.get('opponent', ''), position=prop_data.get('position', ''),
            stat_type=prop_data.get('stat_type', ''), line=line,
            game_total=game_total, spread=spread,
            is_home=prop_data.get('is_home', True), week=prop_data.get('week', 8),
            bet_type=bet_type,
        )

    def _calculate_final_confidence(self, agent_results: Dict, bet_type: str = 'OVER') -> int:
        """Combine agent scores using weighted average
        
        Important: Agent scores are NOT inverted for UNDER. We apply the inversion
        AFTER the weighted average to maintain symmetry.
        """
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
        
        # IMPORTANT: Apply bet_type inversion AFTER weighted average for symmetry
        # This ensures OVER 53% = UNDER 47%, not the other way around
        # NOTE: This method is called from analyze_prop which has access to bet_type,
        # but we don't have it here. Instead, agents will handle the inversion.
        # See agents/*.py for the inversion logic.
        
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

    def _calculate_top_contributing_agents(self, agent_results: Dict) -> list:
        """
        PROJECT 3: Calculate which agents contributed most to the confidence score.
        
        Returns list of (agent_name, contribution_percentage) sorted by contribution magnitude.
        Used by CorrelationAnalyzer to detect hidden correlations between props.
        """
        contributions = []
        total_weight = sum(res.get('weight', 0) for res in agent_results.values())
        
        if total_weight == 0:
            return []
        
        for agent_name, res in agent_results.items():
            raw_score = res.get('raw_score', 50)
            weight = res.get('weight', 0)
            
            # Contribution = how much this agent moved the needle from neutral (50)
            # Expressed as a percentage of total weighted impact
            agent_contribution_pct = abs((raw_score - 50) * weight / total_weight)
            
            if agent_contribution_pct > 0:  # Only include agents that actually contributed
                contributions.append((agent_name, agent_contribution_pct))
        
        # Sort by contribution magnitude (descending)
        contributions.sort(key=lambda x: x[1], reverse=True)
        
        return contributions

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
