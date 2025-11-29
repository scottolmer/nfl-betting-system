"""Score all weeks that have sufficient data available"""

from pathlib import Path
from auto_scorer import load_csv_with_conflict_handling, score_week
import pandas as pd
import argparse

def find_scoreable_weeks(data_dir: Path):
    """Find which weeks can be scored based on available data"""

    # Find all week files
    receiving_files = sorted(data_dir.glob('wk*_receiving_base.csv'))
    weeks_available = []

    for file in receiving_files:
        week_num = int(file.stem.split('wk')[1].split('_')[0])
        df = load_csv_with_conflict_handling(file)
        if df is not None and 'G' in df.columns:
            avg_g = df['G'].head(20).apply(lambda x: int(x) if pd.notna(x) else 0).mean()
            weeks_available.append((week_num, avg_g))

    # Sort by week number
    weeks_available.sort()

    # Determine which weeks can be scored
    scoreable = []
    for week, avg_g in weeks_available:
        # Can score if single-game data available
        if avg_g <= 1.5:
            scoreable.append(week)

    return scoreable


def main():
    parser = argparse.ArgumentParser(description='Score all available weeks')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--data-dir', type=str, default='data', help='Path to data directory')
    parser.add_argument('--db', type=str, help='Path to database file (default: bets.db)')

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    db_path = Path(args.db) if args.db else None

    # Find scoreable weeks
    scoreable = find_scoreable_weeks(data_dir)

    print("="*70)
    print("BATCH SCORING ALL AVAILABLE WEEKS")
    print("="*70)
    print(f"Scoreable weeks: {scoreable}")
    print()

    if args.dry_run:
        print("[DRY RUN MODE - Results will not be saved]\n")
    else:
        print("[LIVE MODE - Results will be saved to database]\n")

    # Score each week
    for week in scoreable:
        print(f"\n{'='*70}")
        print(f"SCORING WEEK {week}")
        print('='*70)

        output = score_week(
            week=week,
            db_path=db_path,
            data_dir=data_dir,
            dry_run=args.dry_run,
            force=not args.dry_run
        )

        print(output)

    print("\n" + "="*70)
    print("BATCH SCORING COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
