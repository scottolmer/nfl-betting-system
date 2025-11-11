#!/usr/bin/env python
"""NFL Betting Prop Analyzer - CLI Tool with LIVE Odds API Integration"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.api.claude_query_handler import ClaudeQueryHandler
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.api.odds_api import OddsAPI
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.WARNING)

class BettingAnalyzerCLI:
    def __init__(self):
        self.handler = ClaudeQueryHandler()
        self.analyzer = PropAnalyzer()
        self.loader = NFLDataLoader(data_dir=str(project_root / "data"))
        self.parlay_builder = ParlayBuilder()
        self.week = 9
        self.odds_api = None
        
        # Try to initialize Odds API
        try:
            self.odds_api = OddsAPI()
        except ValueError as e:
            print(f"⚠️  Odds API not initialized: {e}")
    
    def print_header(self):
        print("\n" + "="*60)
        print("🏈 NFL BETTING PROP ANALYZER (LIVE ODDS)")
        print("="*60)
        print("Commands:")
        print("  analyze <query>     - Analyze a prop (e.g., 'Jordan Love 250 pass yards')")
        print("  parlays [conf]      - Generate parlays (min confidence, default: 58)")
        print("  week <number>       - Change week (default: 8)")
        print("  odds                - Check Odds API quota")
        print("  help               - Show this message")
        print("  exit/quit          - Exit program")
        print("="*60 + "\n")
    
    def fetch_fresh_odds(self):
        """Fetch fresh player props from The Odds API and save to CSV"""
        if not self.odds_api:
            print("⚠️  Odds API not initialized. Check your ODDS_API_KEY in .env\n")
            return False
        
        try:
            print("📡 Connecting to The Odds API...")
            
            # Check quota
            quota = self.odds_api.check_api_quota()
            print(f"   Requests available: {quota['remaining']}")
            
            # Fetch live props
            print("   Fetching live player props...")
            props = self.odds_api.get_player_props()
            
            if not props:
                print("⚠️  No props returned from API\n")
                return False
            
            print(f"✅ Fetched {len(props)} live props\n")
            
            # Convert to DataFrame
            df = pd.DataFrame(props)
            df['fetch_time'] = datetime.now().isoformat()
            df['week'] = self.week
            
            # Save to CSV
            output_file = project_root / "data" / f"betting_lines_wk_{self.week}_live.csv"
            df.to_csv(output_file, index=False)
            print(f"💾 Saved to: {output_file}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching odds: {e}\n")
            return False
    
    def analyze_prop(self, query):
        """Analyze a betting prop with live odds"""
        if not query:
            print("❌ Please provide a query\n")
            return
        
        # Fetch fresh odds before analysis
        self.fetch_fresh_odds()
        
        # Run analysis
        print(f"🔄 Analyzing: {query}...\n")
        response = self.handler.query(query, week=self.week)
        print(response)
    
    def check_odds_quota(self):
        """Check remaining Odds API quota"""
        if not self.odds_api:
            print("❌ Odds API not initialized\n")
            return
        
        try:
            quota = self.odds_api.check_api_quota()
            print(f"\n📊 Odds API Quota Status")
            print(f"   Requests used: {quota['used']}")
            print(f"   Requests remaining: {quota['remaining']}\n")
        except Exception as e:
            print(f"❌ Error checking quota: {e}\n")
    
    def generate_parlays(self, min_conf_str="58"):
        """Generate parlay combinations"""
        try:
            min_conf = int(min_conf_str)
        except ValueError:
            min_conf = 58
        
        # Fetch fresh odds first
        print(f"\n📡 Fetching fresh odds for Week {self.week}...")
        self.fetch_fresh_odds()
        
        print(f"\n🏵 Fetching fresh injury data...")
        try:
            from scripts.fetch_injuries_auto import fetch_and_prepare_injuries
            fetch_and_prepare_injuries(self.week, Path(project_root) / "data")
        except Exception as e:
            print(f"⚠️  Could not fetch fresh injuries: {e}")
        
        print(f"\n🔄 Loading data and analyzing all props for Week {self.week}...")
        
        # Load context
        context = self.loader.load_all_data(week=self.week)
        
        # Analyze all props
        props_list = context.get('props', [])
        print(f"📊 Analyzing {len(props_list)} props...")
        all_analyses = []
        confidence_distribution = {'0-20': 0, '20-40': 0, '40-50': 0, '50-60': 0, '60-70': 0, '70-80': 0, '80+': 0}
        
        for i, prop in enumerate(props_list, 1):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(props_list)}")
            
            try:
                analysis = self.analyzer.analyze_prop(prop, context)
                if analysis:
                    all_analyses.append(analysis)
                    conf = analysis.final_confidence
                    if conf >= 80: confidence_distribution['80+'] += 1
                    elif conf >= 70: confidence_distribution['70-80'] += 1
                    elif conf >= 60: confidence_distribution['60-70'] += 1
                    elif conf >= 50: confidence_distribution['50-60'] += 1
                    elif conf >= 40: confidence_distribution['40-50'] += 1
                    elif conf >= 20: confidence_distribution['20-40'] += 1
                    else: confidence_distribution['0-20'] += 1
            except Exception as e:
                if i <= 3:
                    print(f"      Error analyzing prop {i}: {e}")
                pass
        
        print(f"✅ Analyzed {len(all_analyses)} props")
        print(f"📊 Confidence Distribution:")
        for range_label, count in confidence_distribution.items():
            pct = (count / len(props_list) * 100) if props_list else 0
            print(f"   {range_label}: {count} props ({pct:.1f}%)")
        
        # Build parlays
        parlays = self.parlay_builder.build_parlays(all_analyses, min_confidence=min_conf)
        
        # Format and display
        output = self.parlay_builder.format_parlays_for_betting(parlays)
        print(output)
        print()
    
    def change_week(self, week_str):
        """Change the NFL week"""
        try:
            week = int(week_str)
            if 1 <= week <= 18:
                self.week = week
                print(f"✅ Week set to {week}\n")
            else:
                print("❌ Week must be between 1-18\n")
        except ValueError:
            print("❌ Invalid week number\n")
    
    def run(self):
        """Main CLI loop"""
        self.print_header()
        
        while True:
            try:
                user_input = input("📊 Enter command: ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split(None, 1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if command == 'analyze':
                    self.analyze_prop(arg)
                elif command == 'parlays':
                    self.generate_parlays(arg)
                elif command == 'week':
                    self.change_week(arg)
                elif command == 'odds':
                    self.check_odds_quota()
                elif command == 'help':
                    self.print_header()
                elif command in ['exit', 'quit']:
                    print("👋 Goodbye!\n")
                    break
                else:
                    print("❌ Unknown command. Type 'help' for options\n")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    cli = BettingAnalyzerCLI()
    cli.run()
