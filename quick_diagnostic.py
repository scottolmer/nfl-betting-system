#!/usr/bin/env python3
"""
Quick diagnostic - shows which players are missing from roster

Usage: python quick_diagnostic.py (run from project root)
"""
import pandas as pd
import re
from collections import Counter
import sys
from pathlib import Path

def normalize_name(name):
    if not name: return name
    name = str(name).strip().replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.lower()

def main():
    # Ensure we're in the right directory
    if not Path("data/NFL_roster - Sheet1.csv").exists():
        print("ERROR: Please run this from the project root directory")
        print("Usage: cd C:\\Users\\scott\\Desktop\\nfl-betting-system")
        print("       python quick_diagnostic.py")
        sys.exit(1)
    
    # Load roster
    print("Loading roster...")
    try:
        roster_df = pd.read_csv("data/NFL_roster - Sheet1.csv")
        roster_names = set(normalize_name(p) for p in roster_df['Player'].unique() if p)
        print(f"✓ Roster has {len(roster_names)} players\n")
    except Exception as e:
        print(f"ERROR loading roster: {e}")
        sys.exit(1)
    
    # Load betting
    print("Loading betting lines...")
    try:
        betting_df = pd.read_csv("data/wk8_betting_lines_draftkings.csv")
        player_props = betting_df[betting_df['market'].str.startswith('player_')].copy()
        print(f"✓ Betting file has {len(player_props)} player props\n")
    except Exception as e:
        print(f"ERROR loading betting lines: {e}")
        sys.exit(1)
    
    # Find missing
    missing_count = Counter()
    for desc in player_props['description']:
        norm = normalize_name(desc)
        if norm not in roster_names:
            missing_count[desc] += 1
    
    print(f"{'='*70}")
    print(f"MISSING PLAYERS ({len(missing_count)} unique)")
    print(f"{'='*70}\n")
    
    if missing_count:
        # Sort by prop count (most impactful first)
        for player, count in sorted(missing_count.items(), key=lambda x: -x[1])[:30]:
            print(f"  {player:35} → {count:3} props")
        
        if len(missing_count) > 30:
            print(f"\n  ... and {len(missing_count) - 30} more players")
    
    print(f"\n{'='*70}")
    total_missing_props = sum(missing_count.values())
    total_props = len(player_props)
    matched = total_props - total_missing_props
    
    print(f"Summary:")
    print(f"  Total props: {total_props}")
    print(f"  Can use (matched to roster): {matched}")
    print(f"  Will skip (NOT in roster): {total_missing_props}")
    print(f"  Match rate: {matched/total_props*100:.1f}%")
    
    if matched < 30:
        print(f"\n❌ NOT ENOUGH PROPS ({matched} < 30 minimum needed)")
        print(f"   You'll be able to build {matched // 3} parlays maximum")
    else:
        print(f"\n✓ Enough props to build parlays ({matched} >= 30)")
        print(f"   You can build up to {matched // 3} parlays")
    
    print(f"\n{'='*70}")
    print(f"SOLUTION:")
    print(f"{'='*70}")
    print(f"\n1. Copy the missing player list above")
    print(f"\n2. Add them to: data/NFL_roster - Sheet1.csv")
    print(f"   Format: Player,Position,Team")
    print(f"   Example: Drake London,WR,ATL")
    print(f"\n3. Or use the enhanced roster generator:")
    print(f"   python build_enhanced_roster.py")
    print(f"\n4. Then re-run analysis:")
    print(f"   python scripts/run_analysis.py --week 8 --skip-fetch")

if __name__ == "__main__":
    main()
