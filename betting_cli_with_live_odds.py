#!/usr/bin/env python
"""NFL Betting System CLI with DraftKings Odds"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_optimizer import ParlayOptimizer
from scripts.analysis.odds_integration import OddsIntegrator, integrate_odds_with_analysis
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class BettingAnalyzerCLI:
    def __init__(self):
        self.analyzer = PropAnalyzer()
        self.loader = NFLDataLoader(data_dir=str(project_root / "data"))
        self.odds_integrator = OddsIntegrator(data_dir=str(project_root / "data"))
        self.week = 10
        self.last_parlays = []
        self.bankroll = 1000
        
        print("\n" + "="*70)
        print("🏈 NFL BETTING SYSTEM - DRAFTKINGS ODDS INTEGRATION")
        print("="*70 + "\n")
    
    def print_header(self):
        """Print available commands"""
        print("COMMANDS:")
        print("  pull-lines               - Refresh DraftKings betting lines")
        print("  opt-parlays [quality]    - Generate optimized parlays with DraftKings odds")
        print("  odds-status              - Show odds status")
        print("  week <number>            - Change week")
        print("  help                     - Show all commands")
        print("  exit/quit                - Exit\n")
    
    def pull_lines(self):
        """Refresh DraftKings betting lines"""
        print(f"\n📡 Fetching fresh DraftKings betting lines for Week {self.week}...")
        
        # Load data to trigger refresh
        context = self.loader.load_all_data(week=self.week)
        original_props = context.get('props', [])
        
        # Integrate with odds (this loads from cache but could trigger API)
        enriched_props, odds_source = integrate_odds_with_analysis(
            original_props,
            week=self.week,
            data_dir=str(project_root / "data")
        )
        
        print(f"✅ Loaded {len(enriched_props)} DraftKings betting lines ({odds_source})")
        print(f"   Ready to generate parlays with 'opt-parlays'\n")
    
    def generate_optimized_parlays_with_odds(self, quality_threshold_str="65"):
        """Generate optimized parlays with DraftKings odds"""
        try:
            quality_threshold = int(quality_threshold_str)
        except ValueError:
            quality_threshold = 65
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        original_props = context.get('props', [])
        
        print(f"\n📡 Integrating DraftKings odds...")
        enriched_props, odds_source = integrate_odds_with_analysis(
            original_props,
            week=self.week,
            data_dir=str(project_root / "data")
        )
        
        print(f"✅ Props enriched with {odds_source} odds data: {len(enriched_props)} props")
        
        context['props'] = enriched_props
        
        print(f"\n📊 Analyzing {len(enriched_props)} props...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=50)
        print(f"✅ Analyzed {len(all_analyses)} props")
        
        print(f"\n🔄 Generating optimized parlays (threshold: {quality_threshold}+)...")
        optimizer = ParlayOptimizer()
        
        optimized_data = optimizer.rebuild_parlays_low_correlation(
            all_analyses,
            target_parlays=10,
            min_confidence=quality_threshold
        )
        
        self.last_parlays = optimized_data
        
        print(f"\n" + "="*70)
        print(f"✅ OPTIMIZED PARLAYS - Week {self.week} ({odds_source} DraftKings)")
        print("="*70 + "\n")
        
        if optimized_data:
            for ptype in ['2-leg', '3-leg', '4-leg']:
                parlays = optimized_data.get(ptype, [])
                for i, parlay in enumerate(parlays, 1):
                    print(f"🎯 {ptype.upper()} PARLAY {i}")
                    print(f"   Confidence: {parlay.combined_confidence}%")
                    for leg in parlay.legs:
                        print(f"      • {leg.prop.player_name} ({leg.prop.team}) - {leg.prop.stat_type} {leg.prop.bet_type} {leg.prop.line}")
                    print()
    
    def show_odds_status(self):
        """Display odds status"""
        self.odds_integrator.print_odds_status()
    
    def run(self):
        """Main CLI loop"""
        self.print_header()
        
        while True:
            try:
                cmd = input("📊 Enter command: ").strip().lower()
                
                if not cmd:
                    continue
                elif cmd == "help":
                    self.print_header()
                elif cmd == "pull-lines":
                    self.pull_lines()
                elif cmd.startswith("opt-parlays"):
                    quality = cmd.split()[-1] if len(cmd.split()) > 1 else "65"
                    self.generate_optimized_parlays_with_odds(quality)
                elif cmd == "odds-status":
                    self.show_odds_status()
                elif cmd.startswith("week"):
                    try:
                        week = int(cmd.split()[-1])
                        self.week = week
                        print(f"\n✅ Week changed to {week}\n")
                    except ValueError:
                        print("❌ Invalid week number\n")
                elif cmd in ["exit", "quit"]:
                    print("\n👋 Goodbye!\n")
                    break
                else:
                    print("❌ Unknown command. Type 'help' for options.\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    cli = BettingAnalyzerCLI()
    cli.run()
