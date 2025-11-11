"""Kelly Criterion optimizer for optimal bet sizing across parlays"""

import math
from typing import List, Dict, Tuple

class KellyOptimizer:
    """
    Implements Kelly Criterion for optimal portfolio allocation.
    
    Kelly Criterion: f* = (bp - q) / b
    where:
    - f* = fraction of bankroll to wager
    - b = odds (decimal odds - 1)
    - p = probability of winning (confidence / 100)
    - q = probability of losing (1 - p)
    
    Key principle: Max growth = Expected value / odds
    Larger edge + lower odds = smaller bet size
    Larger edge + higher odds = larger bet size
    """
    
    def __init__(self, bankroll: float, kelly_fraction: float = 0.5):
        """
        Initialize Kelly optimizer.
        
        Args:
            bankroll: Total capital available
            kelly_fraction: Fraction of Kelly to use (0.25 = quarter Kelly for safety)
                           Full Kelly is aggressive; 0.5 Kelly is balanced
        """
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.min_bet = 25  # DraftKings minimum
    
    def kelly_fraction_for_parlay(self, confidence: float, odds: float) -> float:
        """
        Calculate Kelly fraction for a single parlay.
        
        Args:
            confidence: Confidence as percentage (0-100)
            odds: American odds (e.g., -110, +200)
        
        Returns:
            Kelly fraction (0-1)
        """
        # Convert confidence to probability
        p = confidence / 100.0
        q = 1 - p
        
        # Convert American odds to decimal
        decimal_odds = self._american_to_decimal(odds)
        b = decimal_odds - 1  # Net odds
        
        # Kelly formula: f* = (bp - q) / b
        kelly = (b * p - q) / b
        
        # Ensure non-negative (don't bet if expectation is negative)
        kelly = max(0, kelly)
        
        # Apply fractional Kelly for risk management
        kelly = kelly * self.kelly_fraction
        
        # Cap at reasonable maximum (never risk more than 20% per bet)
        kelly = min(kelly, 0.20)
        
        return kelly
    
    def _american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal."""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def _decimal_to_american(self, decimal_odds: float) -> float:
        """Convert decimal odds back to American."""
        if decimal_odds >= 2:
            return (decimal_odds - 1) * 100
        else:
            return -100 / (decimal_odds - 1)
    
    def optimize_portfolio(self, parlays: List[Dict]) -> Dict:
        """
        Optimize bet sizes across multiple parlays.
        
        Args:
            parlays: List of parlay dicts with keys:
                    - 'confidence': confidence percentage (0-100)
                    - 'odds': American odds (e.g., -110)
                    - 'name' or 'id': identifier (optional)
                    - 'legs': list of legs (optional, for display)
        
        Returns:
            Dict with allocation details and sizing
        """
        if not parlays:
            return {"error": "No parlays provided"}
        
        allocations = []
        total_kelly = 0
        
        # Calculate Kelly for each parlay
        for i, parlay in enumerate(parlays):
            confidence = parlay.get('confidence', parlay.get('adjusted_confidence', 70))
            odds = parlay.get('odds', -110)
            
            # Safety: only bet on 62%+ confidence
            if confidence < 62:
                kelly = 0
                reason = "Confidence too low"
            else:
                kelly = self.kelly_fraction_for_parlay(confidence, odds)
                reason = None
            
            allocations.append({
                'index': i,
                'name': parlay.get('name', f"Parlay {i+1}"),
                'confidence': confidence,
                'odds': odds,
                'kelly_fraction': kelly,
                'reason': reason
            })
            
            total_kelly += kelly
        
        # Normalize to sum to 1 (if total > 1)
        if total_kelly > 0:
            for alloc in allocations:
                alloc['normalized_kelly'] = (alloc['kelly_fraction'] / total_kelly) if total_kelly > 0 else 0
        else:
            return {
                "error": "No parlays qualify for betting (all < 62% confidence)",
                "allocations": allocations
            }
        
        # Calculate bet sizes
        for alloc in allocations:
            if total_kelly > 0:
                alloc['bet_amount'] = alloc['normalized_kelly'] * self.bankroll
                # Round to nearest $5
                alloc['bet_amount_rounded'] = max(self.min_bet, round(alloc['bet_amount'] / 5) * 5)
            else:
                alloc['bet_amount'] = 0
                alloc['bet_amount_rounded'] = 0
        
        # Calculate expected outcomes
        total_risk = sum(a['bet_amount_rounded'] for a in allocations)
        
        expected_value = 0
        for alloc in allocations:
            if alloc['bet_amount_rounded'] > 0:
                decimal_odds = self._american_to_decimal(alloc['odds'])
                prob = alloc['confidence'] / 100.0
                ev = alloc['bet_amount_rounded'] * (prob * (decimal_odds - 1) - (1 - prob))
                alloc['expected_value'] = ev
                expected_value += ev
        
        return {
            'success': True,
            'bankroll': self.bankroll,
            'kelly_fraction_used': self.kelly_fraction,
            'total_risk': total_risk,
            'total_expected_value': expected_value,
            'roi': (expected_value / total_risk * 100) if total_risk > 0 else 0,
            'allocations': allocations
        }
    
    def compare_strategies(self, parlays: List[Dict]) -> Dict:
        """
        Compare Kelly allocation vs flat betting vs no bet.
        
        Shows:
        - Flat: Equal bet on each parlay
        - Kelly: Optimized allocation
        - Expected growth rate
        """
        result = self.optimize_portfolio(parlays)
        
        if 'error' in result:
            return result
        
        # Flat betting
        num_parlays = len([p for p in parlays if p.get('confidence', 70) >= 62])
        if num_parlays > 0:
            flat_bet_size = self.bankroll / num_parlays
        else:
            flat_bet_size = 0
        
        flat_ev = 0
        kelly_ev = result['total_expected_value']
        
        for alloc in result['allocations']:
            if alloc['confidence'] >= 62:
                decimal_odds = self._american_to_decimal(alloc['odds'])
                prob = alloc['confidence'] / 100.0
                ev = flat_bet_size * (prob * (decimal_odds - 1) - (1 - prob))
                flat_ev += ev
        
        result['comparison'] = {
            'flat_betting': {
                'bet_per_parlay': flat_bet_size,
                'total_risk': flat_bet_size * num_parlays,
                'expected_value': flat_ev,
                'roi': (flat_ev / (flat_bet_size * num_parlays) * 100) if flat_bet_size * num_parlays > 0 else 0
            },
            'kelly_optimized': {
                'total_risk': result['total_risk'],
                'expected_value': kelly_ev,
                'roi': result['roi']
            },
            'advantage': {
                'ev_difference': kelly_ev - flat_ev,
                'roi_difference': result['roi'] - ((flat_ev / (flat_bet_size * num_parlays) * 100) if flat_bet_size * num_parlays > 0 else 0)
            }
        }
        
        return result


def format_kelly_report(result: Dict) -> str:
    """Format Kelly optimization result for display."""
    
    if 'error' in result:
        return f"\n❌ {result['error']}\n"
    
    if not result.get('success'):
        return f"\n❌ Optimization failed\n"
    
    output = "\n" + "="*90
    output += "\n🎲 KELLY CRITERION PORTFOLIO OPTIMIZATION"
    output += "\n" + "="*90
    
    output += f"\n📊 PORTFOLIO SUMMARY"
    output += f"\nBankroll: ${result['bankroll']:,.2f}"
    output += f"\nKelly Fraction Used: {result['kelly_fraction_used']*100:.0f}% Kelly"
    output += f"\nTotal Risk: ${result['total_risk']:,.2f}"
    output += f"\nExpected Value: ${result['total_expected_value']:,.2f}"
    output += f"\nExpected ROI: {result['roi']:.2f}%"
    
    output += "\n\n" + "-"*90
    output += "\n📋 INDIVIDUAL ALLOCATIONS"
    output += "\n" + "-"*90
    output += f"\n{'#':<3} {'Confidence':<12} {'Odds':<8} {'Kelly %':<10} {'Bet Size':<12} {'EV':<12}"
    output += "\n" + "-"*90
    
    for alloc in result['allocations']:
        if alloc['confidence'] < 62:
            output += f"\n{alloc['index']+1:<3} {alloc['confidence']:.1f}%      {alloc['odds']:<8} SKIP (low conf) — Confidence < 62%"
        else:
            output += f"\n{alloc['index']+1:<3} {alloc['confidence']:.1f}%      {alloc['odds']:<8} {alloc['kelly_fraction']*100:>6.2f}%  ${alloc['bet_amount_rounded']:>10,.0f}  ${alloc.get('expected_value', 0):>10,.2f}"
    
    # Comparison section
    if 'comparison' in result:
        comp = result['comparison']
        output += "\n\n" + "="*90
        output += "\n📈 STRATEGY COMPARISON"
        output += "\n" + "="*90
        
        flat = comp['flat_betting']
        kelly = comp['kelly_optimized']
        adv = comp['advantage']
        
        output += "\n" + "-"*90
        output += f"\n{'Strategy':<20} {'Total Risk':<15} {'Expected Value':<15} {'ROI':<10}"
        output += "\n" + "-"*90
        output += f"\nFlat Betting{' '*8} ${flat['total_risk']:>13,.0f} ${flat['expected_value']:>13,.2f} {flat['roi']:>8.2f}%"
        output += f"\nKelly Optimized{' '*4} ${kelly['total_risk']:>13,.0f} ${kelly['expected_value']:>13,.2f} {kelly['roi']:>8.2f}%"
        
        output += "\n" + "-"*90
        output += f"\n✅ Kelly Advantage:    +${adv['ev_difference']:>13,.2f} EV (+{adv['roi_difference']:.2f}pp ROI)"
        output += "\n" + "="*90
        
        if adv['ev_difference'] > 0:
            output += "\n💡 Kelly allocation extracts significantly more value!"
            output += "\n   By sizing proportional to edge, you maximize long-term growth."
        else:
            output += "\n💡 Parlays don't have sufficient edge. Consider higher confidence threshold."
    
    output += "\n\n💰 USAGE TIPS:"
    output += "\n  • Only bet on 62%+ confidence parlays"
    output += "\n  • Use 50% Kelly (fractional) for safer sizing"
    output += "\n  • Adjust bankroll up/down based on season results"
    output += "\n  • Track actual vs expected to validate model\n"
    
    return output


# Example usage
if __name__ == "__main__":
    # Sample parlays
    parlays = [
        {
            'name': 'Mahomes/Ekeler/Kelce',
            'confidence': 78,
            'odds': -110,
            'legs': 3
        },
        {
            'name': 'Love/Jones Stack',
            'confidence': 74,
            'odds': -110,
            'legs': 2
        },
        {
            'name': 'Burrow/Chase/Higgins',
            'confidence': 71,
            'odds': -115,
            'legs': 3
        },
        {
            'name': 'Lamar/Edwards Multi',
            'confidence': 76,
            'odds': -110,
            'legs': 2
        }
    ]
    
    optimizer = KellyOptimizer(bankroll=1000, kelly_fraction=0.5)
    result = optimizer.compare_strategies(parlays)
    print(format_kelly_report(result))
