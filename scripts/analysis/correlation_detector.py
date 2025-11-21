"""
PROJECT 3: Strategic Correlation Risk Detection
IMPROVEMENT #1: Dynamic Correlation Strength Matrix

Enhances ParlayBuilder to detect hidden correlations based on agent drivers.

IMPROVEMENT: Different agent pairs have different correlation magnitudes.
- DVOA + Matchup (strength 1.5): Very strong → -7.5% penalty per pair
- DVOA + Volume (strength 1.0): Moderate → -5% penalty per pair
- Volume + Trend (strength 0.7): Weak → -3.5% penalty per pair

This provides more nuanced risk assessment than flat -5% per driver.
"""

from typing import List, Dict, Set, Tuple, Optional
from .models import PropAnalysis, Parlay
import logging

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """Detects statistical correlations between props with dynamic strength weighting"""
    
    def __init__(self):
        """Initialize correlation analyzer with strength matrix (PROJECT 3 IMPROVEMENT #1)"""
        self.logger = logging.getLogger(__name__)
        
        # Correlation Strength Matrix - Different agent pairs have different magnitudes
        # Scale: 0.5 (minimal) to 1.5 (very strong)
        # Formula: penalty = -5.0 * strength for each shared agent pair
        self.correlation_strength = {
            # Very Strong (1.5) - Same fundamental weakness measured two ways
            ('DVOA', 'Matchup'): 1.5,        # 🔥 Both signal weakness in opponent defense
            
            # Strong (1.3-1.2) - Game-level signals that reinforce each other
            ('DVOA', 'GameScript'): 1.3,     # Game flow affected by weak defense
            ('Matchup', 'GameScript'): 1.2,  # Game context affects matchup and script
            
            # Moderate-Strong (1.1-0.9) - Related but partially independent signals
            ('Injury', 'Volume'): 1.1,       # Injury directly affects snap count/usage
            ('DVOA', 'Volume'): 1.0,         # Good offense vs weak defense correlation
            ('Injury', 'Matchup'): 0.9,      # Injury affects matchup value
            
            # Weak (0.7-0.6) - Different types of signals
            ('Trend', 'Volume'): 0.7,        # Recent form vs snap count (different dimensions)
            ('Trend', 'Injury'): 0.6,        # Performance vs health status (different)
            ('Volume', 'GameScript'): 0.6,   # Usage vs game flow
            
            # Very Weak (0.5)
            ('Variance', 'Weather'): 0.5,    # Minimal overlap
            ('Trend', 'Variance'): 0.5,      # Trend and variance mostly independent
        }
    
    def get_correlation_strength(self, agent1: str, agent2: str) -> float:
        """
        Get correlation strength between two agents (0.5-1.5 scale).
        
        Returns:
            - 1.5 = very strong correlation (DVOA+Matchup both signal same weakness)
            - 1.0 = moderate correlation (baseline)
            - 0.5 = minimal correlation (nearly independent signals)
        """
        # Check both orderings
        key1 = (agent1, agent2)
        key2 = (agent2, agent1)
        
        if key1 in self.correlation_strength:
            return self.correlation_strength[key1]
        elif key2 in self.correlation_strength:
            return self.correlation_strength[key2]
        else:
            # Default moderate correlation for unknown pairs
            return 1.0
    
    def calculate_correlation_risk(self, leg1: PropAnalysis, leg2: PropAnalysis) -> Tuple[float, List[str]]:
        """
        Calculate correlation penalty between two props using dynamic strength weighting.
        
        For shared drivers, apply: penalty = -5.0 * strength
        - If 2+ drivers shared (pair): use pair strength from matrix
        - If 1 driver shared: use that driver's default strength (1.0)
        
        Examples:
          - DVOA + Matchup both shared: strength 1.5 → -5 * 1.5 = -7.5%
          - Only DVOA shared: strength 1.0 → -5 * 1.0 = -5.0%
          - Only Variance shared: strength 1.0 → -5 * 1.0 = -5.0%
        
        Args:
            leg1: First PropAnalysis
            leg2: Second PropAnalysis
            
        Returns:
            (correlation_penalty, warnings) tuple
        """
        
        # Get top contributing agents for each leg
        leg1_drivers = self._extract_drivers(leg1)
        leg2_drivers = self._extract_drivers(leg2)
        
        # Find shared drivers
        shared_drivers = list(leg1_drivers & leg2_drivers)
        
        if not shared_drivers:
            return 0.0, []  # No correlation
        
        # LOGIC: Use the correlation strength matrix if 2+ drivers are shared
        # Otherwise use baseline strength of 1.0
        
        if len(shared_drivers) >= 2:
            # Two or more shared drivers - look up their pair strength
            # This is the most common case (e.g., both DVOA and Matchup shared)
            pair_strength = self.get_correlation_strength(shared_drivers[0], shared_drivers[1])
            penalty = -5.0 * pair_strength
        else:
            # Single shared driver - use baseline strength
            # This is less redundant than having 2+ shared drivers
            penalty = -5.0 * 1.0  # Baseline strength = 1.0
        
        self.logger.debug(
            f"Correlation: {leg1.prop.player_name} & {leg2.prop.player_name} "
            f"share {shared_drivers} → penalty {penalty:.1f}%"
        )
        
        return penalty, []
    
    def _extract_drivers(self, analysis: PropAnalysis) -> Set[str]:
        """Extract top 2 contributing agents from a PropAnalysis"""
        drivers = set()
        
        if hasattr(analysis, 'top_contributing_agents') and analysis.top_contributing_agents:
            drivers = {agent[0] for agent in analysis.top_contributing_agents[:2]}
        elif analysis.agent_breakdown:
            sorted_agents = sorted(
                analysis.agent_breakdown.items(),
                key=lambda x: x[1].get('weight', 0),
                reverse=True
            )
            drivers = {agent[0] for agent in sorted_agents[:2]}
        
        return drivers
    
    def _get_strength_emoji(self, strength: float) -> str:
        """Get emoji for correlation strength (1.2+ is 🔥)"""
        if strength >= 1.2:
            return "🔥"
        elif strength >= 0.9:
            return "⚠️"
        else:
            return "⚡"
    
    def analyze_parlay_correlations(self, parlay_legs: List[PropAnalysis]) -> Tuple[float, List[str]]:
        """
        Analyze all correlation risks within a parlay.
        
        For each pair of legs that share drivers, calculate the penalty based on
        the strength of correlation between those shared drivers.
        
        Args:
            parlay_legs: List of PropAnalysis objects in the parlay
            
        Returns:
            (total_correlation_penalty, correlation_warnings)
        """
        total_penalty = 0.0
        warnings = []
        
        # Check every pair of legs
        for i, leg1 in enumerate(parlay_legs):
            for leg2 in parlay_legs[i+1:]:
                penalty, _ = self.calculate_correlation_risk(leg1, leg2)
                
                if penalty < 0:
                    total_penalty += penalty
                    
                    # Build warning message
                    leg1_drivers = self._extract_drivers(leg1)
                    leg2_drivers = self._extract_drivers(leg2)
                    shared = leg1_drivers & leg2_drivers
                    shared_list = sorted(list(shared))
                    
                    if len(shared_list) >= 2:
                        # Two or more shared drivers - show the pair
                        strength = self.get_correlation_strength(shared_list[0], shared_list[1])
                        emoji = self._get_strength_emoji(strength)
                        shared_str = " + ".join(shared_list[:2])  # Show first 2
                    else:
                        # Single shared driver
                        strength = 1.0
                        emoji = self._get_strength_emoji(strength)
                        shared_str = shared_list[0] if shared_list else 'unknown'
                    
                    warning = (
                        f"{emoji} {leg1.prop.player_name} ({leg1.prop.team}) & "
                        f"{leg2.prop.player_name} ({leg2.prop.team}): "
                        f"both driven by {shared_str}"
                    )
                    warnings.append(warning)
        
        return total_penalty, warnings


class EnhancedParlayBuilder:
    """Enhanced Parlay Builder with correlation risk detection (Project 3)"""
    
    def __init__(self):
        self.correlation_analyzer = CorrelationAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def calculate_prop_contributions(self, analysis: PropAnalysis) -> List[Tuple[str, float]]:
        """
        Calculate each agent's contribution to the overall confidence score.
        
        Returns list of (agent_name, contribution_percentage) sorted by contribution.
        """
        agent_breakdown = analysis.agent_breakdown
        
        if not agent_breakdown:
            return []
        
        # Calculate contribution for each agent
        contributions = []
        total_weight = sum(agent.get('weight', 0) for agent in agent_breakdown.values())
        
        if total_weight == 0:
            total_weight = 1  # Avoid division by zero
        
        for agent_name, agent_data in agent_breakdown.items():
            weight = agent_data.get('weight', 0)
            raw_score = agent_data.get('raw_score', 50)
            
            # Contribution = how much this agent moved the needle from neutral (50)
            # Weighted by the agent's weight in the overall calculation
            agent_contribution = (raw_score - 50) * (weight / total_weight)
            contributions.append((agent_name, abs(agent_contribution)))
        
        # Sort by contribution magnitude
        contributions.sort(key=lambda x: x[1], reverse=True)
        
        return contributions
    
    def build_parlays_with_correlation(
        self, 
        all_analyses: List[PropAnalysis],
        min_confidence: int = 58,
        max_correlation_penalty: float = -20.0
    ) -> Dict[str, List[Parlay]]:
        """
        Build parlays with enhanced correlation detection.
        
        This is a WRAPPER around the existing build_parlays logic that:
        1. Calculates top_contributing_agents for each prop
        2. Analyzes correlation risks for each parlay
        3. Adjusts confidence and adds warnings
        
        Args:
            all_analyses: All PropAnalysis objects to build parlays from
            min_confidence: Minimum confidence threshold
            max_correlation_penalty: Most severe penalty to apply per parlay
        """
        
        # STEP 1: Populate top_contributing_agents for each analysis
        for analysis in all_analyses:
            if not hasattr(analysis, 'top_contributing_agents') or not analysis.top_contributing_agents:
                analysis.top_contributing_agents = self.calculate_prop_contributions(analysis)
        
        # STEP 2: Build basic parlays using the original builder logic
        from .parlay_builder import ParlayBuilder
        basic_builder = ParlayBuilder()
        basic_parlays = basic_builder.build_parlays(all_analyses, min_confidence)
        
        # STEP 3: Analyze and adjust each parlay for correlations
        enhanced_parlays = {
            '2-leg': [],
            '3-leg': [],
            '4-leg': [],
            '5-leg': [],
        }
        
        for leg_count, parlay_list in basic_parlays.items():
            for parlay in parlay_list:
                # Analyze correlations in this parlay
                correlation_penalty, warnings = self.correlation_analyzer.analyze_parlay_correlations(
                    parlay.legs
                )
                
                # Cap the penalty at max_correlation_penalty
                correlation_penalty = max(correlation_penalty, max_correlation_penalty)
                
                # Adjust parlay confidence
                original_confidence = parlay.combined_confidence
                parlay.correlation_bonus += int(correlation_penalty)
                new_confidence = parlay.combined_confidence
                
                # Log the adjustment if there's a penalty
                if correlation_penalty < 0:
                    self.logger.info(
                        f"Parlay {leg_count} correlation penalty: {original_confidence}% → {new_confidence}% "
                        f"({int(correlation_penalty)}%)"
                    )
                    for warning in warnings:
                        self.logger.info(f"  {warning}")
                
                # Store correlation info on the parlay for display
                parlay.correlation_warnings = warnings
                parlay.correlation_penalty = correlation_penalty
                
                enhanced_parlays[leg_count].append(parlay)
        
        return enhanced_parlays


def format_parlay_with_correlations(parlay: Parlay) -> List[str]:
    """
    Format a parlay with correlation information for display.
    """
    output = []
    
    num_legs = len(parlay.legs)
    output.append(f"\n**PARLAY {num_legs}** - {parlay.risk_level} RISK")
    
    # Show original vs. adjusted confidence if correlation penalty applied
    original_conf = parlay.combined_confidence
    if hasattr(parlay, 'correlation_penalty') and parlay.correlation_penalty < 0:
        original_before_penalty = int(original_conf - parlay.correlation_penalty)
        output.append(
            f"Combined Confidence: {original_conf}% "
            f"(was {original_before_penalty}%, {int(parlay.correlation_penalty)}% correlation penalty)"
        )
    else:
        output.append(f"Combined Confidence: {original_conf}%")
    
    output.append(f"EV: +{parlay.expected_value:.1f}%")
    output.append(f"Recommended Bet: {parlay.recommended_units:.1f} units")
    output.append("")
    
    # Show legs with their drivers
    for j, leg in enumerate(parlay.legs, 1):
        output.append(f"  Leg {j}: {leg.prop.player_name} ({leg.prop.team})")
        bet_type = getattr(leg.prop, 'bet_type', 'OVER')
        output.append(f"         {leg.prop.stat_type} {bet_type} {leg.prop.line}")
        output.append(f"         vs {leg.prop.opponent} | Confidence: {leg.final_confidence}%")
        
        # Show top contributing agents for this leg
        if hasattr(leg, 'top_contributing_agents') and leg.top_contributing_agents:
            top_agents = leg.top_contributing_agents[:2]
            drivers = ", ".join(f"{agent[0]}" for agent in top_agents)
            output.append(f"         [driven by {drivers}]")
    
    output.append("\n  Rationale:")
    output.append(f"    • {parlay.rationale}")
    
    # Show correlation warnings
    if hasattr(parlay, 'correlation_warnings') and parlay.correlation_warnings:
        output.append(f"\n  📊 Correlation Analysis:")
        for warning in parlay.correlation_warnings:
            output.append(f"    • {warning}")
    
    return output
