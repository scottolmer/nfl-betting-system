#!/usr/bin/env python
"""Show all files accessed during NFL betting system analysis"""

import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

# Track file access
accessed = {}
_open = open

def track_open(f, *args, **kwargs):
    fp = str(f) if not isinstance(f, int) else f
    if isinstance(fp, str) and any(x in fp.lower() for x in ['.csv', '.json', '.db', '.txt']):
        if fp not in accessed:
            accessed[fp] = 0
        accessed[fp] += 1
    return _open(f, *args, **kwargs)

import builtins
builtins.open = track_open

# Import system
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print()
print("="*80)
print("🏈 FILE ACCESS TRACKER - NFL BETTING SYSTEM")
print("="*80)
print()

# Get inputs
try:
    week_input = input("Enter week (default 11): ").strip()
    week = int(week_input) if week_input else 11
except:
    week = 11

try:
    props_input = input("Analyze how many props (default 10): ").strip()
    max_props = int(props_input) if props_input else 10
except:
    max_props = 10

print()
print(f"Analyzing Week {week}...")
print()

try:
    loader = NFLDataLoader(data_dir="data")
    analyzer = PropAnalyzer()
    
    print("📥 Loading data...")
    context = loader.load_all_data(week=week)
    
    props_list = context.get('props', [])
    analyze_count = min(max_props, len(props_list))
    print(f"📊 Analyzing {analyze_count} of {len(props_list)} props...")
    print()
    
    for i, prop in enumerate(props_list[:max_props], 1):
        try:
            analysis = analyzer.analyze_prop(prop, context)
            if i % 5 == 0:
                print(f"  Progress: {i}/{analyze_count}")
        except Exception as e:
            pass
    
    print()
    print("="*80)
    print("📁 FILES ACCESSED")
    print("="*80)
    print()
    
    if not accessed:
        print("No files tracked")
    else:
        print(f"Total files accessed: {len(accessed)}")
        print()
        
        for filepath in sorted(accessed.keys()):
            filename = Path(filepath).name
            size_str = ""
            try:
                if Path(filepath).exists():
                    size_bytes = Path(filepath).stat().st_size
                    if size_bytes > 1024*1024:
                        size_str = f"  ({size_bytes/(1024*1024):.1f} MB)"
                    elif size_bytes > 1024:
                        size_str = f"  ({size_bytes/1024:.1f} KB)"
                    else:
                        size_str = f"  ({size_bytes} bytes)"
            except:
                pass
            
            print(f"  ✅ {filename:50s}{size_str}")
    
    print()
    print("="*80)
    print("FILE TYPES BREAKDOWN")
    print("="*80)
    print()
    
    by_type = {}
    for fp in accessed.keys():
        ext = Path(fp).suffix if Path(fp).suffix else "no_ext"
        by_type[ext] = by_type.get(ext, 0) + 1
    
    for ext, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {ext:15s}: {count} files")
    
    print()
    print("="*80)
    print()
    
except Exception as e:
    print()
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()

input("Press Enter to exit...")