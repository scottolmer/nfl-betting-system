"""
Prop Analyzer Orchestrator - Combines all agents with dynamic weight loading
"""

from typing import Dict, List
import logging
import numpy as np
import sys
from pathlib import Path

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
    HitRateAgent,
    AgentConfig,
    MetaAgent,
    MetaAgentConfig,
)

# Import AgentWeightManager for dynamic weight loading
sys.path.insert(0, str(Path(__file__).parent))
from agent_weight_manager import AgentWeightManager


class PropAnalyzer:
    """Main analysis orchestrator with dynamic weight loading"""

    def __init__(self, db_path: str = "bets.db", use_dynamic_weights: bool = True):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.use_dynamic_weights = use_dynamic_weights

        # Initialize weight manager
        if self.use_dynamic_weights:
            self.weight_manager = AgentWeightManager(db_path)
            # Ensure weights are initialized
            self.weight_manager.initialize_default_weights(force=False)
            weights = self.weight_manager.get_current_weights()
            self.logger.info("🔄 Loading agent weights from database...")
        else:
            self.weight_manager = None
            # Fallback to hardcoded weights from AgentConfig
            weights = {
                'DVOA': 2.0,
                'Matchup': 1.5,
                'Volume': 1.5,
                'Injury': 3.0,
                'Trend': 1.0,
                'GameScript': 2.2,
                'Variance': 1.2,
                'Weather': 1.3,
                'HitRate': 2.0,
            }
            self.logger.info("⚙️  Using static agent weights...")

        # Initialize agents with dynamic weights
        self.agents = {
            'DVOA': DVOAAgent(weight=weights.get('DVOA', 2.0)),
            'Matchup': MatchupAgent(weight=weights.get('Matchup', 1.5)),
            'Injury': InjuryAgent(weight=weights.get('Injury', 3.0)),
            'GameScript': GameScriptAgent(weight=weights.get('GameScript', 2.2)),
            'Volume': VolumeAgent(weight=weights.get('Volume', 1.5)),
            'Trend': TrendAgent(weight=weights.get('Trend', 1.0)),
            'Variance': VarianceAgent(weight=weights.get('Variance', 1.2)),
            'Weather': WeatherAgent(weight=weights.get('Weather', 1.3)),
            'HitRate': HitRateAgent(weight=weights.get('HitRate', 2.0)),
        }

        # Log weights
        for agent_name, agent in self.agents.items():
            self.logger.info(f"  {agent_name:12s} weight: {agent.weight:.2f}")

        # Initialize meta-agent (optional, enabled by default)
        meta_config = MetaAgentConfig()
        self.meta_agent = MetaAgent(meta_config) if meta_config.enabled else None
        if self.meta_agent:
            self.logger.info("🔮 Meta-agent initialized (reviews picks >= 65 confidence)")

        self.logger.info("🧠 PropAnalyzer initialized with 9 agents")

    def analyze_prop(self, prop_data: Dict, context: Dict, use_meta_agent: bool = False) -> PropAnalysis:
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

        # DON'T invert agent scores - keep them in OVER perspective for consistent interpretation
        # This way, agent scores always mean "confidence that OVER will hit"

        over_confidence = self._calculate_final_confidence(agent_results)

        # Restore original bet type
        prop.bet_type = original_bet_type

        # CRITICAL FIX: Invert confidence for UNDER bets
        # If agents say 65% OVER will hit, then UNDER bet should show 35% confidence
        if prop.bet_type == 'UNDER':
            final_confidence = 100 - over_confidence
        else:
            final_confidence = over_confidence

        # Determine direction from OVER perspective: >50 = OVER likely, <50 = UNDER likely
        agents_favor_over = over_confidence >= 50

        # For the recommendation, we want it to be relative to the BET we're analyzing
        # If analyzing OVER bet and agents favor OVER → recommend OVER
        # If analyzing OVER bet and agents favor UNDER → recommend UNDER (avoid the OVER)
        # If analyzing UNDER bet and agents favor UNDER → recommend UNDER
        # If analyzing UNDER bet and agents favor OVER → recommend OVER (avoid the UNDER)
        #
        # In other words: recommendation direction = agent prediction, always
        final_direction = "OVER" if agents_favor_over else "UNDER"

        recommendation = AgentConfig.get_recommendation(final_confidence, final_direction)
        edge_explanation = self._build_edge_explanation(prop, final_confidence, agent_results)
        
        # PROJECT 3: Calculate top contributing agents for correlation detection
        top_contributing_agents = self._calculate_top_contributing_agents(agent_results)

        analysis = PropAnalysis(
            prop=prop, final_confidence=final_confidence, recommendation=recommendation,
            rationale=all_rationale, agent_breakdown=agent_results, edge_explanation=edge_explanation,
            top_contributing_agents=top_contributing_agents,
        )

        # Meta-agent review (optional)
        if use_meta_agent and self.meta_agent and self.meta_agent.should_review(analysis):
            meta_result = self.meta_agent.review(analysis, context)
            analysis.final_confidence = meta_result.adjusted_confidence
            analysis.meta_agent_result = meta_result
            if meta_result.meta_rationale:
                analysis.rationale.insert(0, f"[META] {meta_result.meta_rationale}")

        return analysis

    def analyze_all_props(self, context: Dict, min_confidence: int = 50,
                          exclude_players: List[str] = None) -> List[PropAnalysis]:
        """Analyze all props and filter based on whether we should take the bet

        With the fixed system:
        - For OVER bets: confidence represents probability OVER hits
        - For UNDER bets: confidence represents probability UNDER hits (inverted from OVER)
        - Both are filtered using the same threshold: confidence >= min_confidence

        Args:
            context: Dict containing props and other context data
            min_confidence: Minimum confidence threshold for filtering
            exclude_players: List of player names to exclude (for Pick6/platform filtering)
        """
        props = context.get('props', [])
        if not props:
            self.logger.error("No props found in context!"); return []

        # Filter out excluded players if provided
        if exclude_players:
            exclude_players_lower = [p.lower().strip() for p in exclude_players]
            original_count = len(props)
            props = [p for p in props if p.get('player_name', '').lower().strip() not in exclude_players_lower]
            filtered_count = original_count - len(props)
            if filtered_count > 0:
                self.logger.info(f"🚫 Excluded {filtered_count} props from {len(exclude_players)} players")

        self.logger.info(f"📊 Analyzing {len(props)} props...")
        results = []

        for prop_data in props:
            try:
                if not prop_data.get('player_name') or not prop_data.get('stat_type'):
                    continue

                analysis = self.analyze_prop(prop_data, context)
                if analysis and hasattr(analysis, 'final_confidence'):
                    analysis = PropsValidator.validate_prop_analysis(analysis)

                    # FIXED: Now confidence is already adjusted for bet type
                    # Both OVER and UNDER use the same threshold
                    should_include = analysis.final_confidence >= min_confidence

                    if should_include:
                        results.append(analysis)

            except Exception as e:
                player = prop_data.get('player_name', '?')
                stat = prop_data.get('stat_type', '?')
                self.logger.error(f"❌ Failed: {player} {stat} - {e}", exc_info=False)

        results = PropsValidator.validate_all_analyses(results)
        results.sort(key=lambda x: x.final_confidence, reverse=True)
        self.logger.info(f"✅ Analyzed {len(results)} props")
        return results


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

    @staticmethod
    def prop_analysis_to_dict(analysis: PropAnalysis) -> Dict:
        """Convert PropAnalysis to JSON-serializable dict for assistant interface"""
        prop = analysis.prop
        return {
            'player_name': prop.player_name,
            'team': prop.team,
            'opponent': prop.opponent,
            'position': prop.position,
            'stat_type': prop.stat_type,
            'line': prop.line,
            'bet_type': prop.bet_type,
            'week': prop.week,
            'confidence': analysis.final_confidence,
            'recommendation': analysis.recommendation,
            'edge_explanation': analysis.edge_explanation,
            'agent_breakdown': analysis.agent_breakdown,
            'rationale': analysis.rationale[:3] if analysis.rationale else [],  # Top 3 reasons
        }
