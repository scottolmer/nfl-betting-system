"""
Prop Analyzer Orchestrator - Combines all agents with dynamic weight loading
"""

from typing import Dict, List
import logging
import numpy as np
import sys
import json
from pathlib import Path

from .models import PlayerProp, PropAnalysis
from .props_validator import PropsValidator
from .agents import (
    DVOAAgent,
    MatchupAgent,
    InjuryAgent,
    GameScriptAgent,
    VolumeAgent,
    # TrendAgent,      # REMOVED - 68% neutral, weak signal
    VarianceAgent,
    # WeatherAgent,    # REMOVED - no data available
    # HitRateAgent,    # REMOVED - no predictive value (51% both directions)
    AgentConfig,
    MetaAgent,
    MetaAgentConfig,
)

# Import AgentWeightManager for dynamic weight loading
sys.path.insert(0, str(Path(__file__).parent))
from agent_weight_manager import AgentWeightManager


class PropAnalyzer:
    """Main analysis orchestrator with dynamic weight loading"""

    def __init__(self, db_path: str = "bets.db", use_dynamic_weights: bool = True,
                 custom_weights: Dict[str, float] = None, apply_calibration: bool = True):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.use_dynamic_weights = use_dynamic_weights
        self.apply_calibration = apply_calibration

        # Load calibration config
        self.calibration_config = self._load_calibration_config()
        if self.calibration_config and self.apply_calibration:
            self.logger.info("📊 Calibration config loaded (stat filters + bias corrections)")

        # Initialize weight manager and load weights
        if custom_weights is not None:
            # Use provided weights directly (for optimization)
            weights = custom_weights
            self.weight_manager = None
            self.logger.info("🔧 Using custom weights (optimization mode)...")
        elif self.use_dynamic_weights:
            self.weight_manager = AgentWeightManager(db_path)
            # Ensure weights are initialized
            self.weight_manager.initialize_default_weights(force=False)
            weights = self.weight_manager.get_current_weights()
            self.logger.info("🔄 Loading agent weights from database...")
        else:
            self.weight_manager = None
            # Fallback to calibrated weights from offseason analysis
            # Based on weeks 11-16 data: Matchup/Volume hurt predictions, Injury/DVOA/Variance help
            # REMOVED: Trend, Weather, HitRate (no predictive value)
            weights = {
                'DVOA': 3.2,
                'Matchup': 0.5,    # Reduced - 38.1% accuracy (worse than random)
                'Volume': 0.75,   # Reduced - 44.4% accuracy
                'Injury': 4.7,    # Increased - highly predictive
                'GameScript': 0.82,
                'Variance': 2.4,
            }
            self.logger.info("⚙️  Using calibrated static agent weights...")

        # Initialize agents with dynamic weights
        # REMOVED: Trend (68% neutral), Weather (no data), HitRate (no predictive value)
        self.agents = {
            'DVOA': DVOAAgent(weight=weights.get('DVOA', 2.0)),
            'Matchup': MatchupAgent(weight=weights.get('Matchup', 1.5)),
            'Injury': InjuryAgent(weight=weights.get('Injury', 3.0)),
            'GameScript': GameScriptAgent(weight=weights.get('GameScript', 2.2)),
            'Volume': VolumeAgent(weight=weights.get('Volume', 1.5)),
            'Variance': VarianceAgent(weight=weights.get('Variance', 1.2)),
        }

        # Log weights
        for agent_name, agent in self.agents.items():
            self.logger.info(f"  {agent_name:12s} weight: {agent.weight:.2f}")

        # Initialize meta-agent (optional, enabled by default)
        meta_config = MetaAgentConfig()
        self.meta_agent = MetaAgent(meta_config) if meta_config.enabled else None
        if self.meta_agent:
            self.logger.info("🔮 Meta-agent initialized (reviews picks >= 65 confidence)")

        self.logger.info("🧠 PropAnalyzer initialized with 6 agents")

    def _load_calibration_config(self) -> Dict:
        """Load calibration config from config/calibration_config.json"""
        config_path = Path(__file__).parent.parent.parent / "config" / "calibration_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load calibration config: {e}")
        return {}

    def _is_stat_type_excluded(self, stat_type: str) -> bool:
        """Check if stat type should be excluded based on calibration config"""
        if not self.calibration_config or not self.apply_calibration:
            return False
        excluded = self.calibration_config.get('excluded_stat_types', [])
        return stat_type in excluded

    def _apply_bias_correction(self, confidence: int, stat_type: str, bet_type: str) -> int:
        """Apply over/under bias correction based on calibration analysis"""
        if not self.calibration_config or not self.apply_calibration:
            return confidence

        bias_corrections = self.calibration_config.get('over_under_bias', {})
        bias = bias_corrections.get(stat_type, 0)

        if bias == 0:
            return confidence

        # Apply bias: UNDER bets get boosted, OVER bets get reduced
        # Use /3 to prevent bias from dominating over agent signals
        if bet_type == 'UNDER':
            corrected = confidence + (bias / 3)
        else:
            corrected = confidence - (bias / 3)

        corrected = max(0, min(100, corrected))
        return int(round(corrected))

    def _get_anti_predictive_agents(self) -> List[str]:
        """Get list of agents whose signals should be inverted"""
        if not self.calibration_config or not self.apply_calibration:
            return []
        return self.calibration_config.get('anti_predictive_agents', [])

    def _apply_stat_type_adjustment(self, confidence: int, stat_type: str) -> int:
        """
        Apply confidence bonus/penalty based on stat type historical reliability.

        High-reliability stat types (55%+ win rate) get a bonus:
        - Rush+Rec Yds: +8 (67.1% historical)
        - Pass Completions: +6 (62.8% historical)
        - Pass TDs: +6 (62.2% historical)
        - Rush Yds: +4 (57.2% historical)

        Low-reliability stat types (<50% win rate) get a penalty:
        - Rec Yds: -3 (48.4% historical)
        """
        if not self.calibration_config or not self.apply_calibration:
            return confidence

        # Check for bonus
        bonuses = self.calibration_config.get('stat_type_bonus', {})
        if stat_type in bonuses:
            confidence += bonuses[stat_type]

        # Check for penalty
        penalties = self.calibration_config.get('stat_type_penalty', {})
        if stat_type in penalties:
            confidence -= penalties[stat_type]

        return max(0, min(100, confidence))

    def _calculate_agreement_adjustment(self, agent_results: Dict) -> int:
        """
        Calculate confidence adjustment based on agent agreement level.

        Key insight from analysis:
        - High agreement (80%+) correlates with WORSE performance (26-41% win rate)
        - Low agreement (<50%) correlates with BETTER performance (57-72% win rate)

        This is because when all agents agree, the line has already moved
        to price in the obvious factors. Disagreement indicates potential value.
        """
        if not self.calibration_config or not self.apply_calibration:
            return 0

        settings = self.calibration_config.get('agreement_settings', {})
        if not settings:
            return 0

        high_threshold = settings.get('high_agreement_threshold', 80)
        low_threshold = settings.get('low_agreement_threshold', 50)
        high_penalty = settings.get('high_agreement_penalty', 6)
        low_bonus = settings.get('low_agreement_bonus', 5)

        # Use effective scores (after anti-predictive inversion) for agreement check
        # This matches how scores are used in _calculate_final_confidence
        anti_predictive = self._get_anti_predictive_agents()

        agreeing = 0
        total = 0

        for agent_name, result in agent_results.items():
            direction = result.get('direction', '').upper()
            if direction in ('OVER', 'UNDER'):
                total += 1
                score = result.get('raw_score', 50)
                # Apply inversion for anti-predictive agents
                if agent_name in anti_predictive:
                    score = 100 - score
                if score >= 50:
                    agreeing += 1

        if total == 0:
            return 0

        agreement_pct = (agreeing / total) * 100

        # Apply adjustment
        if agreement_pct >= high_threshold:
            return -high_penalty  # Penalty for high agreement
        elif agreement_pct <= low_threshold:
            return low_bonus  # Bonus for low agreement (disagreement)
        else:
            return 0  # No adjustment for medium agreement

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

        # Apply bias correction to the OVER confidence BEFORE inversion.
        # This ensures symmetric treatment: a bias that reduces OVER confidence
        # automatically increases UNDER confidence by the same amount via 100-x.
        over_confidence = self._apply_bias_correction(
            over_confidence, prop.stat_type, 'OVER'
        )

        # Apply stat type reliability adjustment BEFORE inversion for symmetry.
        # A stat bonus on the OVER score benefits whichever direction the agents lean.
        over_confidence = self._apply_stat_type_adjustment(
            over_confidence, prop.stat_type
        )

        # Invert confidence for UNDER bets
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

        # Store source prop data for bookmaker/all_books metadata
        analysis._source_prop_data = prop_data

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

        excluded_count = 0
        for prop_data in props:
            try:
                if not prop_data.get('player_name') or not prop_data.get('stat_type'):
                    continue

                # Check if stat type is excluded based on calibration
                stat_type = prop_data.get('stat_type', '')
                if self._is_stat_type_excluded(stat_type):
                    excluded_count += 1
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
        if excluded_count > 0:
            self.logger.info(f"🚫 Excluded {excluded_count} props (calibration filter)")
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
        """Combine agent scores using weighted average with calibration adjustments.

        Key calibration fixes applied:
        1. Anti-predictive agents (Trend, Variance, GameScript) have scores INVERTED
           because they show 55-60% win rate when they DISAGREE with the bet
        2. Agreement penalty/bonus based on how many agents agree
        3. Global dampening to reduce overconfidence

        Important: Agent scores are NOT inverted for UNDER. We apply the inversion
        AFTER the weighted average to maintain symmetry.
        """
        total_weighted_score = 0.0
        total_weight = 0.0

        # Get list of anti-predictive agents
        anti_predictive = self._get_anti_predictive_agents()

        for agent_name, result in agent_results.items():
            weight = result.get('weight', 0)
            if weight > 0:
                raw_score = result.get('raw_score', 50)

                # CALIBRATION FIX: Invert scores for anti-predictive agents
                if agent_name in anti_predictive:
                    raw_score = 100 - raw_score

                # Reduce weight for neutral signals (score ~50) to prevent
                # high-weight agents like Injury from diluting real signals
                # when they have no actionable data (healthy players = 50)
                effective_weight = weight
                dist_from_neutral = abs(raw_score - 50)
                if dist_from_neutral < 5:
                    # Neutral signal: reduce to 20% of weight so it doesn't anchor
                    effective_weight = weight * 0.2

                total_weighted_score += raw_score * effective_weight
                total_weight += effective_weight

        if total_weight == 0:
            for agent_name, result in agent_results.items():
                raw_score = result.get('raw_score', 50)
                if agent_name in anti_predictive:
                    raw_score = 100 - raw_score
                total_weighted_score += raw_score
                total_weight += 1

        if total_weight == 0:
            return 50

        weighted_avg = total_weighted_score / total_weight

        # CALIBRATION FIX: Apply agreement adjustment
        # High agreement = penalty, Low agreement = bonus
        agreement_adj = self._calculate_agreement_adjustment(agent_results)

        # IMPORTANT: Apply bet_type inversion AFTER weighted average for symmetry
        # This ensures OVER 53% = UNDER 47%, not the other way around

        # CALIBRATION FIX (Project 3): Global Dampening REMOVED
        # Retaining 100% of the signal as per user request to use full 0-100 range.
        dist_from_50 = weighted_avg - 50
        damped_dist = dist_from_50 * 1.0
        final_score = 50 + damped_dist

        # Apply agreement adjustment AFTER dampening
        final_score += agreement_adj

        final_score_int = int(round(max(0, min(100, final_score))))
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
