
import sys
import json
import logging
from pathlib import Path
import pandas as pd
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Direct import to avoid circular dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "data_loader",
    project_root / "scripts" / "analysis" / "data_loader.py"
)
data_loader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_loader_module)
normalize_name = data_loader_module.normalize_name

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ResultGrader:
    def __init__(self, data_dir=None):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data")
        self.results_dir = self.data_dir / "backtest_results"
        
    def load_actual_stats(self, week: int):
        """
        Load actual stats from all base files for the given week.
        Returns a dict: {player_name: {stat_type: value}}
        """
        stats_map = {}
        
        # Map stat types to (file_suffix, column_name)
        # We need to cover: Pass Yds, Pass TDs, Rush Yds, Rec Yds, Receptions
        files_to_load = [
            (f"wk{week}_passing_base.csv", [
                ('pass_yds', 'YDS'), 
                ('pass_td', 'TD'),
                ('pass_attempts', 'ATT'),
                ('pass_completions', 'COM')
            ]),
            (f"wk{week}_rushing_base.csv", [
                ('rush_yds', 'YDS'),
                ('rush_attempts', 'ATT')
            ]),
            (f"wk{week}_receiving_base.csv", [
                ('rec_yds', 'YDS'),
                ('receptions', 'REC')
            ])
        ]
        
        for filename, mappings in files_to_load:
            fpath = self.data_dir / filename
            if not fpath.exists():
                logger.warning(f"⚠️ Missing stats file: {filename}")
                continue
                
            try:
                # Robust header detection
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                
                header_row = 0
                for i, line in enumerate(lines):
                    if 'Player' in line and 'Tm' in line:
                        header_row = i
                        break
                
                df = pd.read_csv(fpath, header=header_row)
                
                # Check again if we loaded correctly
                if 'Player' not in df.columns and 'Rk' in df.columns:
                     # sometimes Rk is first, but Player should be there.
                     pass

                for _, row in df.iterrows():
                    # Skip if row is just garbage/git markers
                    if not isinstance(row.get('Player'), str): continue
                    if 'BASIC' in str(row.get('Player')): continue
                    player = normalize_name(row.get('Player', ''))
                    if not player: continue
                    
                    if player not in stats_map: stats_map[player] = {}
                    
                    for stat_key, col_name in mappings:
                        try:
                            val = row.get(col_name, 0)
                            stats_map[player][stat_key] = float(val)
                        except:
                            stats_map[player][stat_key] = 0.0
                            
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                
        return stats_map

    def grade_week(self, week: int):
        """
        Grade the predictions for a specific week.
        """
        pred_file = self.results_dir / f"predictions_week_{week}.json"
        if not pred_file.exists():
            logger.error(f"❌ Predictions file not found: {pred_file}")
            return
            
        with open(pred_file, 'r') as f:
            predictions = json.load(f)
            
        actuals = self.load_actual_stats(week)
        graded_results = []
        
        wins = 0
        total = 0
        
        logger.info(f"📊 Grading Week {week} Results...")
        
        # Mapping bet stat types to our internal keys
        stat_type_map = {
            'player_pass_yds': 'pass_yds',
            'player_pass_tds': 'pass_td',
            'player_pass_attempts': 'pass_attempts',
            'player_pass_completions': 'pass_completions',
            'player_rush_yds': 'rush_yds',
            'player_rush_attempts': 'rush_attempts',
            'player_reception_yds': 'rec_yds',
            'player_receptions': 'receptions'
        }
        
        sample_keys = list(actuals.keys())[:5]
        logger.info(f"DEBUG: Loaded {len(actuals)} players in actuals. Samples: {sample_keys}")
        
        for p in predictions:
            player = normalize_name(p['player_name'])
            stat_type_raw = p['stat_type'].lower() # Lowercase for matching
            line = p['line']
            bet_type = p['bet_type'] # 'Over' or 'Under'
            
            # Map stat type
            internal_key = stat_type_map.get(stat_type_raw)
            if not internal_key:
                # Try simple matching
                if 'pass' in stat_type_raw and 'yds' in stat_type_raw: internal_key = 'pass_yds'
                elif 'pass' in stat_type_raw and 'td' in stat_type_raw: internal_key = 'pass_td'
                elif 'pass' in stat_type_raw and 'att' in stat_type_raw: internal_key = 'pass_attempts'
                elif 'pass' in stat_type_raw and 'comp' in stat_type_raw: internal_key = 'pass_completions'
                elif 'rush' in stat_type_raw and 'yds' in stat_type_raw: internal_key = 'rush_yds'
                elif 'rush' in stat_type_raw and 'att' in stat_type_raw: internal_key = 'rush_attempts'
                elif 'rec' in stat_type_raw and 'yds' in stat_type_raw: internal_key = 'rec_yds'
                elif 'recep' in stat_type_raw: internal_key = 'receptions'
            
            # Get actual
            actual_val = 0
            found = False
            
            if player in actuals:
                if internal_key in actuals[player]:
                    actual_val = actuals[player][internal_key]
                    found = True
            
            # If not found but we have the player, assume 0 for that stat? 
            # Or if player completely missing, maybe they didn't play (void?)
            # For backtesting simplicity: if predicted and not found, assume 0 implies loss OR void. 
            # We'll assume Loss for now if player data missing? No, that's unfair. 
            # But wait, looking at the files, inactive players aren't in the box score?
            # Let's mark as 'VOID/MISSING' if player not in actuals.
            
            result = 'UNKNOWN'
            if player not in actuals:
                result = 'VOID' 
            elif not found:
                 # Player played but didn't correct stat? e.g. QB logic for rushing?
                 # If we have player but no 'rush_yds' key, it means they weren't in rushing file. 
                 # Thus 0 yards.
                 actual_val = 0
                 found = True
            
            if found:
                if bet_type.lower() == 'over':
                    result = 'WIN' if actual_val > line else 'LOSS'
                elif bet_type.lower() == 'under':
                    result = 'WIN' if actual_val < line else 'LOSS'
                else:
                    result = 'PUSH' if actual_val == line else result
            else:
                if len(graded_results) < 5:
                    logger.info(f"DEBUG: Failed match for {player} - Key: {internal_key}. In Actuals? {player in actuals}")
                    if player in actuals:
                        logger.info(f"   Available keys: {list(actuals[player].keys())}")

            p['actual_value'] = actual_val
            p['result'] = result
            graded_results.append(p)
            
            if result == 'WIN': wins += 1
            if result in ['WIN', 'LOSS']: total += 1
            
        # Summary
        win_rate = (wins / total * 100) if total > 0 else 0
        logger.info(f"✅ Graded {len(graded_results)} bets.")
        logger.info(f"🏆 Win Rate: {win_rate:.1f}% ({wins}/{total})")
        
        # Save graded
        output_file = self.results_dir / f"graded_week_{week}.json"
        with open(output_file, 'w') as f:
            json.dump(graded_results, f, indent=2)
            
        logger.info(f"💾 Saved graded results to {output_file}")
        return output_file

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, required=True, help='Week to grade')
    args = parser.parse_args()
    
    grader = ResultGrader()
    grader.grade_week(args.week)
