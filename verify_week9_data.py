#!/usr/bin/env python
"""Verify Week 9 data files and system readiness"""

from pathlib import Path
import pandas as pd

data_dir = Path("C:/Users/scott/Desktop/nfl-betting-systemv2/data")
week = 9

print("\n" + "="*60)
print(f"📋 WEEK {week} DATA VERIFICATION")
print("="*60)
print()

# Check betting lines
print("1️⃣ Betting Lines:")
betting_files = [
    data_dir / f"wk{week}_betting_lines_draftkings.csv.csv",
    data_dir / f"wk{week}_betting_lines_draftkings.csv",
]
found = False
for f in betting_files:
    if f.exists():
        df = pd.read_csv(f)
        print(f"   ✅ {f.name}")
        print(f"      Rows: {len(df)}")
        print(f"      Player props: {len(df[df['market'].str.contains('player', na=False)])}")
        found = True
        if '.csv.csv' in f.name:
            print(f"      ⚠️  Double extension - rename to remove one .csv")
        break
if not found:
    print(f"   ❌ No betting lines found for week {week}")

print()

# Check injury report
print("2️⃣ Injury Report:")
injury_files = [
    data_dir / f"wk{week}_injuries.csv",
    data_dir / f"wk{week}-injury-report.csv",
]
found = False
for f in injury_files:
    if f.exists():
        df = pd.read_csv(f)
        print(f"   ✅ {f.name}")
        print(f"      Players: {len(df)}")
        found = True
        break
if not found:
    print(f"   ❌ No injury report found for week {week}")

print()

# Check DVOA (will use Week 8)
print("3️⃣ DVOA Files (expects Week 8 fallback):")
dvoa_files = [
    ('Offensive DVOA', f'wk8_offensive_DVOA.csv'),
    ('Defensive DVOA', f'wk8_dvoa_defensive.csv'),
    ('Def vs WR', f'wk8_dvoa_defensive_vs_receiver.csv.csv'),
]
for name, filename in dvoa_files:
    f = data_dir / filename
    if f.exists():
        df = pd.read_csv(f, header=1)
        print(f"   ✅ {name}: {filename} ({len(df)} teams)")
    else:
        print(f"   ❌ {name}: {filename}")

print()

# Check historical stats
print("4️⃣ Historical Stats (Week 5-8):")
stat_types = ['passing_base', 'receiving_base', 'receiving_usage', 'rushing_base']
weeks_with_data = 0
for check_week in [5, 6, 7, 8]:
    has_all = all((data_dir / f"wk{check_week}_{st}.csv").exists() for st in stat_types)
    if has_all:
        weeks_with_data += 1
print(f"   ✅ {weeks_with_data}/4 weeks have complete historical data")

print()
print("="*60)
print("SYSTEM STATUS:")
print("="*60)
if found:
    print(f"✅ Ready for Week {week} analysis")
    print(f"   - Using Week {week} betting lines")
    print(f"   - Using Week {week} injuries")
    print(f"   - Using Week 8 DVOA (most recent completed)")
    print(f"   - Using Weeks 5-8 historical trends")
else:
    print("❌ Missing critical files")

print()
