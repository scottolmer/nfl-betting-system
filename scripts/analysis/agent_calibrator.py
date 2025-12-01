"""
Agent Calibration System
Analyzes historical agent performance and automatically adjusts weights
"""

import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
from agent_weight_manager import AgentWeightManager


class AgentCalibrator:
    def __init__(self, db_path: str):
        """Initialize with database connection"""
        self.db_path = db_path
        self.agents = [
            'DVOA', 'Matchup', 'Volume', 'Injury', 
            'Trend', 'GameScript', 'Variance', 'Weather'
        ]
    
    def get_logged_legs(self, week: int = None) -> List[Dict]:
        """Fetch all logged leg results from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if week:
            query = """
                SELECT l.leg_id, l.parlay_id, l.result, l.agent_scores,
                       p.confidence_score, p.week
                FROM legs l
                JOIN parlays p ON l.parlay_id = p.parlay_id
                WHERE p.week = ? AND l.result IS NOT NULL
                ORDER BY p.created_timestamp DESC
            """
            cursor.execute(query, (week,))
        else:
            query = """
                SELECT l.leg_id, l.parlay_id, l.result, l.agent_scores,
                       p.confidence_score, p.week
                FROM legs l
                JOIN parlays p ON l.parlay_id = p.parlay_id
                WHERE l.result IS NOT NULL
                ORDER BY p.created_timestamp DESC
            """
            cursor.execute(query)

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def calculate_agent_accuracy(self, legs: List[Dict]) -> Dict[str, Dict]:
        """Calculate accuracy metrics for each agent"""
        agent_stats = defaultdict(lambda: {
            'predictions': [],
            'actuals': [],
            'hits': 0,
            'total': 0,
            'accuracy': 0,
            'calibration_error': 0,
            'sample_size': 0
        })
        
        for leg in legs:
            if not leg['agent_scores']:
                continue

            actual = leg['result']  # 1 if hit, 0 if miss
            try:
                import json
                agent_scores = json.loads(leg['agent_scores']) if isinstance(leg['agent_scores'], str) else leg['agent_scores']
            except (json.JSONDecodeError, TypeError):
                continue
            
            for agent_name, score in agent_scores.items():
                # Convert agent score (0-100) to confidence (0-1)
                predicted_conf = score / 100.0
                agent_stats[agent_name]['predictions'].append(predicted_conf)
                agent_stats[agent_name]['actuals'].append(1 if actual else 0)
                agent_stats[agent_name]['total'] += 1
                
                if actual:
                    agent_stats[agent_name]['hits'] += 1
        
        # Calculate metrics
        for agent_name, stats in agent_stats.items():
            if stats['total'] > 0:
                # Sample size
                stats['sample_size'] = stats['total']

                # Actual accuracy
                stats['accuracy'] = stats['hits'] / stats['total']

                # Calibration error (predicted vs actual)
                total_error = sum(
                    abs(pred - actual)
                    for pred, actual in zip(stats['predictions'], stats['actuals'])
                )
                stats['calibration_error'] = total_error / stats['total']

                # Overconfidence: predicted higher than actual
                stats['overconfidence'] = (
                    sum(stats['predictions']) / len(stats['predictions']) - stats['accuracy']
                )

        return dict(agent_stats)
    
    def generate_recalibration_report(self, week: int = None) -> str:
        """Generate recalibration recommendations"""
        legs = self.get_logged_legs(week)
        
        if not legs:
            return "❌ No logged leg results found for calibration.\n"
        
        accuracy = self.calculate_agent_accuracy(legs)
        
        report = "\n" + "="*80 + "\n"
        report += "🔬 AGENT RECALIBRATION ANALYSIS\n"
        report += "="*80 + "\n\n"
        
        if week:
            report += f"Week {week} | {len(legs)} legs analyzed\n"
        else:
            report += f"All-time | {len(legs)} legs analyzed\n"
        
        report += "-"*80 + "\n\n"
        
        # Sort by calibration error
        sorted_agents = sorted(
            accuracy.items(),
            key=lambda x: x[1]['calibration_error'],
            reverse=True
        )
        
        report += "AGENT PERFORMANCE RANKING:\n"
        report += "-"*80 + "\n"
        
        for rank, (agent_name, stats) in enumerate(sorted_agents, 1):
            if stats['total'] < 3:
                status = "⚠️ (insufficient data)"
            elif stats['overconfidence'] > 0.15:
                status = "🔴 (overconfident)"
            elif stats['overconfidence'] < -0.15:
                status = "🔵 (underconfident)"
            else:
                status = "✅ (well-calibrated)"
            
            report += f"\n{rank}. {agent_name:15} {status}\n"
            report += f"   Accuracy:          {stats['accuracy']*100:.1f}% ({stats['hits']}/{stats['total']} hits)\n"
            report += f"   Calibration Error: {stats['calibration_error']:.3f}\n"
            report += f"   Overconfidence:   {stats['overconfidence']:+.3f}\n"
            
            # Recommendation
            if stats['total'] >= 3:
                if stats['overconfidence'] > 0.15:
                    report += f"   → REDUCE weight (agent too bullish)\n"
                elif stats['overconfidence'] < -0.15:
                    report += f"   → INCREASE weight (agent too conservative)\n"
                else:
                    report += f"   → OK (no adjustment needed)\n"
        
        report += "\n" + "="*80 + "\n"
        report += "WEIGHT ADJUSTMENT GUIDE:\n"
        report += "-"*80 + "\n"
        report += "• Overconfident agents: -0.5 weight per 0.1 overconfidence\n"
        report += "• Underconfident agents: +0.5 weight per 0.1 underconfidence\n"
        report += "• Sample size matters: <5 legs = unreliable\n"
        report += "="*80 + "\n\n"
        
        return report
    
    def get_agent_recommendation(self, agent_name: str, current_weight: float, week: int = None) -> Tuple[float, str]:
        """Get specific weight recommendation for an agent"""
        legs = self.get_logged_legs(week)
        accuracy = self.calculate_agent_accuracy(legs)
        
        if agent_name not in accuracy or accuracy[agent_name]['total'] < 3:
            return current_weight, "Insufficient data for recommendation"
        
        stats = accuracy[agent_name]
        overconf = stats['overconfidence']
        
        # Weight adjustment formula
        adjustment = -overconf * 5  # Amplify for weight adjustment
        new_weight = max(0.5, min(5.0, current_weight + adjustment))  # Clamp 0.5-5.0
        
        if abs(adjustment) < 0.2:
            reasoning = "Well-calibrated, no change needed"
        elif overconf > 0:
            reasoning = f"Over-predicting (by {overconf:.1%}), reduce weight"
        else:
            reasoning = f"Under-predicting (by {abs(overconf):.1%}), increase weight"
        
        return new_weight, reasoning


def calibrate_agents_interactive(db_path: str, week: int = None, auto_apply: bool = False):
    """Interactive calibration interface with optional auto-apply"""
    cal = AgentCalibrator(db_path)
    weight_manager = AgentWeightManager(db_path)

    # Show current weights
    print("\n📊 CURRENT WEIGHTS:")
    weight_manager.print_current_weights()

    # Generate calibration report
    print(cal.generate_recalibration_report(week))

    # Get agent performance
    legs = cal.get_logged_legs(week)
    agent_performance = cal.calculate_agent_accuracy(legs)

    # Check if auto-learning is enabled
    auto_learning_enabled = weight_manager.is_auto_learning_enabled()

    if auto_apply or auto_learning_enabled:
        print("\n🤖 AUTO-LEARNING ENABLED - Applying weight adjustments...\n")

        # Auto-adjust weights
        adjustments = weight_manager.auto_adjust_weights(
            agent_performance=agent_performance,
            week=week,
            dry_run=False
        )

        # Print adjustment summary
        weight_manager.print_adjustment_summary(adjustments)

        # Show updated weights
        print("\n✅ UPDATED WEIGHTS:")
        weight_manager.print_current_weights()

    else:
        print("\n📋 WEIGHT ADJUSTMENT RECOMMENDATIONS (dry run):\n")

        # Show what would be adjusted (dry run)
        adjustments = weight_manager.auto_adjust_weights(
            agent_performance=agent_performance,
            week=week,
            dry_run=True
        )

        weight_manager.print_adjustment_summary(adjustments)

        print("\n💡 To enable automatic weight adjustments:")
        print("   Run: calibrate-agents --auto-apply")
        print("   Or enable globally: from agent_weight_manager import AgentWeightManager")
        print("                       AgentWeightManager().enable_auto_learning()\n")


if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "bets.db"
    week = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    calibrate_agents_interactive(db_path, week)
