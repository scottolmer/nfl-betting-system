#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import sys
import os

# Get absolute path to data folder
script_dir = Path(__file__).parent
root_dir = script_dir.parent
data_dir = root_dir / 'data'

class PropAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.load_data()
    
    def load_data(self):
        print("\n📂 Loading Data...")
        self.lines = pd.read_csv(self.data_dir / 'wk7_betting_lines_TRANSFORMED.csv')
        self.dvoa_off = pd.read_csv(self.data_dir / 'wk7_offensive_DVOA.csv')
        self.dvoa_def = pd.read_csv(self.data_dir / 'w7_defensive_DVOA.csv')
        self.injuries = pd.read_csv(self.data_dir / 'week7_injury_report.txt')
        
        print(f"✅ Betting Lines: {len(self.lines)} props")
        print(f"✅ DVOA Off: {len(self.dvoa_off)} teams")
        print(f"✅ DVOA Def: {len(self.dvoa_def)} teams")
        print(f"✅ Injuries: {len(self.injuries)} players")
        print(f"✅ Games: {len(self.games)} games")
    
    def analyze_all(self):
        print(f"\n🧠 Analyzing {len(self.lines)} props...")
        results = []
        for idx, row in self.lines.iterrows():
            result = self.score_prop(row)
            results.append(result)
        results = sorted(results, key=lambda x: x['Confidence'], reverse=True)
        return results
    
    def score_prop(self, row):
        home = row['home_team']
        away = row['away_team']
        player = row['player_name']
        prop_type = row['prop_type']
        line = row['line']
        
        home_dvoa = self.dvoa_off[self.dvoa_off['Tm'] == home]['DVOA'].values
        home_off_score = (50 + home_dvoa[0] * 1.5) if len(home_dvoa) > 0 else 50
        
        away_def = self.dvoa_def[self.dvoa_def['Tm'] == away]['DVOA'].values
        away_def_score = (50 - away_def[0] * 1.5) if len(away_def) > 0 else 50
        
        aly_score = 50
        if prop_type in ['rush_yds', 'rush_attempts']:
            aly = self.aly_off[self.aly_off['Team'] == home]['ALYards'].values
            if len(aly) > 0:
                aly_score = 50 + (aly[0] - 5.0) * 5
        
        game = self.games[(self.games['Home'] == home) & (self.games['Away'] == away)]
        game_total = (game['Home Pts'].values[0] + game['Away Pts'].values[0]) if len(game) > 0 else 45
        total_score = 50 + (game_total - 44) * 1.5
        
        injury_score = 50
        inj = self.injuries[(self.injuries['Player'].str.contains(player.split()[0], na=False, case=False)) & (self.injuries['Team'] == home)]
        if len(inj) > 0:
            status = inj['Status'].values[0]
            injury_score = 0 if status == 'OUT' else (25 if status == 'DOUBTFUL' else 40)
        
        confidence = (home_off_score * 0.25 + away_def_score * 0.30 + aly_score * 0.20 + total_score * 0.15 + injury_score * 0.10)
        confidence = max(0, min(100, confidence))
        ev = (confidence - 52.4) / 100
        
        return {'Player': player, 'Team': home, 'Opp': away, 'Prop': prop_type.upper(), 'Line': line, 'Confidence': round(confidence, 1), 'EV': f"{ev:+.1%}"}
    
    def print_results(self, results, top_n=50):
        print("\n" + "="*100)
        print("🎯 TOP PROPS")
        print("="*100)
        df = pd.DataFrame(results[:top_n])
        print(df.to_string(index=False))
        
        high_conf = len([r for r in results if r['Confidence'] >= 70])
        med_conf = len([r for r in results if 60 <= r['Confidence'] < 70])
        pos_ev = len([r for r in results if '+' in r['EV']])
        
        print(f"\n📊 STATS:")
        print(f"   70+ Confidence: {high_conf}")
        print(f"   60-69 Confidence: {med_conf}")
        print(f"   Positive EV: {pos_ev}")
        
        df_export = pd.DataFrame([r for r in results if r['Confidence'] >= 50])
        df_export.to_csv(root_dir / 'week7_results.csv', index=False)
        print(f"\n✅ Exported {len(df_export)} props to week7_results.csv")

if __name__ == '__main__':
    print(f"Data directory: {data_dir}")
    analyzer = PropAnalyzer(data_dir)
    results = analyzer.analyze_all()
    analyzer.print_results(results, top_n=50)