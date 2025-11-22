"""
CLI Tool for Exporting Weekly Parlays for Calibration

Usage:
    # Export single week
    python scripts/export_parlays_cli.py --week 12

    # Export single week with year
    python scripts/export_parlays_cli.py --week 12 --year 2024

    # Export all available weeks
    python scripts/export_parlays_cli.py --all

    # Preview before exporting
    python scripts/export_parlays_cli.py --week 12 --preview

    # Overwrite existing files without prompting
    python scripts/export_parlays_cli.py --week 12 --overwrite
"""

import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.export_parlays import (
    WeeklyParlayExporter,
    export_weekly_parlays,
    export_all_parlays,
    preview_weekly_parlays
)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Export weekly parlays to CSV for calibration analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export parlays for week 12
  python scripts/export_parlays_cli.py --week 12

  # Preview what will be exported
  python scripts/export_parlays_cli.py --week 12 --preview

  # Export all available weeks
  python scripts/export_parlays_cli.py --all

  # Export with overwrite (no prompt)
  python scripts/export_parlays_cli.py --week 12 --overwrite
        """
    )

    # Main options
    parser.add_argument(
        '--week',
        type=int,
        help='NFL week number to export (1-18)'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2024,
        help='Season year (default: 2024)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Export all available weeks'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview export without saving file'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing files without prompting'
    )
    parser.add_argument(
        '--list-weeks',
        action='store_true',
        help='List all weeks with available parlays'
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.week, args.all, args.list_weeks]):
        parser.print_help()
        print("\n[ERROR] Must specify --week, --all, or --list-weeks")
        sys.exit(1)

    # List available weeks
    if args.list_weeks:
        exporter = WeeklyParlayExporter()
        weeks = exporter.get_available_weeks(args.year)

        print(f"\n{'=' * 80}")
        print(f"AVAILABLE WEEKS FOR {args.year}")
        print(f"{'=' * 80}")

        if weeks:
            print(f"\nWeeks with parlays: {', '.join(map(str, weeks))}")
            print(f"Total weeks: {len(weeks)}")
        else:
            print(f"\n[ERROR] No weeks with parlays found for {args.year}")

        print(f"{'=' * 80}\n")
        return

    # Export all weeks
    if args.all:
        print(f"\n>> Exporting all available weeks for {args.year}...\n")
        exported_files = export_all_parlays(year=args.year, overwrite=args.overwrite)

        if exported_files:
            print(f"\n[SUCCESS] Exported {len(exported_files)} weeks")
        else:
            print(f"\n[ERROR] No parlays found to export")

        return

    # Preview mode
    if args.preview:
        print(f"\n>> Previewing export for week {args.week}...\n")
        preview_weekly_parlays(week=args.week, year=args.year)
        return

    # Export single week
    print(f"\n>> Exporting parlays for week {args.week} ({args.year})...\n")
    filepath = export_weekly_parlays(
        week=args.week,
        year=args.year,
        overwrite=args.overwrite
    )

    if filepath:
        print(f"\n[SUCCESS] Export successful!")
        print(f"File location: {filepath}")
        print(f"\nNext steps:")
        print(f"   1. Open {Path(filepath).name} in Excel/Google Sheets")
        print(f"   2. Fill in 'bet_result' column with W or L for each leg")
        print(f"   3. Save the file")
        print(f"   4. Run calibration analysis\n")
    else:
        print(f"\n[ERROR] Export failed or cancelled\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Export cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
