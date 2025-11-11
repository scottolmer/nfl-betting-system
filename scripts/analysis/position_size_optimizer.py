"""
Position Sizing Optimizer - Adjusts bet sizes based on player exposure and correlation risk

Professional betting strategy that:
1. Reduces bet size on high-exposure parlays
2. Increases bet size on diversified parlays
3. Maintains total bankroll allocation while managing risk
"""

from typing import List, Dict, Tuple
from collections import Counter
import math


class PositionSizeOptimizer:
    """Optimizes bet sizing based on player exposure and correlation"""
    
    def __init__(self, bankroll: float, base_kelly_fraction: float = 0.5):
        """
        Args:
            bankroll: Total betting bankroll
            base_kelly_fraction: Base Kelly fraction (0.5 = half Kelly for safety)
        """
        self.bankroll = bankroll
        self.base_kelly_fraction = base_kelly_fraction
    
    def calculate_exposure_adjusted_sizing(
        self, 
        parlays: List[Dict],
        total_allocation: float = 0.10  # Allocate 10% of bankroll total
    ) -> List[Dict]:
        """
        Calculate optimal bet sizes adjusting for player exposure
        
        Args:
            parlays: List of parlay dicts with 'legs' containing player info
            total_allocation: Total % of bankroll to allocate across all parlays
            
        Returns:
            List of parlays with added 'recommended_bet' and 'exposure_penalty' fields
        """
        
        # Step 1: Calculate player exposure across all parlays
        player_counts = self._calculate_player_exposure(parlays)
        
        # Step 2: Calculate exposure penalty for each parlay
        parlay_exposure_scores = []
        for parlay in parlays:
            exposure_score = self._calculate_parlay_exposure_score(parlay, player_counts, len(parlays))
            parlay_exposure_scores.append(exposure_score)
        
        # Step 3: Calculate base allocation per parlay
        total_bankroll_allocation = self.bankroll * total_allocation
        
        # Step 4: Weight allocation inversely to exposure
        # Parlays with low exposure get MORE money, high exposure get LESS
        inverse_exposure_weights = [1.0 / (score + 0.1) for score in parlay_exposure_scores]
        total_weight = sum(inverse_exposure_weights)
        
        # Step 5: Assign bet sizes
        sized_parlays = []
        for i, parlay in enumerate(parlays):
            # Base allocation based on inverse exposure weighting
            weight_fraction = inverse_exposure_weights[i] / total_weight
            base_bet = total_bankroll_allocation * weight_fraction
            
            # Apply confidence multiplier (higher confidence = slightly more)
            confidence = parlay.get('adjusted_confidence', parlay.get('confidence', 70))
            confidence_multiplier = confidence / 70.0  # Normalize around 70%
            
            # Final bet size
            recommended_bet = base_bet * confidence_multiplier
            
            # Add to parlay
            sized_parlay = parlay.copy()
            sized_parlay['recommended_bet'] = recommended_bet
            sized_parlay['exposure_score'] = parlay_exposure_scores[i]
            sized_parlay['exposure_penalty'] = 1.0 - (parlay_exposure_scores[i] / max(parlay_exposure_scores))
            sized_parlay['base_allocation'] = base_bet
            
            sized_parlays.append(sized_parlay)
        
        return sized_parlays
    
    def _calculate_player_exposure(self, parlays: List[Dict]) -> Counter:
        """Count how many parlays each player appears in"""
        player_counts = Counter()
        
        for parlay in parlays:
            players = set()
            
            # Handle different parlay structures
            if 'parlay' in parlay and hasattr(parlay['parlay'], 'legs'):
                for leg in parlay['parlay'].legs:
                    players.add(leg.prop.player_name)
            elif 'legs' in parlay:
                for leg in parlay['legs']:
                    if hasattr(leg, 'prop'):
                        players.add(leg.prop.player_name)
                    elif isinstance(leg, dict):
                        players.add(leg.get('player', leg.get('player_name', '')))
            
            # Count each player once per parlay
            for player in players:
                player_counts[player] += 1
        
        return player_counts
    
    def _calculate_parlay_exposure_score(
        self, 
        parlay: Dict, 
        player_counts: Counter,
        total_parlays: int
    ) -> float:
        """
        Calculate exposure score for a parlay (higher = more concentrated risk)
        
        Score is based on:
        1. How many high-exposure players are in this parlay
        2. Average exposure % of players in this parlay
        """
        
        players = []
        
        # Extract players from parlay
        if 'parlay' in parlay and hasattr(parlay['parlay'], 'legs'):
            players = [leg.prop.player_name for leg in parlay['parlay'].legs]
        elif 'legs' in parlay:
            for leg in parlay['legs']:
                if hasattr(leg, 'prop'):
                    players.append(leg.prop.player_name)
                elif isinstance(leg, dict):
                    players.append(leg.get('player', leg.get('player_name', '')))
        
        if not players:
            return 0.0
        
        # Calculate average exposure % of players in this parlay
        exposure_percentages = [
            (player_counts[player] / total_parlays * 100) 
            for player in players
        ]
        
        avg_exposure = sum(exposure_percentages) / len(exposure_percentages)
        
        # Penalty increases exponentially with exposure
        # 10% exposure = score of ~10
        # 40% exposure = score of ~40
        # But we also penalize having MULTIPLE high-exposure players
        max_exposure = max(exposure_percentages)
        
        # Combined score: 70% average exposure, 30% max exposure
        exposure_score = (avg_exposure * 0.7) + (max_exposure * 0.3)
        
        return exposure_score
    
    def format_sizing_report(self, sized_parlays: List[Dict]) -> str:
        """Format position sizing recommendations as a report"""
        
        lines = []
        lines.append("\n" + "="*80)
        lines.append("💰 POSITION SIZING OPTIMIZER - EXPOSURE-ADJUSTED RECOMMENDATIONS")
        lines.append("="*80)
        lines.append(f"\nBankroll: ${self.bankroll:,.2f}")
        
        total_recommended = sum(p['recommended_bet'] for p in sized_parlays)
        lines.append(f"Total Allocation: ${total_recommended:,.2f} ({(total_recommended/self.bankroll)*100:.1f}% of bankroll)")
        
        # Sort by recommended bet size (descending)
        sorted_parlays = sorted(sized_parlays, key=lambda x: x['recommended_bet'], reverse=True)
        
        lines.append("\n" + "-"*80)
        lines.append(f"{'PARLAY':<8} {'BET SIZE':<12} {'EXPOSURE':<12} {'CONFIDENCE':<12} {'PLAYERS':<30}")
        lines.append("-"*80)
        
        for i, parlay in enumerate(sorted_parlays, 1):
            bet = parlay['recommended_bet']
            exposure = parlay['exposure_score']
            conf = parlay.get('adjusted_confidence', parlay.get('confidence', 0))
            
            # Get player names
            players = []
            if 'parlay' in parlay and hasattr(parlay['parlay'], 'legs'):
                players = [leg.prop.player_name[:12] for leg in parlay['parlay'].legs]
            elif 'legs' in parlay:
                for leg in parlay['legs']:
                    if hasattr(leg, 'prop'):
                        players.append(leg.prop.player_name[:12])
                    elif isinstance(leg, dict):
                        players.append(leg.get('player', '')[:12])
            
            player_str = ", ".join(players[:3])
            if len(players) > 3:
                player_str += "..."
            
            # Risk indicator
            if exposure >= 35:
                risk = "🔴"
            elif exposure >= 25:
                risk = "🟡"
            else:
                risk = "🟢"
            
            lines.append(
                f"{i:<8} ${bet:>9.2f}  {risk} {exposure:>5.1f}%    "
                f"{conf:>6.1f}%      {player_str:<30}"
            )
        
        lines.append("-"*80)
        
        # Summary statistics
        high_exposure_count = sum(1 for p in sized_parlays if p['exposure_score'] >= 35)
        low_exposure_count = sum(1 for p in sized_parlays if p['exposure_score'] < 25)
        
        lines.append(f"\n📊 Portfolio Statistics:")
        lines.append(f"  Total Parlays: {len(sized_parlays)}")
        lines.append(f"  High Exposure (🔴): {high_exposure_count} parlays")
        lines.append(f"  Low Exposure (🟢): {low_exposure_count} parlays")
        
        avg_bet = total_recommended / len(sized_parlays)
        max_bet = max(p['recommended_bet'] for p in sized_parlays)
        min_bet = min(p['recommended_bet'] for p in sized_parlays)
        
        lines.append(f"\n💵 Bet Sizing:")
        lines.append(f"  Average: ${avg_bet:,.2f}")
        lines.append(f"  Range: ${min_bet:,.2f} - ${max_bet:,.2f}")
        lines.append(f"  Ratio (Max/Min): {max_bet/min_bet:.2f}x")
        
        lines.append("\n" + "="*80)
        lines.append("💡 STRATEGY: Larger bets on diversified parlays, smaller bets on concentrated ones")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def get_simple_recommendations(self, sized_parlays: List[Dict]) -> List[Tuple[int, float]]:
        """
        Get simple list of (parlay_index, bet_amount) recommendations
        
        Returns:
            List of tuples: (parlay_index, recommended_bet_amount)
        """
        return [(i, p['recommended_bet']) for i, p in enumerate(sized_parlays)]


# Example usage
if __name__ == "__main__":
    # Test with dummy data
    test_parlays = [
        {
            'confidence': 75,
            'legs': [
                {'player_name': 'patrick mahomes', 'stat_type': 'Pass Yds'},
                {'player_name': 'travis kelce', 'stat_type': 'Rec Yds'}
            ]
        },
        {
            'confidence': 72,
            'legs': [
                {'player_name': 'patrick mahomes', 'stat_type': 'Pass TDs'},
                {'player_name': 'tyreek hill', 'stat_type': 'Rec Yds'}
            ]
        },
        {
            'confidence': 78,
            'legs': [
                {'player_name': 'justin jefferson', 'stat_type': 'Rec Yds'},
                {'player_name': 'dalvin cook', 'stat_type': 'Rush Yds'}
            ]
        }
    ]
    
    optimizer = PositionSizeOptimizer(bankroll=5000, base_kelly_fraction=0.5)
    sized = optimizer.calculate_exposure_adjusted_sizing(test_parlays, total_allocation=0.10)
    report = optimizer.format_sizing_report(sized)
    print(report)
