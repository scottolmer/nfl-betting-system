
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, data_dir=None, custom_weights=None):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data")
        self.results_dir = self.data_dir / "backtest_results"
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.custom_weights = custom_weights  # Optional weights for optimization
        
    def run_backtest(self, week: int, min_confidence: int = 50):
        """
        Run the analysis pipeline for a historical week.
        """
        logger.info(f"🚀 Starting Backtest for Week {week}...")
        
        # 1. Load Historical Data
        loader = NFLDataLoader(data_dir=str(self.data_dir))
        # This automatically looks for files like "wk{week}_dvoa..." etc.
        context = loader.load_all_data(week=week)
        
        if not context.get('props'):
            logger.error(f"❌ No props found for Week {week}. Check if 'wk{week}_betting_lines_draftkings.csv' exists.")
            return None
            
        logger.info(f"✓ Loaded {len(context['props'])} base props for Week {week}")
        
        # 2. Analyze Props
        logger.info("🧠 Analyzing props with historical data...")
        analyzer = PropAnalyzer(custom_weights=self.custom_weights)
        all_analyses = analyzer.analyze_all_props(context, min_confidence=min_confidence)
        logger.info(f"✓ Generated {len(all_analyses)} analyses with confidence >= {min_confidence}")
        
        # 3. Serialize Predictions for Grading
        predictions = []
        for a in all_analyses:
            predictions.append({
                'player_name': a.prop.player_name,
                'team': a.prop.team,
                'opponent': a.prop.opponent,
                'stat_type': a.prop.stat_type,
                'line': a.prop.line,
                'bet_type': a.prop.bet_type,
                'confidence': a.final_confidence,
                'agents': {name: score for name, score in a.agent_breakdown.items()},
                'is_home': a.prop.is_home
            })
            
        # 4. Save Predictions
        output_file = self.results_dir / f"predictions_week_{week}.json"
        with open(output_file, 'w') as f:
            json.dump(predictions, f, indent=2)
            
        logger.info(f"💾 Saved {len(predictions)} predictions to {output_file}")
        
        # 5. Build Parlays (Optional match check)
        # We can also save the "betting card" parlays to see what the system WOULD have recommended
        parlay_builder = ParlayBuilder()
        # Diversify first (mimic run_analysis logic)
        diversified = self._diversify_props_simple(all_analyses)
        parlays = parlay_builder.build_parlays(diversified, min_confidence=52)
        
        # Save parlays structure
        parlay_output_file = self.results_dir / f"parlays_week_{week}.json"
        
        # Helper to serialze parlay objects
        def serialize_parlay(p_list):
            return [{
                'confidence': p.combined_confidence,
                'legs': [f"{l.prop.player_name} {l.prop.stat_type} {l.prop.bet_type} {l.prop.line}" for l in p.legs],
                'risk': p.risk_level,
                'units': p.recommended_units
            } for p in p_list]

        serialized_parlays = {
            k: serialize_parlay(v) for k, v in parlays.items()
        }
        
        with open(parlay_output_file, 'w') as f:
            json.dump(serialized_parlays, f, indent=2)
            
        logger.info(f"💾 Saved generated parlays to {parlay_output_file}")
        
        return output_file

    def run_backtest_in_memory(self, week: int, min_confidence: int = 50):
        """
        Run backtest and return predictions in memory (no file I/O).
        Used by weight optimizer for fast iteration.

        Returns:
            List of prediction dicts with keys: player_name, team, opponent, stat_type,
            line, bet_type, confidence
        """
        # 1. Load Historical Data
        loader = NFLDataLoader(data_dir=str(self.data_dir))
        context = loader.load_all_data(week=week)

        if not context.get('props'):
            return []

        # 2. Analyze Props (suppress logging for speed)
        analyzer = PropAnalyzer(custom_weights=self.custom_weights)
        all_analyses = analyzer.analyze_all_props(context, min_confidence=min_confidence)

        # 3. Return predictions directly (no file write)
        predictions = []
        for a in all_analyses:
            predictions.append({
                'player_name': a.prop.player_name,
                'team': a.prop.team,
                'opponent': a.prop.opponent,
                'stat_type': a.prop.stat_type,
                'line': a.prop.line,
                'bet_type': a.prop.bet_type,
                'confidence': a.final_confidence,
            })

        return predictions

    def _diversify_props_simple(self, all_analyses):
        # Simplified version of run_analysis.diversify_props
        games = {}
        for analysis in all_analyses:
            game = f"{analysis.prop.team}_{analysis.prop.opponent}"
            if game not in games: games[game] = []
            games[game].append(analysis)
            
        diversified = []
        max_rounds = max(len(p) for p in games.values()) if games else 0
        for i in range(max_rounds):
            for game in games:
                if i < len(games[game]):
                    diversified.append(games[game][i])
        return diversified

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, required=True, help='Week to backtest')
    args = parser.parse_args()
    
    engine = BacktestEngine()
    engine.run_backtest(args.week)
