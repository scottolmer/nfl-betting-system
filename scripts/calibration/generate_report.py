
import sys
import json
import logging
from pathlib import Path
from collections import defaultdict
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class CalibrationReporter:
    def __init__(self, data_dir=None):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data")
        self.results_dir = self.data_dir / "backtest_results"
        
    def generate_report(self):
        """
        Aggregate all graded files and generate a calibration report.
        """
        # Find all graded files
        files = list(self.results_dir.glob("graded_week_*.json"))
        if not files:
            logger.warning("⚠️ No graded result files found in backtest_results/")
            return

        all_bets = []
        for f in files:
            try:
                with open(f, 'r') as json_file:
                    bets = json.load(json_file)
                    all_bets.extend(bets)
            except Exception as e:
                logger.error(f"Error reading {f}: {e}")
                
        logger.info(f"📊 Aggregated {len(all_bets)} total bets from {len(files)} weeks.")
        
        # Bucketing
        buckets = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for bet in all_bets:
            conf = bet.get('confidence', 0)
            result = bet.get('result')
            
            if result not in ['WIN', 'LOSS']: continue # Skip voids/pushes
            
            # Bucket by 5s: 50-54, 55-59 ...
            bucket_floor = int(conf // 5) * 5
            bucket_key = f"{bucket_floor}-{bucket_floor+4}"
            
            buckets[bucket_key]['total'] += 1
            if result == 'WIN':
                buckets[bucket_key]['wins'] += 1
                
        # Print Report
        print("\n" + "="*60)
        print("📈 CALIBRATION REPORT (Predicted vs Actual)")
        print("="*60)
        print(f"{'Confidence':<15} {'Count':<10} {'Win Rate':<10} {'Diff from Mid':<15}")
        print("-" * 60)
        
        sorted_keys = sorted(buckets.keys(), key=lambda x: int(x.split('-')[0]))
        
        total_wins = 0
        total_graded = 0
        
        for k in sorted_keys:
            stats = buckets[k]
            total = stats['total']
            wins = stats['wins']
            win_rate = (wins / total * 100) if total > 0 else 0
            
            # Midpoint of bucket (e.g., 50-54 -> 52.0)
            midpoint = int(k.split('-')[0]) + 2
            diff = win_rate - midpoint
            
            # Formatting
            diff_str = f"{diff:+.1f}%"
            if abs(diff) > 10: diff_str += " ⚠️"
            
            print(f"{k:<15} {total:<10} {win_rate:.1f}%     {diff_str:<15}")
            
            total_wins += wins
            total_graded += total
            
        print("-" * 60)
        global_win_rate = (total_wins / total_graded * 100) if total_graded > 0 else 0
        print(f"{'TOTAL':<15} {total_graded:<10} {global_win_rate:.1f}%")
        print("="*60 + "\n")
        
        # --- AGENT BREAKDOWN ANALYSIS ---
        print("🕵️ AGENT PERFORMANCE ANALYSIS")
        print("="*60)
        # We want to see: When Agent X contributes significantly (high score), what is the win rate?
        
        agent_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
        
        for bet in all_bets:
            result = bet.get('result')
            if result not in ['WIN', 'LOSS']: continue
            
            agents = bet.get('agents', {})
            for agent_name, agent_data in agents.items():
                # Handle nested dict structure from JSON
                if isinstance(agent_data, dict):
                    score = agent_data.get('raw_score', 50)
                else:
                    score = agent_data # In case flattened later
                    
                # Only count if the agent was "active" / "confident"
                # e.g. score > 50 or < 50
                if abs(score - 50) >= 5: # Minimal contribution threshold
                    agent_stats[agent_name]['total'] += 1
                    if result == 'WIN':
                         agent_stats[agent_name]['wins'] += 1

        print(f"{'Agent':<15} {'Count':<10} {'Win Rate':<10} {'Diff from Global':<15}")
        print("-" * 60)
        
        for agent, stats in agent_stats.items():
            total = stats['total']
            wins = stats['wins']
            win_rate = (wins / total * 100) if total > 0 else 0
            diff = win_rate - global_win_rate
            
            diff_str = f"{diff:+.1f}%"
            indicator = ""
            if diff > 5: indicator = "🟢"
            elif diff < -5: indicator = "🔴"
            
            print(f"{agent:<15} {total:<10} {win_rate:.1f}%     {diff_str:<15} {indicator}")
        print("="*60 + "\n")

if __name__ == "__main__":
    reporter = CalibrationReporter()
    reporter.generate_report()
