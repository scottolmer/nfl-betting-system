"""
Debug player name matching
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

def debug_player_names():
    print("🔍 Debugging Player Name Matching")
    print("="*60)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=7)
    
    # Get sample prop players
    print("\n📊 Sample Players from BETTING LINES:")
    sample_props = context['props'][:10]
    for prop in sample_props:
        print(f"   '{prop['player_name']}' - {prop['position']}")
    
    # Get sample players from usage data
    print("\n📊 Sample Players from USAGE DATA:")
    usage = context.get('usage', {})
    for i, player_name in enumerate(list(usage.keys())[:10]):
        snap_pct = usage[player_name].get('snap_share_pct', 0)
        target_pct = usage[player_name].get('target_share_pct', 0)
        print(f"   '{player_name}' - Snap: {snap_pct:.1f}%, Target: {target_pct:.1f}%")
    
    # Check if AJ Brown is in the data
    print("\n🔍 Looking for AJ Brown variants:")
    search_terms = ['AJ Brown', 'A.J. Brown', 'A.J.  Brown', 'Brown']
    
    for term in search_terms:
        matches = [k for k in usage.keys() if term.lower() in k.lower()]
        if matches:
            for match in matches:
                snap = usage[match].get('snap_share_pct', 0)
                target = usage[match].get('target_share_pct', 0)
                print(f"   FOUND: '{match}' - Snap: {snap:.1f}%, Target: {target:.1f}%")
    
    # Check DeVonta Smith
    print("\n🔍 Looking for DeVonta Smith variants:")
    search_terms = ['DeVonta Smith', 'Devonta Smith', 'Smith']
    
    for term in search_terms:
        matches = [k for k in usage.keys() if 'smith' in k.lower() and 'devonta' in k.lower()]
        if matches:
            for match in matches:
                snap = usage[match].get('snap_share_pct', 0)
                target = usage[match].get('target_share_pct', 0)
                print(f"   FOUND: '{match}' - Snap: {snap:.1f}%, Target: {target:.1f}%")
    
    print("\n" + "="*60)
    print("✅ Debug complete!")

if __name__ == "__main__":
    debug_player_names()
