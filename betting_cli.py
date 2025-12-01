#!/usr/bin/env python
"""NFL Betting Prop Analyzer - CLI with optimized parlay generation"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.api.claude_query_handler import ClaudeQueryHandler
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.correlation_detector import EnhancedParlayBuilder
from scripts.analysis.parlay_optimizer import ParlayOptimizer
from scripts.analysis.dependency_analyzer import DependencyAnalyzer
from scripts.analysis.performance_tracker import PerformanceTracker
from scripts.analysis.agent_calibrator import AgentCalibrator
from scripts.analysis.kelly_optimizer import KellyOptimizer, format_kelly_report
from scripts.analysis.position_size_optimizer import PositionSizeOptimizer
from scripts.analysis.odds_integration import OddsIntegrator, integrate_odds_with_analysis
from scripts.utils.parlay_gui import show_parlays_gui
from scripts.utils.props_json_exporter import PropsJSONExporter
from scripts.utils.enhanced_props_exporter import EnhancedPropsExporter
from scripts.analysis.chat_interface import run_chat_interface
import auto_scorer
import prop_logger
import props_scorer
import logging

logging.basicConfig(level=logging.WARNING)

class BettingAnalyzerCLI:
    def __init__(self):
        self.handler = ClaudeQueryHandler()
        self.analyzer = PropAnalyzer()
        self.loader = NFLDataLoader(data_dir=str(project_root / "data"))
        self.parlay_builder = ParlayBuilder()
        self.tracker = PerformanceTracker(db_path=str(project_root / "bets.db"))
        self.calibrator = AgentCalibrator(db_path=str(project_root / "bets.db"))
        self.odds_integrator = OddsIntegrator(data_dir=str(project_root / "data"))
        self.week = 9
        self.last_parlays = []
        self.last_parlay_ids = []  # Store parlay IDs for reference
        self.bankroll = 1000
    
    def print_header(self):
        print("\n" + "="*70)
        print("🏈 NFL BETTING SYSTEM - COMPLETE ANALYSIS")
        print("="*70)
        print("\nCommands:")
        print("  pull-lines               - Refresh DraftKings betting lines")
        print("  analyze <query>          - Analyze prop (e.g., 'Love 250 pass yards')")
        print("  parlays [conf]           - Generate standard parlays (default: 58)")
        print("  parlays-teams <teams>    - Generate parlays for specific teams (e.g., 'parlays-teams GB,DET,KC')")
        print("  opt-parlays [quality]    - Generate optimized low-correlation parlays")
        print("  opt-parlays-teams <tms>  - Generate optimized parlays for specific teams")
        print("  top-props [count]        - Show top N props by confidence (default: 20)")
        print("  top-overs [count]        - Show top N OVER props only (default: 20)")
        print("  top-unders [count]       - Show top N UNDER props only (default: 20)")
        print("  top-team <team> [count]  - Show top N props for team (e.g., 'top-team SEA')")
        print("  export-props [count]     - Export props as JSON for Claude (default: 50)")
        print("  export-enhanced [count]  - Export props with clustering & contradictions (default: 50)")
        print("  chat                     - Launch natural language chat interface")
        print("  week <number>            - Change week (1-18)")
        print("\n  💰 BANKROLL & SIZING:")
        print("  bankroll <amount>        - Set betting bankroll (e.g., 'bankroll 5000')")
        print("  kelly [bankroll]         - Calculate Kelly sizing for last parlays")
        print("\n  🏥 INJURY DIAGNOSTICS:")
        print("  injury-diagnostic [player] - Show injury system status (or specific player)")
        print("\n  📊 TRACKING COMMANDS:")
        print("  log-parlay <index>       - Mark parlay N as one you're betting on")
        print("  log-result <id> <hits>   - Log results (e.g., 'log-result parlay_001 2/3')")
        print("  log-legs <id> <W/L>...   - Log per-leg results (e.g., 'log-legs parlay_001 W W L')")
        print("  score-week <week> [opts] - Auto-score parlays from CSV (e.g., 'score-week 10 --dry-run')")
        print("\n  📈 COMPREHENSIVE PROP TRACKING:")
        print("  analyze-week <wk> [opts] - Log ALL analyzed props for scoring (e.g., 'analyze-week 10 --top 100')")
        print("  score-props <week>       - Score all logged props from CSV (e.g., 'score-props 10')")
        print("  calibrate-props [week]   - Show detailed calibration for all props")
        print("\n  📊 CALIBRATION & REPORTS:")
        print("  auto-learn <week>             - Score props + calibrate agents (one command!)")
        print("  calibrate [week]              - Show calibration report (all weeks or specific)")
        print("  calibrate-agents [week] [opt] - Agent calibration (add --auto-apply to adjust weights)")
        print("  enable-auto-learning          - Enable automatic weight adjustments after each calibration")
        print("  disable-auto-learning         - Disable automatic weight adjustments")
        print("  show-weights                  - Display current agent weights")
        print("  recent [limit]                - Show recent logged parlays (default: 10)")
        print("  summary <week>                - Show week summary stats")
        print("\n  help                     - Show this message")
        print("  exit/quit                - Exit")
        print("="*70 + "\n")
    
    def print_command_syntax(self):
        """Print command syntax reminder"""
        print("\n" + "="*70)
        print("📋 COMMAND SYNTAX REFERENCE")
        print("="*70)
        print("  analyze <query>        | Example: analyze Mahomes 250 pass yards NYG")
        print("  top-props [count]      | Example: top-props 20 (default: 20)")
        print("  top-overs [count]      | Example: top-overs 20 (default: 20)")
        print("  top-unders [count]     | Example: top-unders 20 (default: 20)")
        print("  top-team <team> [cnt]  | Example: top-team SEA 15 (default count: 20)")
        print("  export-props [count]   | Example: export-props 50 (default: 50)")
        print("  export-enhanced [cnt]  | Example: export-enhanced 50 (default: 50)")
        print("  chat                   | Launch natural language query interface")
        print("  parlays [confidence]   | Example: parlays 65 (default: 65)")
        print("  parlays-teams <teams>  | Example: parlays-teams GB,DET,KC,DAL,CIN,BAL")
        print("  opt-parlays [quality]  | Example: opt-parlays 75 (default: 65)")
        print("  opt-parlays-teams <tm> | Example: opt-parlays-teams GB,DET,KC")
        print("  week <number>          | Example: week 10")
        print("  bankroll <amount>      | Example: bankroll 5000")
        print("  kelly [bankroll]       | Example: kelly 3000 (uses stored if not provided)")
        print("  log-parlay <index>     | Example: log-parlay 0 (mark parlay as bet)")
        print("  log-result <id> <hits> | Example: log-result parlay_001 3/3")
        print("  log-legs <id> <W/L>... | Example: log-legs parlay_001 W W L")
        print("  score-week <wk> [opts] | Example: score-week 10 --dry-run (or --force)")
        print("  calibrate [week]       | Example: calibrate 9 (or calibrate for all)")
        print("  calibrate-agents [w]   | Example: calibrate-agents 9 (or all weeks)")
        print("="*70 + "\n")
    
    def pull_lines(self):
        """Refresh DraftKings betting lines"""
        print(f"\n📡 Refreshing DraftKings betting lines for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        enriched_props, odds_source = integrate_odds_with_analysis(
            context.get('props', []),
            week=self.week,
            data_dir=str(project_root / "data")
        )
        print(f"✅ Loaded {len(enriched_props)} DraftKings lines ({odds_source})\n")
    
    def analyze_prop(self, query):
        """Analyze a betting prop"""
        if not query:
            print("❌ Please provide a query\n")
            return
        
        print(f"\n🔄 Analyzing: {query}")
        print("Optional - Enter weather (temp/wind/conditions) or press Enter to skip:")
        weather_input = input("Weather: ").strip()
        
        weather = None
        if weather_input:
            weather = {'conditions': weather_input}
        
        print()
        response = self.handler.query(query, week=self.week, weather=weather)
        print(response)
    
    def show_top_props(self, count_str="20"):
        """Show top props by confidence score - includes OVER and UNDER"""
        try:
            count = int(count_str)
        except ValueError:
            count = 20
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing props (OVER + UNDER)...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)
        
        # Deduplicate: keep only highest confidence for each player+stat_type+bet_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            bet_type = getattr(prop, 'bet_type', 'OVER')
            key = (prop.player_name.lower(), prop.stat_type, bet_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        over_count = sum(1 for p in top_props if getattr(p.prop, 'bet_type', 'OVER') == 'OVER')
        under_count = sum(1 for p in top_props if getattr(p.prop, 'bet_type', 'OVER') == 'UNDER')
        
        print(f"\n🔥 TOP {len(top_props)} PROPS BY CONFIDENCE - WEEK {self.week}")
        print(f"   ({over_count} OVER | {under_count} UNDER)")
        print("="*70)
        print("")
        
        for i, analysis in enumerate(top_props, 1):
            prop = analysis.prop
            conf = analysis.final_confidence
            
            if conf >= 80:
                emoji = "🔥"
            elif conf >= 75:
                emoji = "⭐"
            elif conf >= 70:
                emoji = "✅"
            elif conf >= 65:
                emoji = "📊"
            else:
                emoji = "📈"
            
            bet_type = getattr(prop, 'bet_type', 'OVER')
            print(f"{emoji} {i:2d}. {prop.player_name:20s} ({prop.team:3s}) vs {prop.opponent:3s}")
            print(f"     {prop.stat_type:15s} {bet_type} {prop.line:6.1f} | Confidence: {conf:5.1f}%")
            print()
        
        print("="*70)
        print(f"\n💡 Use any of these players to build your parlay!")
        print(f"   Example: analyze Mahomes 250 pass yards\n")
    
    def show_top_overs(self, count_str="20"):
        """Show top OVER props only by confidence score"""
        try:
            count = int(count_str)
        except ValueError:
            count = 20
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing OVER props...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)
        
        # Filter to OVER only
        over_analyses = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'OVER']
        
        # Deduplicate: keep only highest confidence for each player+stat_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(over_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            key = (prop.player_name.lower(), prop.stat_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        print(f"\n🔥 TOP {len(top_props)} OVER PROPS BY CONFIDENCE - WEEK {self.week}")
        print("="*70)
        print("")
        
        for i, analysis in enumerate(top_props, 1):
            prop = analysis.prop
            conf = analysis.final_confidence
            
            if conf >= 80:
                emoji = "🔥"
            elif conf >= 75:
                emoji = "⭐"
            elif conf >= 70:
                emoji = "✅"
            elif conf >= 65:
                emoji = "📊"
            else:
                emoji = "📈"
            
            print(f"{emoji} {i:2d}. {prop.player_name:20s} ({prop.team:3s}) vs {prop.opponent:3s}")
            print(f"     {prop.stat_type:15s} OVER {prop.line:6.1f} | Confidence: {conf:5.1f}%")
            print()
        
        print("="*70)
        print(f"\n💡 Use any of these players to build your parlay!")
        print(f"   Example: analyze Mahomes 250 pass yards\n")
    
    def show_top_unders(self, count_str="20"):
        """Show top UNDER props only by confidence score"""
        try:
            count = int(count_str)
        except ValueError:
            count = 20
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing UNDER props...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)
        
        # Filter to UNDER only
        under_analyses = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER']
        
        # Deduplicate: keep only highest confidence for each player+stat_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(under_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            key = (prop.player_name.lower(), prop.stat_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        print(f"\n🔥 TOP {len(top_props)} UNDER PROPS BY CONFIDENCE - WEEK {self.week}")
        print("="*70)
        print("")
        
        for i, analysis in enumerate(top_props, 1):
            prop = analysis.prop
            conf = analysis.final_confidence
            
            if conf >= 80:
                emoji = "🔥"
            elif conf >= 75:
                emoji = "⭐"
            elif conf >= 70:
                emoji = "✅"
            elif conf >= 65:
                emoji = "📊"
            else:
                emoji = "📈"
            
            print(f"{emoji} {i:2d}. {prop.player_name:20s} ({prop.team:3s}) vs {prop.opponent:3s}")
            print(f"     {prop.stat_type:15s} UNDER {prop.line:6.1f} | Confidence: {conf:5.1f}%")
            print()
        
        print("="*70)
        print(f"\n💡 Use any of these players to build your parlay!")
        print(f"   Example: analyze Mahomes 250 pass yards\n")
    
    def show_top_props_by_team(self, team_str=""):
        """Show top props by team and confidence score"""
        if not team_str:
            print("❌ Please provide a team abbreviation (e.g., 'top-team SEA' or 'top-team KC 15')\n")
            return
        
        # Parse arguments - could be "SEA" or "SEA 15"
        args = team_str.split()
        team_abbr = args[0].upper()
        
        try:
            count = int(args[1]) if len(args) > 1 else 20
        except (ValueError, IndexError):
            count = 20
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing props for {team_abbr}...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)
        
        # Filter to team only
        team_analyses = [a for a in all_analyses if a.prop.team.upper() == team_abbr]
        
        if not team_analyses:
            print(f"\n⚠️  No props found for {team_abbr}. Check the team abbreviation.\n")
            return
        
        # Deduplicate: keep only highest confidence for each player+stat_type+bet_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(team_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            bet_type = getattr(prop, 'bet_type', 'OVER')
            key = (prop.player_name.lower(), prop.stat_type, bet_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        over_count = sum(1 for p in top_props if getattr(p.prop, 'bet_type', 'OVER') == 'OVER')
        under_count = sum(1 for p in top_props if getattr(p.prop, 'bet_type', 'OVER') == 'UNDER')
        
        print(f"\n🔥 TOP {len(top_props)} PROPS FOR {team_abbr} BY CONFIDENCE - WEEK {self.week}")
        print(f"   ({over_count} OVER | {under_count} UNDER)")
        print("="*70)
        print("")
        
        for i, analysis in enumerate(top_props, 1):
            prop = analysis.prop
            conf = analysis.final_confidence
            
            if conf >= 80:
                emoji = "🔥"
            elif conf >= 75:
                emoji = "⭐"
            elif conf >= 70:
                emoji = "✅"
            elif conf >= 65:
                emoji = "📊"
            else:
                emoji = "📈"
            
            bet_type = getattr(prop, 'bet_type', 'OVER')
            print(f"{emoji} {i:2d}. {prop.player_name:20s} ({prop.team:3s}) vs {prop.opponent:3s}")
            print(f"     {prop.stat_type:15s} {bet_type} {prop.line:6.1f} | Confidence: {conf:5.1f}%")
            print()
        
        print("="*70)
        print(f"\n💡 Use any of these players to build your parlay!")
        print(f"   Example: analyze Metcalf 75 receiving yards\n")
    
    def export_props_command(self, count_str="50"):
        """Export top props as JSON for conversational Claude analysis"""
        try:
            count = int(count_str)
        except ValueError:
            count = 50
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing props...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)
        
        # Deduplicate: keep only highest confidence for each player+stat_type+bet_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            bet_type = getattr(prop, 'bet_type', 'OVER')
            key = (prop.player_name.lower(), prop.stat_type, bet_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        print(f"\n📤 Exporting {len(top_props)} props to JSON...")
        
        # Generate JSON export
        json_export, summary = PropsJSONExporter.export_props_with_summary(top_props)
        
        # Print summary
        print(summary)
        print("\n" + "="*70)
        print("📋 JSON EXPORT FOR CLAUDE")
        print("="*70)
        print(json_export)
        print("="*70)
        
        # Try to copy to clipboard
        try:
            import pyperclip
            pyperclip.copy(json_export)
            print("\n✅ JSON copied to clipboard!")
            print("   Paste into Claude with: Ctrl+V")
            print("   Then ask Claude questions like:")
            print("   - 'Create a 3-leg parlay from high passing yards props'")
            print("   - 'Which players correlate most?'")
            print("   - 'Show me all TD props with bellcow RBs'\n")
        except ImportError:
            print("\n💡 Tip: Install pyperclip for auto-clipboard:")
            print("   pip install pyperclip")
            print("\n   Or manually copy the JSON above and paste into Claude\n")
    
    def export_enhanced_command(self, count_str="50"):
        """Export props with correlation clustering and contradiction detection"""
        try:
            count = int(count_str)
        except ValueError:
            count = 50
        
        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)
        
        print(f"📊 Analyzing props...")
        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)
        
        # Deduplicate: keep only highest confidence for each player+stat_type+bet_type
        seen = {}
        deduped_analyses = []
        
        for analysis in sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True):
            prop = analysis.prop
            bet_type = getattr(prop, 'bet_type', 'OVER')
            key = (prop.player_name.lower(), prop.stat_type, bet_type)
            
            if key not in seen:
                seen[key] = True
                deduped_analyses.append(analysis)
                if len(deduped_analyses) >= count:
                    break
        
        top_props = deduped_analyses
        
        print(f"\n📤 Exporting {len(top_props)} props with enhanced analysis...")
        
        # Use EnhancedPropsExporter
        exporter = EnhancedPropsExporter()
        json_export = exporter.export_enhanced(top_props)
        
        # Print summary
        print(f"\n✅ Enhanced export complete!")
        print(f"   • Analyzed {len(top_props)} props")
        print(f"   • Correlation clusters detected")
        print(f"   • Contradictions identified")
        print(f"   • Agent analysis included")
        
        print("\n" + "="*70)
        print("📋 ENHANCED JSON EXPORT FOR CLAUDE")
        print("="*70)
        print(json_export)
        print("="*70)
        
        # Try to copy to clipboard
        try:
            import pyperclip
            pyperclip.copy(json_export)
            print("\n✅ JSON copied to clipboard!")
            print("   Paste into Claude and ask:")
            print("   - 'Which clusters create hidden correlation risk?'")
            print("   - 'Are there any contradictory high-confidence bets?'")
            print("   - 'Which agents disagree most on these props?'\n")
        except ImportError:
            print("\n💡 Tip: Install pyperclip for auto-clipboard:")
            print("   pip install pyperclip")
            print("\n   Or manually copy the JSON above and paste into Claude\n")
    
    def generate_parlays(self, min_conf_str="58", teams=None):
        """Generate standard parlay combinations WITH CORRELATION DETECTION (PROJECT 3)

        Args:
            min_conf_str: Minimum confidence threshold
            teams: Optional list of team abbreviations to filter to (e.g., ['GB', 'DET', 'KC'])
        """
        try:
            min_conf = int(min_conf_str)
        except ValueError:
            min_conf = 58

        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)

        props_list = context.get('props', [])
        betting_source = context.get('betting_lines_source', 'UNKNOWN')
        print(f"📊 Analyzing {len(props_list)} props (OVER + UNDER)...")

        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)

        # Filter by teams if specified
        if teams:
            all_analyses = [a for a in all_analyses if a.prop.team in teams]
            print(f"📌 Filtered to teams: {', '.join(teams)} ({len(all_analyses)} props)")
        
        print(f"✅ Analyzed {len(all_analyses)} props (OVER + UNDER)")
        
        # Build confidence distribution
        confidence_distribution = {'0-20': 0, '20-40': 0, '40-50': 0, '50-60': 0, '60-70': 0, '70-80': 0, '80+': 0}
        for analysis in all_analyses:
            conf = analysis.final_confidence
            if conf >= 80: confidence_distribution['80+'] += 1
            elif conf >= 70: confidence_distribution['70-80'] += 1
            elif conf >= 60: confidence_distribution['60-70'] += 1
            elif conf >= 50: confidence_distribution['50-60'] += 1
            elif conf >= 40: confidence_distribution['40-50'] += 1
            elif conf >= 20: confidence_distribution['20-40'] += 1
            else: confidence_distribution['0-20'] += 1
        
        print(f"📊 Confidence Distribution:")
        for range_label, count in confidence_distribution.items():
            pct = (count / len(all_analyses) * 100) if all_analyses else 0
            print(f"   {range_label}: {count} props ({pct:.1f}%)")
        
        # PROJECT 3: Use EnhancedParlayBuilder with correlation detection
        print(f"\n🔍 Analyzing correlations (PROJECT 3)...")
        enhanced_builder = EnhancedParlayBuilder()
        parlays = enhanced_builder.build_parlays_with_correlation(all_analyses, min_confidence=min_conf)
        output = self.parlay_builder.format_parlays_for_betting(parlays, betting_source=betting_source)
        print(output)
        
        self.last_parlays = parlays
        print(f"\n💡 Tip: Use 'log-parlay 0' to log the first parlay, 'log-parlay 1' for second, etc.")
        print(f"💰 Tip: Use 'kelly' to calculate optimal sizing\n")
        
        try:
            print("\n📊 Opening parlay display window...")
            show_parlays_gui(parlays, optimized=False, week=self.week)
        except Exception as e:
            print(f"⚠️ GUI not available: {e}")
            print("✓ Parlays displayed in terminal above\n")
    
    def generate_optimized_parlays(self, quality_str=None, teams=None):
        """Generate optimized low-correlation parlays with dependency analysis

        Args:
            quality_str: Minimum quality threshold
            teams: Optional list of team abbreviations to filter to (e.g., ['GB', 'DET', 'KC'])
        """
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ ERROR: ANTHROPIC_API_KEY not set in .env\n")
            return

        quality_threshold = None
        if quality_str:
            try:
                quality_threshold = int(quality_str)
            except ValueError:
                quality_threshold = 65

        print(f"\n🔄 Loading data for Week {self.week}...")
        context = self.loader.load_all_data(week=self.week)

        props_list = context.get('props', [])
        print(f"📊 Analyzing {len(props_list)} props (OVER + UNDER)...")

        all_analyses = self.analyzer.analyze_all_props(context, min_confidence=50)

        # Filter by teams if specified
        if teams:
            all_analyses = [a for a in all_analyses if a.prop.team in teams]
            print(f"📌 Filtered to teams: {', '.join(teams)} ({len(all_analyses)} props)")

        print(f"✅ Analyzed {len(all_analyses)} high-confidence props (OVER + UNDER)")

        print("\n" + "="*70)
        print("🔄 REBUILDING PARLAYS - LOW CORRELATION OPTIMIZATION")
        print("="*70)

        optimizer = ParlayOptimizer(api_key=api_key)
        optimized_parlays = optimizer.rebuild_parlays_low_correlation(
            all_analyses,
            target_parlays=10,
            min_confidence=50,
            max_player_exposure=0.30,
            teams=teams
        )
        
        print("\n🔍 Validating dependencies...\n")
        dep_analyzer = DependencyAnalyzer(api_key=api_key)
        
        best = []
        for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
            for parlay in optimized_parlays.get(ptype, []):
                analysis = dep_analyzer.analyze_parlay_dependencies(parlay)
                rec = analysis.get('recommendation')
                adj_conf = analysis.get('adjusted_confidence')
                
                if quality_threshold and adj_conf < quality_threshold:
                    continue
                
                if rec != "AVOID":
                    best.append({
                        'parlay': parlay,
                        'adjusted_confidence': adj_conf,
                        'recommendation': rec,
                        'adjustment': analysis.get('correlation_adjustment', {}).get('adjustment_value', 0)
                    })
        
        best.sort(key=lambda x: x['adjusted_confidence'], reverse=True)
        
        output = optimizer.format_best_parlays(best)
        print(output)
        
        if quality_threshold:
            print(f"\n📊 Quality filtered to {quality_threshold}%+ confidence")
        
        # Calculate exposure-adjusted position sizing
        print("\n" + "="*70)
        print("💰 CALCULATING EXPOSURE-ADJUSTED POSITION SIZING")
        print("="*70)
        position_optimizer = PositionSizeOptimizer(bankroll=self.bankroll, base_kelly_fraction=0.5)
        sized_parlays = position_optimizer.calculate_exposure_adjusted_sizing(
            best, 
            total_allocation=0.10
        )
        sizing_report = position_optimizer.format_sizing_report(sized_parlays)
        print(sizing_report)
        
        # AUTO-LOG: Automatically log all generated parlays and store IDs
        print("\n" + "="*70)
        print("📝 AUTO-LOGGING PARLAYS")
        print("="*70 + "\n")
        
        parlay_ids = []
        for i, parlay_item in enumerate(sized_parlays):
            confidence = parlay_item.get('adjusted_confidence', parlay_item.get('confidence', 70))
            
            if isinstance(parlay_item, dict) and 'parlay' in parlay_item:
                parlay_obj = parlay_item['parlay']
            else:
                parlay_obj = parlay_item
            
            parlay_data = {
                'confidence': confidence,
                'odds': -110,
                'agent_scores': {},
                'legs': []
            }
            
            if hasattr(parlay_obj, 'legs'):
                for leg in parlay_obj.legs:
                    if hasattr(leg, 'prop'):
                        prop = leg.prop
                        parlay_data['legs'].append({
                            'player': prop.player_name,
                            'team': prop.team,
                            'prop_type': prop.stat_type,
                            'bet_type': getattr(prop, 'bet_type', 'OVER'),
                            'line': prop.line,
                            'agent_scores': {}
                        })
            
            if parlay_data['legs']:
                parlay_id = self.tracker.log_parlay(parlay_data, self.week, "generated")
                if parlay_id:
                    parlay_ids.append(parlay_id)
                    print(f"✅ Parlay {i+1} logged! ID: {parlay_id}")
            else:
                parlay_ids.append(None)
        
        self.last_parlays = sized_parlays
        self.last_parlay_ids = parlay_ids
        
        print(f"\n" + "="*70)
        print("💾 PARLAY REFERENCE IDs (copy these to track results)")
        print("="*70)
        for i, pid in enumerate(parlay_ids):
            if pid:
                print(f"Parlay {i+1}: {pid}")
        print("="*70)
        
        print(f"\n💡 Tip: Copy the IDs above to track results later")
        print(f"💡 Tip: Use 'log-result <ID> X/Y' to record if you bet on it\n")
        
        try:
            print("\n📊 Opening optimized parlay display window...")
            gui_parlays = {}
            for item in best:
                parlay = item['parlay']
                ptype = f"{len(parlay.legs)}-leg"
                if ptype not in gui_parlays:
                    gui_parlays[ptype] = []
                gui_parlays[ptype].append(parlay)
            show_parlays_gui(gui_parlays, optimized=True, week=self.week)
        except Exception as e:
            print(f"⚠️ GUI not available: {e}")
            print("✓ Parlays displayed in terminal above\n")
    
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
    
    def log_parlay_command(self, index_str):
        """Mark a parlay as one you're betting on"""
        try:
            index = int(index_str)
            if index < 0 or index >= len(self.last_parlay_ids):
                print(f"❌ Parlay index {index} not found. Generated {len(self.last_parlay_ids)} parlays.\n")
                return
            
            parlay_id = self.last_parlay_ids[index]
            if not parlay_id:
                print(f"❌ Parlay {index+1} has no ID.\n")
                return
            
            print(f"\n✅ Parlay {index+1} marked as bet")
            print(f"   ID: {parlay_id}")
            print(f"   After games complete, log results with:")
            print(f"   log-result {parlay_id} X/Y (e.g., 2/3 if 2 legs hit)\n")
        
        except Exception as e:
            import traceback
            print(f"❌ Error: {e}\n")
            traceback.print_exc()
    
    def log_results_command(self, arg_str):
        """Log results for a parlay"""
        try:
            parts = arg_str.split()
            if len(parts) < 2:
                print("❌ Usage: log-result <parlay_id> <hits>/<total>\n")
                print("   Example: log-result parlay_1730000000 3/3\n")
                return
            
            parlay_id = parts[0]
            hits_str = parts[1]
            
            if '/' not in hits_str:
                print("❌ Format results as 'hits/total' (e.g., 2/3)\n")
                return
            
            hits, total = map(int, hits_str.split('/'))
            
            leg_results = {}
            for i in range(total):
                leg_results[f'leg_{i}'] = i < hits
            
            self.tracker.log_results(parlay_id, leg_results)
            print(f"✅ Results logged!\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def log_legs_command(self, arg_str):
        """Log per-leg results (W/L for each leg)"""
        try:
            parts = arg_str.split()
            if len(parts) < 2:
                print("❌ Usage: log-legs <parlay_id> <W/L> <W/L> ...\n")
                print("   Example: log-legs parlay_001 W W L\n")
                return
            
            parlay_id = parts[0]
            leg_outcomes = parts[1:]
            
            # Validate all outcomes are W or L
            for outcome in leg_outcomes:
                if outcome.upper() not in ['W', 'L']:
                    print(f"❌ Invalid outcome '{outcome}'. Use only W or L\n")
                    return
            
            # Build leg results dict
            leg_results = {}
            for i, outcome in enumerate(leg_outcomes):
                leg_results[f'leg_{i}'] = (outcome.upper() == 'W')
            
            self.tracker.log_results(parlay_id, leg_results)
            
            # Summary output
            wins = sum(1 for v in leg_results.values() if v)
            total = len(leg_results)
            print(f"✅ Per-leg results logged!")
            print(f"   Parlay ID: {parlay_id}")
            print(f"   Result: {wins}/{total} legs hit")
            print(f"   Details: {' '.join([f'Leg {i+1}={o.upper()}' for i, o in enumerate(leg_outcomes)])}\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def calibrate_command(self, week_str=""):
        """Show calibration report"""
        try:
            week = None
            if week_str:
                week = int(week_str)
            
            self.tracker.calibration_report(week=week)
        except ValueError:
            print("❌ Invalid week number\n")
    
    def calibrate_agents_command(self, arg_str=""):
        """Show agent accuracy & apply weight adjustments (optionally)"""
        try:
            args = arg_str.split()
            week = None
            auto_apply = '--auto-apply' in args or '--auto' in args

            # Extract week number if present
            for arg in args:
                if arg.isdigit():
                    week = int(arg)
                    break

            # Import and run calibration
            from scripts.analysis.agent_calibrator import calibrate_agents_interactive
            calibrate_agents_interactive(db_path=str(self.db_path), week=week, auto_apply=auto_apply)

        except Exception as e:
            print(f"❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
    
    def recent_command(self, limit_str="10"):
        """Show recent parlays"""
        try:
            limit = int(limit_str)
            self.tracker.list_recent_parlays(limit=limit)
        except ValueError:
            print("❌ Invalid limit\n")
    
    def summary_command(self, week_str):
        """Show week summary"""
        try:
            week = int(week_str)
            self.tracker.week_summary(week=week)
        except ValueError:
            print("❌ Invalid week number\n")

    def enable_auto_learning_command(self):
        """Enable automatic weight adjustments"""
        try:
            from scripts.analysis.agent_weight_manager import AgentWeightManager
            manager = AgentWeightManager(str(self.db_path))
            manager.enable_auto_learning()
            print("\n✅ Auto-learning ENABLED")
            print("   Agent weights will be automatically adjusted after each calibration.\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

    def disable_auto_learning_command(self):
        """Disable automatic weight adjustments"""
        try:
            from scripts.analysis.agent_weight_manager import AgentWeightManager
            manager = AgentWeightManager(str(self.db_path))
            manager.disable_auto_learning()
            print("\n⏸️  Auto-learning DISABLED")
            print("   Agent weights will NOT be automatically adjusted.")
            print("   Use 'calibrate-agents --auto-apply' to manually apply adjustments.\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

    def show_weights_command(self):
        """Display current agent weights"""
        try:
            from scripts.analysis.agent_weight_manager import AgentWeightManager
            manager = AgentWeightManager(str(self.db_path))
            manager.print_current_weights()
        except Exception as e:
            print(f"❌ Error: {e}\n")

    def auto_learn_command(self, week_str):
        """Auto-learn: Score props + calibrate agents in one command"""
        try:
            if not week_str:
                print("❌ Usage: auto-learn <week>\n")
                print("   Example: auto-learn 12\n")
                return

            week = int(week_str)

            print("\n" + "="*70)
            print(f"🤖 AUTO-LEARN WEEK {week}")
            print("="*70 + "\n")

            # Step 1: Score props
            print("📊 Step 1/2: Scoring props from CSV files...\n")
            self.score_props_command(str(week))

            print("\n" + "-"*70 + "\n")

            # Step 2: Calibrate agents with auto-apply
            print("🎯 Step 2/2: Calibrating agents and adjusting weights...\n")
            self.calibrate_agents_command(f"{week} --auto-apply")

            print("\n" + "="*70)
            print(f"✅ AUTO-LEARN COMPLETE FOR WEEK {week}")
            print("="*70 + "\n")
            print("💡 Next steps:")
            print(f"   - Weights have been automatically adjusted")
            print(f"   - Run 'show-weights' to see updated values")
            print(f"   - Run 'analyze-week {week+1} --top 100' to analyze next week\n")

        except ValueError:
            print("❌ Invalid week number\n")
        except Exception as e:
            print(f"❌ Error in auto-learn: {e}\n")
            import traceback
            traceback.print_exc()

    def score_week_command(self, arg_str):
        """Auto-score parlays from CSV files"""
        try:
            # Parse arguments
            args = arg_str.split()

            if not args:
                print("❌ Usage: score-week <week> [--dry-run] [--force]\n")
                print("   Examples:")
                print("     score-week 10 --dry-run    (preview scoring)")
                print("     score-week 10              (execute scoring)")
                print("     score-week 10 --force      (re-score already scored parlays)\n")
                return

            week = int(args[0])
            dry_run = '--dry-run' in args
            force = '--force' in args

            # Call auto_scorer module
            output = auto_scorer.score_week(
                week=week,
                db_path=project_root / "bets.db",
                data_dir=project_root / "data",
                dry_run=dry_run,
                force=force
            )

            print(output)

        except ValueError:
            print("❌ Invalid week number\n")
        except Exception as e:
            print(f"❌ Error scoring week: {e}\n")
            import traceback
            traceback.print_exc()

    def analyze_week_command(self, arg_str):
        """Analyze and log all props for comprehensive scoring"""
        try:
            args = arg_str.split()

            if not args:
                print("[ERROR] Usage: analyze-week <week> [--top N] [--all]\n")
                print("   Examples:")
                print("     analyze-week 10 --top 100    (log top 100 props)")
                print("     analyze-week 10 --top 200    (log top 200 props)")
                print("     analyze-week 10 --all        (log all analyzed props)\n")
                return

            week = int(args[0])
            top_n = None

            if '--all' in args:
                top_n = None
            elif '--top' in args:
                try:
                    top_idx = args.index('--top')
                    top_n = int(args[top_idx + 1])
                except (ValueError, IndexError):
                    print("[ERROR] Invalid --top value. Using default (top 100)\n")
                    top_n = 100
            else:
                top_n = 100  # Default

            print(f"\n[LOADING] Loading data for Week {week}...")
            context = self.loader.load_all_data(week=week)

            print(f"[ANALYZING] Analyzing props...")
            all_analyses = self.analyzer.analyze_all_props(context, min_confidence=60)

            print(f"[OK] Analyzed {len(all_analyses)} props\n")

            # Log to database
            logged, skipped = prop_logger.log_analyzed_props(
                all_analyses,
                week=week,
                db_path=project_root / "bets.db",
                top_n=top_n
            )

            print(f"[OK] Logged {logged} props to database")
            if skipped > 0:
                print(f"     (Skipped {skipped} duplicates)")

            print(f"\n[OK] Week {week} props logged!")
            print(f"     Next step: Run 'score-props {week}' to score them\n")

        except ValueError:
            print("[ERROR] Invalid week number\n")
        except Exception as e:
            print(f"[ERROR] Error analyzing week: {e}\n")
            import traceback
            traceback.print_exc()

    def score_props_command(self, arg_str):
        """Score all logged props from CSV files"""
        try:
            args = arg_str.split()

            if not args:
                print("[ERROR] Usage: score-props <week> [--dry-run]\n")
                print("   Examples:")
                print("     score-props 10 --dry-run    (preview scoring)")
                print("     score-props 10              (execute scoring)\n")
                return

            week = int(args[0])
            dry_run = '--dry-run' in args

            output = props_scorer.score_props_for_week(
                week=week,
                db_path=project_root / "bets.db",
                data_dir=project_root / "data",
                dry_run=dry_run
            )

            print(output)

        except ValueError:
            print("[ERROR] Invalid week number\n")
        except Exception as e:
            print(f"[ERROR] Error scoring props: {e}\n")
            import traceback
            traceback.print_exc()

    def calibrate_props_command(self, week_str=""):
        """Show comprehensive prop calibration report"""
        try:
            week = int(week_str) if week_str else None

            summary = prop_logger.get_props_summary(week, db_path=project_root / "bets.db")

            print("\n" + "="*70)
            if week:
                print(f"PROPS CALIBRATION SUMMARY - WEEK {week}")
            else:
                print("PROPS CALIBRATION SUMMARY - ALL WEEKS")
            print("="*70)

            print(f"\nTotal Props Analyzed: {summary['total']}")
            print(f"Props Scored: {summary['scored']}")
            print(f"Props Pending: {summary['pending']}")
            print(f"Hit Rate: {summary['hit_rate']:.1f}%")

            print("\n" + "="*70)
            print("\n💡 For detailed breakdown, props were scored with 'score-props' command")
            week_str = week if week else "<week>"
            print(f"   Run 'score-props {week_str}' to see full analysis\n")

        except ValueError:
            print("❌ Invalid week number\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

    def injury_diagnostic_command(self, player_name=""):
        """Show injury system diagnostic"""
        print("\n" + "="*80)
        print("INJURY AGENT DIAGNOSTIC - COMPLETE SYSTEM CHECK")
        print("="*80 + "\n")
        
        # STEP 1: Check Injury Data Loading
        print("STEP 1: Injury Data Loading")
        print("-" * 80)
        
        context = self.loader.load_all_data(week=self.week)
        injury_text = context.get('injuries')
        
        if not injury_text:
            print("❌ CRITICAL: No injury data loaded!")
            print("   File might not exist: wk" + str(self.week) + "-injury-report.csv\n")
            return
        
        lines = injury_text.split('\n')
        print(f"✅ Injury data loaded: {len(lines)} lines")
        
        # Look for specific player or just show summary
        if player_name:
            player_in_injuries = any(player_name.lower() in line.lower() for line in lines)
            if player_in_injuries:
                print(f"✅ {player_name} found in injury data")
                for line in lines:
                    if player_name.lower() in line.lower():
                        print(f"   → {line}")
            else:
                print(f"⚠️  {player_name} NOT found in injury data")
        else:
            # Show injury data summary
            statuses = {}
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 5:
                        status = parts[4].strip().lower()
                        statuses[status] = statuses.get(status, 0) + 1
            
            print("Injury Status Breakdown:")
            for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
                print(f"   {status:15} : {count:3d} players")
        
        print()
        
        # STEP 2: Test Injury Agent
        print("STEP 2: Injury Agent Configuration")
        print("-" * 80)
        
        injury_agent = self.analyzer.agents.get('Injury')
        if injury_agent:
            print(f"✅ Injury Agent found with weight: {injury_agent.weight}")
            if injury_agent.weight >= 3.0:
                print(f"✅ Weight is high ({injury_agent.weight}) - injuries take priority")
            else:
                print(f"⚠️  Weight is low ({injury_agent.weight}) - may not override other signals")
        else:
            print("❌ CRITICAL: Injury agent not in orchestrator!")
        
        print()
        
        # STEP 3: Analyze specific player if provided
        if player_name:
            print(f"STEP 3: {player_name} Analysis")
            print("-" * 80)
            
            player_props = [p for p in context.get('props', []) if player_name.lower() in p.get('player_name', '').lower()]
            
            if not player_props:
                print(f"❌ No props found for {player_name} this week")
            else:
                print(f"Found {len(player_props)} prop(s) for {player_name}\n")
                
                for i, prop_data in enumerate(player_props):
                    print(f"Analyzing: {prop_data.get('stat_type')} O{prop_data.get('line')}")
                    print("-" * 80)
                    
                    analysis = self.analyzer.analyze_prop(prop_data, context)
                    
                    print(f"Final Confidence: {analysis.final_confidence}%")
                    print(f"Recommendation: {analysis.recommendation}\n")
                    
                    # Check Injury Agent specifically
                    injury_result = analysis.agent_breakdown.get('Injury', {})
                    injury_score = injury_result.get('raw_score', 'N/A')
                    injury_weight = injury_result.get('weight', 'N/A')
                    injury_rationale = injury_result.get('rationale', [])
                    
                    print("Injury Agent Breakdown:")
                    print(f"  Score: {injury_score}")
                    print(f"  Weight: {injury_weight}")
                    print(f"  Rationale: {injury_rationale if injury_rationale else 'None'}")
                    
                    if injury_score < 50 and injury_rationale:
                        print("  ✅ Injury penalty IS being applied!")
                    elif injury_score == 50:
                        print("  ⚠️  No injury penalty (player not in injury report or healthy)")
                    
                    print("\nAll Agent Scores:")
                    print("-" * 80)
                    
                    total_contribution = 0
                    for agent_name, result in analysis.agent_breakdown.items():
                        score = result.get('raw_score', 50)
                        weight = result.get('weight', 0)
                        contribution = (score - 50) * weight
                        total_contribution += contribution
                        
                        status = "↑" if contribution > 0 else ("↓" if contribution < 0 else "→")
                        print(f"  {status} {agent_name:15} Score: {score:3.0f} × Weight: {weight:4.2f} = {contribution:+6.2f}")
                    
                    print("-" * 80)
                    print(f"  Total Contribution: {total_contribution:+.2f} (final conf: {analysis.final_confidence}%)")
                    print()
        
        print()
        print("="*80)
        print()

    def kelly_sizing_command(self, arg_str=""):
        """Calculate optimal Kelly sizing"""
        if not self.last_parlays:
            print("❌ No parlays generated yet. Run 'parlays' or 'opt-parlays' first.\n")
            return
        
        if arg_str:
            try:
                self.bankroll = float(arg_str)
            except ValueError:
                print(f"❌ Invalid bankroll amount. Using default: ${self.bankroll}\n")
        
        kelly_parlays = []
        for i, parlay in enumerate(self.last_parlays):
            if isinstance(parlay, dict):
                confidence = parlay.get('adjusted_confidence', parlay.get('confidence', 70))
            else:
                confidence = 70
            
            kelly_parlays.append({
                'name': f"Parlay {i+1}",
                'confidence': confidence,
                'odds': -110,
                'legs': []
            })
        
        print("\n🎲 Calculating optimal Kelly allocation...")
        print(f"   Bankroll: ${self.bankroll:,.2f}")
        print(f"   Parlays: {len(kelly_parlays)}\n")
        
        optimizer = KellyOptimizer(bankroll=self.bankroll, kelly_fraction=0.5)
        result = optimizer.compare_strategies(kelly_parlays)
        
        output = format_kelly_report(result)
        print(output)
    
    def set_bankroll_command(self, amount_str):
        """Set betting bankroll"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("❌ Bankroll must be positive\n")
                return
            self.bankroll = amount
            print(f"✅ Bankroll set to ${amount:,.2f}\n")
        except ValueError:
            print("❌ Invalid amount\n")

    def launch_chat_interface(self):
        """Launch natural language chat interface"""
        print("\n🚀 Launching Natural Language Chat Interface...")
        print("   Type 'exit' in chat to return to main CLI\n")
        try:
            data_dir = str(project_root / "data")
            run_chat_interface(data_dir=data_dir)
            print("\n✅ Chat interface closed. Back to main CLI\n")
        except KeyboardInterrupt:
            print("\n✅ Chat interface closed. Back to main CLI\n")
        except Exception as e:
            print(f"\n❌ Error launching chat: {e}\n")
            print("   Make sure ANTHROPIC_API_KEY is set in .env\n")
    
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
                
                if command == 'pull-lines':
                    self.pull_lines()
                elif command == 'analyze':
                    self.analyze_prop(arg)
                elif command == 'top-props':
                    self.show_top_props(arg)
                elif command == 'top-overs':
                    self.show_top_overs(arg)
                elif command == 'top-unders':
                    self.show_top_unders(arg)
                elif command == 'top-team':
                    self.show_top_props_by_team(arg)
                elif command == 'export-props':
                    self.export_props_command(arg)
                elif command == 'export-enhanced':
                    self.export_enhanced_command(arg)
                elif command == 'chat':
                    self.launch_chat_interface()
                elif command == 'parlays':
                    self.generate_parlays(arg)
                elif command == 'parlays-teams':
                    # Parse teams from comma-separated list
                    if not arg:
                        print("❌ Please specify teams: parlays-teams GB,DET,KC")
                        continue
                    teams = [t.strip().upper() for t in arg.split(',')]
                    self.generate_parlays("58", teams=teams)
                elif command == 'opt-parlays':
                    self.generate_optimized_parlays(arg)
                elif command == 'opt-parlays-teams':
                    # Parse teams from comma-separated list
                    if not arg:
                        print("❌ Please specify teams: opt-parlays-teams GB,DET,KC")
                        continue
                    teams = [t.strip().upper() for t in arg.split(',')]
                    self.generate_optimized_parlays(quality_str=None, teams=teams)
                elif command == 'week':
                    self.change_week(arg)
                elif command == 'bankroll':
                    self.set_bankroll_command(arg)
                elif command == 'kelly':
                    self.kelly_sizing_command(arg)
                elif command == 'log-parlay':
                    self.log_parlay_command(arg)
                elif command == 'log-result':
                    self.log_results_command(arg)
                elif command == 'log-legs':
                    self.log_legs_command(arg)
                elif command == 'score-week':
                    self.score_week_command(arg)
                elif command == 'analyze-week':
                    self.analyze_week_command(arg)
                elif command == 'score-props':
                    self.score_props_command(arg)
                elif command == 'auto-learn':
                    self.auto_learn_command(arg)
                elif command == 'calibrate':
                    self.calibrate_command(arg)
                elif command == 'calibrate-agents':
                    self.calibrate_agents_command(arg)
                elif command == 'calibrate-props':
                    self.calibrate_props_command(arg)
                elif command == 'enable-auto-learning':
                    self.enable_auto_learning_command()
                elif command == 'disable-auto-learning':
                    self.disable_auto_learning_command()
                elif command == 'show-weights':
                    self.show_weights_command()
                elif command == 'recent':
                    self.recent_command(arg)
                elif command == 'summary':
                    self.summary_command(arg)
                elif command == 'injury-diagnostic':
                    self.injury_diagnostic_command(arg)
                elif command == 'help':
                    self.print_header()
                elif command in ['exit', 'quit']:
                    print("👋 Goodbye!\n")
                    break
                else:
                    print("❌ Unknown command. Type 'help' for options\n")
                
                if command not in ['help', 'exit', 'quit']:
                    self.print_command_syntax()
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    cli = BettingAnalyzerCLI()
    cli.run()
