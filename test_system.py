"""
Quick diagnostic script to test the system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("="*70)
print("SYSTEM DIAGNOSTIC TEST")
print("="*70)
print()

# Test 1: Python packages
print("1. Testing Python packages...")
try:
    import pandas as pd
    import numpy as np
    print("   ✅ pandas, numpy installed")
except ImportError as e:
    print(f"   ❌ Missing package: {e}")
    sys.exit(1)

# Test 2: Project imports
print("\n2. Testing project imports...")
try:
    from scripts.analysis.data_loader import NFLDataLoader
    print("   ✅ data_loader imported")
except Exception as e:
    print(f"   ❌ data_loader import failed: {e}")
    
try:
    from scripts.analysis.orchestrator import PropAnalyzer
    print("   ✅ orchestrator imported")
except Exception as e:
    print(f"   ❌ orchestrator import failed: {e}")

try:
    from scripts.analysis.parlay_builder import ParlayBuilder
    print("   ✅ parlay_builder imported")
except Exception as e:
    print(f"   ❌ parlay_builder import failed: {e}")

# Test 3: Data files
print("\n3. Checking data files...")
data_dir = project_root / "data"
week = 7

required_files = [
    f"wk{week}_offensive_DVOA.csv",
    f"wk{week}_def_v_wr_DVOA.csv",
    f"wk{week}_betting_lines_draftkings.csv"
]

for filename in required_files:
    filepath = data_dir / filename
    if filepath.exists():
        print(f"   ✅ {filename}")
    else:
        print(f"   ❌ MISSING: {filename}")

# Test 4: Try loading data
print("\n4. Testing data loader...")
try:
    loader = NFLDataLoader(data_dir=str(data_dir))
    context = loader.load_all_data(week=week)
    
    print(f"   ✅ Loaded {len(context['betting_lines'])} betting lines")
    print(f"   ✅ DVOA Offensive: {context['dvoa_off'] is not None}")
    print(f"   ✅ DVOA Defensive: {context['dvoa_def'] is not None}")
    print(f"   ✅ Def vs WR: {context['def_vs_wr'] is not None}")
    print(f"   ✅ Context created successfully")
    
except Exception as e:
    print(f"   ❌ Data loading failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
