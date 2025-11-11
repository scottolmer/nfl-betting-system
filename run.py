#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NFL Betting System - Simple Command Runner
Usage: python run <command> [options]

Commands:
  monitor                  Run single line movement check
  monitor-continuous       Run continuous monitoring (hourly)
  monitor-live             Run continuous monitoring (15 min interval for live games)
  bot                      Start Slack bot
  analyze [week]           Analyze props for specific week
  build-parlays [week]     Build optimal parlays
  build-parlays-optimized  Build low-correlation parlays with dependency analysis
  help                     Show this help message

Examples:
  python run monitor                                # Single check
  python run monitor-continuous                     # Hourly monitoring
  python run monitor-live                           # Live game monitoring (15 min)
  python run bot                                    # Start Slack bot
  python run analyze week 8                         # Analyze week 8
  python run build-parlays week 8                   # Build parlays for week 8
  python run build-parlays-optimized 9              # Build optimized parlays for week 9
  python run build-parlays-optimized 9 --quality 65 # Show only 65%+ confidence parlays
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Fix UTF-8 encoding on Windows for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / '.env')


def print_banner():
    """Print app banner"""
    print("")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║          🏈 NFL BETTING SYSTEM COMMAND RUNNER 🏈          ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("")


def print_help():
    """Print help message"""
    print_banner()
    print(__doc__)


def run_monitor(interval=60):
    """Run line monitor"""
    from scripts.line_monitoring.monitor_main_enhanced import EnhancedLineMonitorCLI
    
    monitor = EnhancedLineMonitorCLI()
    monitor.run_continuously_enhanced(interval_minutes=interval)


def run_single_check():
    """Run single monitor check"""
    from scripts.line_monitoring.monitor_main_enhanced import EnhancedLineMonitorCLI
    
    monitor = EnhancedLineMonitorCLI()
    monitor.run_check_enhanced()


def run_slack_bot():
    """Run Slack bot"""
    from scripts.slack_bot.app_enhanced import app
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting NFL Betting Slack Bot...")
    
    try:
        handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
        handler.start()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)


def run_analysis(week=None):
    """Run prop analysis"""
    if week is None:
        week = int(os.environ.get('NFL_WEEK', 8))
    
    from scripts.analysis.orchestrator import PropAnalyzer
    from scripts.analysis.data_loader import NFLDataLoader
    
    print_banner()
    print(f"📊 Analyzing props for Week {week}...")
    print("")
    
    data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
    prop_analyzer = PropAnalyzer()
    
    # Load and analyze
    context = data_loader.load_all_data(week=week)
    all_analyses = prop_analyzer.analyze_all_props(context, min_confidence=60)
    
    # Get top props
    top_props = sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True)[:10]
    
    print(f"🎯 TOP 10 PROPS - WEEK {week}")
    print("=" * 60)
    print("")
    
    for i, analysis in enumerate(top_props, 1):
        prop = analysis.prop
        conf = analysis.final_confidence
        
        # Confidence emoji
        if conf >= 75:
            emoji = "🔥"
        elif conf >= 70:
            emoji = "⭐"
        elif conf >= 65:
            emoji = "✅"
        else:
            emoji = "📊"
        
        print(f"{emoji} {i}. {prop.player_name} ({prop.team})")
        print(f"   {prop.stat_type} OVER {prop.line}")
        print(f"   Confidence: {conf:.0f}% | vs {prop.opponent}")
        
        if analysis.rationale:
            for reason in analysis.rationale[:2]:
                print(f"   • {reason}")
        print("")
    
    print("=" * 60)
    print(f"📊 Total props analyzed: {len(all_analyses)}")
    print("")


def run_parlay_builder(week=None):
    """Build optimal parlays"""
    import json
    
    if week is None:
        week = int(os.environ.get('NFL_WEEK', 8))
    
    from scripts.analysis.orchestrator import PropAnalyzer
    from scripts.analysis.data_loader import NFLDataLoader
    from scripts.analysis.parlay_builder import ParlayBuilder
    
    print_banner()
    print(f"🎰 Building parlays for Week {week}...")
    print("")
    
    data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
    prop_analyzer = PropAnalyzer()
    parlay_builder = ParlayBuilder()
    
    # Load and analyze
    context = data_loader.load_all_data(week=week)
    all_analyses = prop_analyzer.analyze_all_props(context, min_confidence=60)
    
    # Diversify
    def diversify_props(analyses):
        """Diversify props across games"""
        games = {}
        for analysis in analyses:
            game = f"{analysis.prop.team} vs {analysis.prop.opponent}"
            if game not in games:
                games[game] = []
            games[game].append(analysis)
        
        for game in games:
            games[game].sort(key=lambda x: x.final_confidence, reverse=True)
        
        diversified = []
        max_rounds = max(len(props) for props in games.values()) if games else 0
        
        for round_num in range(max_rounds):
            for game, props in sorted(games.items(), key=lambda x: len(x[1]), reverse=True):
                if round_num < len(props):
                    diversified.append(props[round_num])
        
        return diversified
    
    diversified = diversify_props(all_analyses)
    
    # Build parlays
    parlays = parlay_builder.build_parlays(diversified, min_confidence=65)
    
    print(f"🎰 WEEK {week} PARLAYS")
    print("=" * 60)
    print("")
    
    total_parlays = 0
    total_units = 0
    
    for parlay_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
        parlay_list = parlays.get(parlay_type, [])
        
        if parlay_list:
            print(f"*{parlay_type.upper()} PARLAYS:* ({len(parlay_list)})")
            
            for i, parlay in enumerate(parlay_list, 1):
                print(f"\n  Parlay {i} - {parlay.risk_level} RISK")
                print(f"  💰 Bet: {parlay.recommended_units} units")
                
                for j, leg in enumerate(parlay.legs, 1):
                    if isinstance(leg, dict):
                        player = leg.get('player', '?')
                        stat = leg.get('stat', '?')
                        pick = leg.get('pick', '?')
                        line = leg.get('line', '?')
                    else:
                        try:
                            prop = leg.prop if hasattr(leg, 'prop') else leg
                            player = prop.player_name if hasattr(prop, 'player_name') else str(leg)
                            stat = prop.stat_type if hasattr(prop, 'stat_type') else '?'
                            pick = 'OVER'
                            line = prop.line if hasattr(prop, 'line') else '?'
                        except:
                            player = str(leg)
                            stat = '?'
                            pick = '?'
                            line = '?'
                    
                    print(f"     {j}. {player} - {stat} {pick} {line}")
                
                total_units += parlay.recommended_units
            
            print("")
            total_parlays += len(parlay_list)
    
    print("=" * 60)
    print(f"📊 Total parlays built: {total_parlays}")
    print(f"💸 Total Investment: {total_units:.1f} units (${total_units * 10:.0f} @ $10/unit)")
    
    # Save regular parlays to timestamped folder
    print("\n[DEBUG] Starting save sequence...")
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "parlay_runs" / f"wk{week}_regular" / run_timestamp
    print(f"[DEBUG] Output dir: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Directory created")
    
    # Prepare data for JSON serialization
    regular_data = {
        'timestamp': run_timestamp,
        'week': week,
        'total_props_analyzed': len(all_analyses),
        'parlays': []
    }
    
    for parlay_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
        for parlay in parlays.get(parlay_type, []):
            parlay_data = {
                'type': parlay_type,
                'recommended_units': parlay.recommended_units,
                'risk_level': parlay.risk_level,
                'legs': []
            }
            
            for leg in parlay.legs:
                if hasattr(leg, 'prop'):
                    leg_data = {
                        'player_name': leg.prop.player_name,
                        'team': leg.prop.team,
                        'opponent': leg.prop.opponent,
                        'stat_type': leg.prop.stat_type,
                        'line': leg.prop.line,
                        'position': leg.prop.position,
                        'confidence': leg.final_confidence
                    }
                    parlay_data['legs'].append(leg_data)
            
            regular_data['parlays'].append(parlay_data)
    
    # Save regular parlays JSON
    with open(output_dir / "regular_parlays.json", "w") as f:
        json.dump(regular_data, f, indent=2)
    
    # Save summary
    summary = {
        'timestamp': run_timestamp,
        'week': week,
        'type': 'regular',
        'props_analyzed': len(all_analyses),
        'parlays_generated': total_parlays,
        'total_units': total_units,
        'file': 'regular_parlays.json'
    }
    
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Regular parlays saved to: parlay_runs\\wk{week}_regular\\{run_timestamp}\\")
    print("")


def run_parlay_builder_optimized(week=None, quality_threshold=None):
    """Build low-correlation parlays with dependency analysis
    
    Args:
        week: NFL week number
        quality_threshold: Minimum adjusted confidence (0-100), None shows all
    """
    import json
    
    if week is None:
        week = int(os.environ.get('NFL_WEEK', 8))
    
    from scripts.analysis.orchestrator import PropAnalyzer
    from scripts.analysis.data_loader import NFLDataLoader
    from scripts.analysis.parlay_optimizer import ParlayOptimizer
    from scripts.analysis.dependency_analyzer import DependencyAnalyzer
    
    print_banner()
    print(f"🔄 Building optimized parlays for Week {week}...")
    if quality_threshold:
        print(f"📊 Quality filter: {quality_threshold}%+")
    print()
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)
    
    data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
    prop_analyzer = PropAnalyzer()
    
    # Load and analyze
    context = data_loader.load_all_data(week=week)
    all_analyses = prop_analyzer.analyze_all_props(context, min_confidence=60)
    print(f"📊 {len(all_analyses)} props analyzed")
    print()
    
    # Optimize parlays - this already includes dependency analysis
    optimizer = ParlayOptimizer(api_key=api_key)
    optimized_parlays = optimizer.rebuild_parlays_low_correlation(
        all_analyses,
        target_parlays=10,
        min_confidence=65
    )
    
    # Single dependency pass - analyze each parlay once
    print("\n🔍 Validating dependencies...\n")
    dep_analyzer = DependencyAnalyzer(api_key=api_key)
    
    best = []
    for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
        for parlay in optimized_parlays.get(ptype, []):
            analysis = dep_analyzer.analyze_parlay_dependencies(parlay)
            rec = analysis.get('recommendation')
            adj_conf = analysis.get('adjusted_confidence')
            
            # Skip if below quality threshold
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
    
    # Format and print
    output = optimizer.format_best_parlays(best)
    print(output)
    
    # Save optimized parlays to timestamped folder
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "parlay_runs" / f"wk{week}_optimized" / run_timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare data for JSON serialization
    optimized_data = {
        'timestamp': run_timestamp,
        'week': week,
        'quality_threshold': quality_threshold,
        'total_props_analyzed': len(all_analyses),
        'parlays': []
    }
    
    for item in best:
        parlay = item['parlay']
        parlay_data = {
            'type': parlay.parlay_type,
            'adjusted_confidence': item['adjusted_confidence'],
            'recommendation': item['recommendation'],
            'adjustment': item['adjustment'],
            'recommended_units': parlay.recommended_units,
            'risk_level': parlay.risk_level,
            'legs': []
        }
        
        for leg in parlay.legs:
            leg_data = {
                'player_name': leg.prop.player_name,
                'team': leg.prop.team,
                'opponent': leg.prop.opponent,
                'stat_type': leg.prop.stat_type,
                'line': leg.prop.line,
                'position': leg.prop.position,
                'confidence': leg.final_confidence
            }
            parlay_data['legs'].append(leg_data)
        
        optimized_data['parlays'].append(parlay_data)
    
    # Save optimized parlays JSON
    with open(output_dir / "optimized_parlays.json", "w") as f:
        json.dump(optimized_data, f, indent=2)
    
    # Save summary
    summary = {
        'timestamp': run_timestamp,
        'week': week,
        'type': 'optimized',
        'quality_threshold': quality_threshold,
        'props_analyzed': len(all_analyses),
        'parlays_generated': len(best),
        'accepts': sum(1 for item in best if item['recommendation'] == 'ACCEPT'),
        'modifies': sum(1 for item in best if item['recommendation'] == 'MODIFY'),
        'file': 'optimized_parlays.json'
    }
    
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Optimized parlays saved to: parlay_runs\\wk{week}_optimized\\{run_timestamp}\\")
    
    print("\n💡 KEY INSIGHTS:")
    print("   • Parlays optimized for low correlation")
    print("   • Multiple games and players per parlay = lower risk")
    print("   • Adjusted confidence reflects real win probability")
    print("   • Only ACCEPT/MODIFY parlays shown")
    if quality_threshold:
        print(f"   • Quality filtered to {quality_threshold}%+ confidence")
    print()


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    try:
        if command == 'help' or command == '-h' or command == '--help':
            print_help()
        
        elif command == 'monitor':
            run_single_check()
        
        elif command == 'monitor-continuous':
            run_monitor(interval=60)
        
        elif command == 'monitor-live':
            print_banner()
            print("🎮 LIVE GAME MONITORING (15 minute interval)")
            print("")
            run_monitor(interval=15)
        
        elif command == 'bot':
            run_slack_bot()
        
        elif command == 'analyze':
            week = None
            if len(sys.argv) > 3 and sys.argv[2].lower() == 'week':
                week = int(sys.argv[3])
            run_analysis(week=week)
        
        elif command == 'build-parlays':
            week = None
            if len(sys.argv) > 3 and sys.argv[2].lower() == 'week':
                week = int(sys.argv[3])
            run_parlay_builder(week=week)
        
        elif command == 'build-parlays-optimized':
            week = None
            quality_threshold = None
            
            # Parse arguments
            i = 2
            while i < len(sys.argv):
                arg = sys.argv[i]
                
                if arg == '--quality' and i + 1 < len(sys.argv):
                    try:
                        quality_threshold = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        i += 1
                elif arg.lower() == 'week' and i + 1 < len(sys.argv):
                    try:
                        week = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        i += 1
                else:
                    try:
                        week = int(arg)
                    except ValueError:
                        pass
                    i += 1
            
            run_parlay_builder_optimized(week=week, quality_threshold=quality_threshold)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("")
            print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("")
        print("🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print("")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
