"""
Custom Parlay Builder - CLI Entry Point
Interactive tool for manually building 6-leg parlays from analyzed props.

Usage:
    python scripts/run_custom_parlay_builder.py --week 12
    python scripts/run_custom_parlay_builder.py --week 12 --year 2024
    python scripts/run_custom_parlay_builder.py --week 12 --preview

Options:
    --week: NFL week number (required)
    --year: Year (default: 2024)
    --preview: Preview available props without building a parlay
"""

import sys
from pathlib import Path
import logging
import argparse
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.custom_parlay_builder import CustomParlayBuilder, run_custom_parlay_builder


def main():
    """Main entry point for custom parlay builder"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Custom Parlay Builder - Build manual 6-leg parlays from analyzed props"
    )
    parser.add_argument(
        "--week",
        type=int,
        required=True,
        help="NFL week number (e.g., 12)"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2024,
        help="Year (default: 2024)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview available props without building a parlay"
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=50,
        help="Minimum confidence threshold for displaying props (default: 50)"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Display header
    print("\n" + "=" * 100)
    print("🏈 NFL CUSTOM PARLAY BUILDER")
    print("=" * 100)
    print(f"Week: {args.week}")
    print(f"Year: {args.year}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    # STEP 1: Load all data
    print("📂 STEP 1: LOADING NFL DATA")
    print("-" * 100)

    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=args.week)

    if context.get('props') is None or len(context['props']) == 0:
        print("❌ No props found after loading! Check your data files.")
        print(f"   Make sure betting lines for week {args.week} exist in the data directory.")
        print(f"   Expected file: data/betting_lines_wk_{args.week}_*.csv")
        return

    print(f"✅ Loaded data for {len(context['props'])} props")
    print()

    # STEP 2: Analyze all props with orchestrator
    print("🤖 STEP 2: ANALYZING PROPS WITH 8-AGENT SYSTEM")
    print("-" * 100)

    analyzer = PropAnalyzer()
    analyzed_props = analyzer.analyze_all_props(
        context=context,
        min_confidence=args.min_confidence
    )

    print(f"✅ Analyzed {len(analyzed_props)} props (min confidence: {args.min_confidence}%)")
    print()

    # STEP 3: Display props or run builder
    if args.preview:
        # Preview mode - just show the props
        print("📊 PREVIEW MODE: DISPLAYING ALL ANALYZED PROPS")
        print("-" * 100)

        builder = CustomParlayBuilder(analyzed_props, args.week, args.year)
        builder.display_all_props(
            sort_by="confidence",
            min_confidence=args.min_confidence,
            limit=50
        )

        print("\n💡 TIP: To build a custom parlay, run without --preview flag:")
        print(f"   python scripts/run_custom_parlay_builder.py --week {args.week}")
        print()

    else:
        # Interactive builder mode
        print("🏗️  STEP 3: INTERACTIVE PARLAY BUILDER")
        print("-" * 100)
        print()

        parlay_id = run_custom_parlay_builder(analyzed_props, args.week, args.year)

        if parlay_id:
            print("\n" + "=" * 100)
            print("✅ SUCCESS - CUSTOM PARLAY CREATED")
            print("=" * 100)
            print(f"Parlay ID: {parlay_id}")
            print(f"Week: {args.week}")
            print(f"Tracking: parlay_tracking.json")
            print()
            print("Next steps:")
            print("  1. Mark as bet: Use parlay_tracker.mark_bet(parlay_id, bet_amount)")
            print("  2. Log results: Use parlay_tracker.mark_result(parlay_id, result, prop_results)")
            print("  3. View stats: Use parlay_tracker.get_statistics()")
            print("=" * 100)
            print()
        else:
            print("\n" + "=" * 100)
            print("❌ No parlay was created")
            print("=" * 100)
            print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Custom parlay builder interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
