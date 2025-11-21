"""
Debug: Check why DVOA files aren't being loaded
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

data_dir = Path("./data")

print("\n" + "="*70)
print("CHECKING WHAT FILES EXIST IN /data")
print("="*70)

print("\nAll WK12 files in /data:")
for f in data_dir.glob("wk12*"):
    print(f"  ✓ {f.name}")

print("\nAll WK11 files in /data:")
for f in data_dir.glob("wk11*"):
    print(f"  ✓ {f.name}")

print("\n" + "="*70)
print("CHECKING DVOA OFFENSIVE FALLBACK")
print("="*70)

for try_week in [12, 11, 10, 9]:
    print(f"\nWeek {try_week}:")
    
    patterns = [
        f"wk{try_week}_offensive_DVOA.csv",
        f"wk{try_week}_offensive_dvoa.csv",
        f"wk{try_week}_dvoa_offensive.csv",
        f"DVOA_Off_wk_{try_week}.csv"
    ]
    
    for pattern in patterns:
        fpath = data_dir / pattern
        exists = fpath.exists()
        emoji = "✓" if exists else "✗"
        print(f"  {emoji} {pattern}")
        
    # Try glob
    glob_results = list(data_dir.glob(f"wk{try_week}_offensive_DVOA.csv"))
    print(f"  GLOB result: {len(glob_results)} matches")
    if glob_results:
        print(f"    Found: {glob_results[0].name}")
        break

print("\n" + "="*70)
print("CHECKING BETTING LINES FALLBACK")
print("="*70)

for try_week in [12, 11, 10]:
    print(f"\nWeek {try_week}:")
    
    patterns = [
        f"wk{try_week}_betting_lines_draftkings.csv",
        f"wk{try_week}_betting_lines_TRANSFORMED.csv",
        f"betting_lines_wk_{try_week}_live.csv"
    ]
    
    for pattern in patterns:
        fpath = data_dir / pattern
        exists = fpath.exists()
        emoji = "✓" if exists else "✗"
        print(f"  {emoji} {pattern}")

print("\n" + "="*70)
