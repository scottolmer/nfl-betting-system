"""
Correlation Strength Calibration Tracker
Track actual parlay results to validate & refine the correlation strength matrix.

This tool helps you:
1. Log parlays with their detected correlations
2. Track their actual results (win/loss)
3. Calculate loss rates by correlation type
4. Recommend strength adjustments based on real data

Usage:
  tracker = CorrelationCalibrationTracker()
  
  # After generating parlays:
  tracker.log_parlay(
      parlay_id="2025-11-17-001",
      correlation_types=["DVOA+Matchup", "Volume+Trend"],
      initial_confidence=72,
      result="LOSS",
      notes="KC passing game too correlated"
  )
  
  # After week ends:
  tracker.analyze_by_correlation_type()
  tracker.recommend_adjustments()
  tracker.export_calibration_data()
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict


class CorrelationCalibrationTracker:
    """Track correlation accuracy and recommend strength adjustments"""
    
    def __init__(self, data_dir: str = "calibration_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.calibration_file = self.data_dir / "correlation_calibration.json"
        self.data = self._load_data()
        
        # Current strength values (should match correlation_detector.py)
        self.current_strengths = {
            ('DVOA', 'Matchup'): 1.5,
            ('DVOA', 'GameScript'): 1.3,
            ('Matchup', 'GameScript'): 1.2,
            ('Injury', 'Volume'): 1.1,
            ('DVOA', 'Volume'): 1.0,
            ('Injury', 'Matchup'): 0.9,
            ('Trend', 'Volume'): 0.7,
            ('Trend', 'Injury'): 0.6,
            ('Variance', 'Weather'): 0.5,
        }
    
    def _load_data(self) -> Dict:
        """Load calibration data from file"""
        if self.calibration_file.exists():
            with open(self.calibration_file, 'r') as f:
                return json.load(f)
        return {'parlays': [], 'adjustments': []}
    
    def _save_data(self):
        """Save calibration data to file"""
        with open(self.calibration_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_parlay(
        self,
        parlay_id: str,
        correlation_types: List[str],
        initial_confidence: int,
        final_confidence: int,
        result: str,  # 'WIN', 'LOSS', 'PUSH', 'PARTIAL'
        parlay_size: int = 0,
        units_bet: float = 0.0,
        payout_if_win: float = 0.0,
        notes: str = ""
    ):
        """
        Log a parlay with its correlation and result.
        
        Args:
            parlay_id: Unique identifier for parlay (e.g., "2025-11-17-001")
            correlation_types: List of detected correlations (e.g., ["DVOA+Matchup"])
            initial_confidence: Confidence before correlation penalty
            final_confidence: Confidence after correlation penalty
            result: Outcome (WIN, LOSS, PUSH, PARTIAL)
            parlay_size: Number of legs in parlay
            units_bet: How much was wagered
            payout_if_win: Potential payout (for ROI calculation)
            notes: Custom observations
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'parlay_id': parlay_id,
            'parlay_size': parlay_size,
            'correlation_types': correlation_types,
            'initial_confidence': initial_confidence,
            'final_confidence': final_confidence,
            'confidence_penalty': final_confidence - initial_confidence,
            'result': result,
            'units_bet': units_bet,
            'payout_if_win': payout_if_win,
            'notes': notes,
        }
        
        self.data['parlays'].append(entry)
        self._save_data()
        
        print(f"✓ Logged parlay {parlay_id}: {result} "
              f"({', '.join(correlation_types) if correlation_types else 'no correlations'})")
    
    def analyze_by_correlation_type(self) -> Dict[str, Dict]:
        """
        Analyze which correlation types predict loss rates accurately.
        
        Returns:
            {
                'DVOA+Matchup': {
                    'total': 5,
                    'wins': 2,
                    'losses': 3,
                    'loss_rate': 0.60,
                    'current_strength': 1.5,
                    'expected_loss_rate': 0.70  # Based on strength magnitude
                }
            }
        """
        correlation_stats = defaultdict(lambda: {'total': 0, 'wins': 0, 'losses': 0})
        
        # Count results for each correlation type
        for parlay in self.data['parlays']:
            result = parlay['result']
            
            if result == 'WIN':
                count = 1
                loss_count = 0
            elif result == 'LOSS':
                count = 1
                loss_count = 1
            elif result == 'PUSH':
                continue  # Skip pushes
            elif result == 'PARTIAL':
                count = 0.5  # Count as half
                loss_count = 0.25
            else:
                continue
            
            # If no correlations detected, skip
            if not parlay.get('correlation_types'):
                continue
            
            # Add to stats for each correlation type in parlay
            for corr_type in parlay['correlation_types']:
                correlation_stats[corr_type]['total'] += count
                if loss_count:
                    correlation_stats[corr_type]['losses'] += loss_count
                else:
                    correlation_stats[corr_type]['wins'] += count
        
        # Calculate loss rates and expected rates
        analysis = {}
        for corr_type, stats in correlation_stats.items():
            total = stats['total']
            losses = stats['losses']
            
            if total == 0:
                continue
            
            loss_rate = losses / total
            
            # Get current strength (try both orderings)
            agents = corr_type.split('+')
            if len(agents) == 2:
                key1 = tuple(agents)
                key2 = (agents[1], agents[0])
                strength = self.current_strengths.get(key1) or self.current_strengths.get(key2)
            else:
                strength = 1.0  # Unknown
            
            # Expected loss rate (rough proxy: higher strength = more losses expected)
            # This is empirical and should be refined over time
            expected_loss_rate = 0.5 + (strength - 1.0) * 0.2  # Range: 0.4 to 0.7
            
            analysis[corr_type] = {
                'total_parlays': total,
                'wins': stats['wins'],
                'losses': losses,
                'loss_rate': round(loss_rate, 2),
                'current_strength': strength or 1.0,
                'expected_loss_rate': round(expected_loss_rate, 2),
                'accuracy': 'accurate' if abs(loss_rate - expected_loss_rate) < 0.15 else (
                    'too_lenient' if loss_rate > expected_loss_rate else 'too_harsh'
                )
            }
        
        return analysis
    
    def recommend_adjustments(self) -> List[Dict]:
        """
        Recommend strength adjustments based on actual vs expected loss rates.
        
        Returns:
            List of adjustment recommendations
        """
        analysis = self.analyze_by_correlation_type()
        recommendations = []
        
        for corr_type, stats in analysis.items():
            actual_loss_rate = stats['loss_rate']
            expected_loss_rate = stats['expected_loss_rate']
            current_strength = stats['current_strength']
            accuracy = stats['accuracy']
            
            # Only recommend if we have enough data
            if stats['total_parlays'] < 3:
                continue
            
            if accuracy == 'too_harsh':
                # Loss rate lower than expected, strength should be lower
                adjustment = -0.1
                new_strength = current_strength + adjustment
                recommendations.append({
                    'correlation_type': corr_type,
                    'issue': f"Too harsh (actual loss {actual_loss_rate}, expected {expected_loss_rate})",
                    'current_strength': current_strength,
                    'recommended_strength': max(0.5, new_strength),  # Floor at 0.5
                    'adjustment': adjustment,
                    'confidence': 'MEDIUM' if stats['total_parlays'] < 5 else 'HIGH'
                })
            
            elif accuracy == 'too_lenient':
                # Loss rate higher than expected, strength should be higher
                adjustment = +0.1
                new_strength = current_strength + adjustment
                recommendations.append({
                    'correlation_type': corr_type,
                    'issue': f"Too lenient (actual loss {actual_loss_rate}, expected {expected_loss_rate})",
                    'current_strength': current_strength,
                    'recommended_strength': min(1.5, new_strength),  # Ceiling at 1.5
                    'adjustment': adjustment,
                    'confidence': 'MEDIUM' if stats['total_parlays'] < 5 else 'HIGH'
                })
        
        return recommendations
    
    def print_analysis(self):
        """Print formatted analysis and recommendations"""
        print("\n" + "="*80)
        print("CORRELATION STRENGTH CALIBRATION ANALYSIS")
        print("="*80 + "\n")
        
        analysis = self.analyze_by_correlation_type()
        
        if not analysis:
            print("No correlation data available yet. Continue logging parlays.\n")
            return
        
        print("CURRENT CORRELATION PERFORMANCE:")
        print("-" * 80)
        print(f"{'Correlation Type':<20} {'Total':<8} {'Loss%':<8} {'Expected':<10} {'Status':<12}")
        print("-" * 80)
        
        for corr_type, stats in sorted(analysis.items()):
            status = stats['accuracy'].replace('_', ' ').upper()
            print(f"{corr_type:<20} {int(stats['total_parlays']):<8} "
                  f"{stats['loss_rate']:<8.0%} {stats['expected_loss_rate']:<10.0%} {status:<12}")
        
        print("\n" + "="*80)
        print("RECOMMENDED ADJUSTMENTS:")
        print("="*80 + "\n")
        
        recommendations = self.recommend_adjustments()
        
        if not recommendations:
            print("All correlations performing within expected ranges. No adjustments needed.\n")
        else:
            for rec in recommendations:
                print(f"⚙️  {rec['correlation_type']}")
                print(f"    Issue: {rec['issue']}")
                print(f"    Current Strength: {rec['current_strength']:.1f}")
                print(f"    → Recommended: {rec['recommended_strength']:.1f} "
                      f"({rec['adjustment']:+.1f})")
                print(f"    Confidence: {rec['confidence']}")
                print()
        
        print("="*80 + "\n")
    
    def export_calibration_data(self, format: str = 'json') -> Path:
        """
        Export calibration data for backup/analysis.
        
        Args:
            format: 'json' or 'csv'
            
        Returns:
            Path to exported file
        """
        if format == 'json':
            filename = f"calibration_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.data_dir / filename
            with open(filepath, 'w') as f:
                json.dump(self.data, f, indent=2)
        
        elif format == 'csv':
            import csv
            filename = f"calibration_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', newline='') as f:
                if not self.data['parlays']:
                    return filepath
                
                writer = csv.DictWriter(f, fieldnames=self.data['parlays'][0].keys())
                writer.writeheader()
                for parlay in self.data['parlays']:
                    # Convert lists to strings for CSV
                    row = {k: str(v) if isinstance(v, list) else v for k, v in parlay.items()}
                    writer.writerow(row)
        
        print(f"✓ Exported calibration data to {filepath}")
        return filepath
    
    def get_summary_stats(self) -> Dict:
        """Get overall summary statistics"""
        parlays = self.data['parlays']
        
        if not parlays:
            return {'total_parlays': 0}
        
        results = defaultdict(int)
        total_correlated = 0
        total_units = 0
        total_potential = 0
        
        for p in parlays:
            results[p['result']] += 1
            if p['correlation_types']:
                total_correlated += 1
            total_units += p.get('units_bet', 0)
            total_potential += p.get('payout_if_win', 0)
        
        return {
            'total_parlays': len(parlays),
            'wins': results.get('WIN', 0),
            'losses': results.get('LOSS', 0),
            'pushes': results.get('PUSH', 0),
            'with_correlations': total_correlated,
            'correlation_rate': round(total_correlated / len(parlays), 2) if parlays else 0,
            'total_units_wagered': total_units,
            'total_potential_return': total_potential,
        }


def main():
    """Demo usage"""
    tracker = CorrelationCalibrationTracker()
    
    # Example: Log some sample parlays
    tracker.log_parlay(
        parlay_id="2025-11-17-001",
        correlation_types=["DVOA+Matchup"],
        initial_confidence=75,
        final_confidence=68,
        result="LOSS",
        parlay_size=3,
        units_bet=0.5,
        notes="KC passing correlation"
    )
    
    tracker.log_parlay(
        parlay_id="2025-11-17-002",
        correlation_types=["Volume+Trend"],
        initial_confidence=70,
        final_confidence=67,
        result="WIN",
        parlay_size=2,
        units_bet=1.0,
        notes="Low correlation strength, still won"
    )
    
    # Print analysis
    tracker.print_analysis()
    
    # Export data
    tracker.export_calibration_data('json')


if __name__ == "__main__":
    main()
