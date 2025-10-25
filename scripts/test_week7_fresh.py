"""
Force-reload test - bypasses all caching
"""

import sys
import logging
from pathlib import Path
import importlib

# Clear any existing module cache
for module in list(sys.modules.keys()):
    if 'analysis' in module:
        del sys.modules[module]

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Force fresh import
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_week_7():
    print("\n" + "="*60)
    print("🏈 NFL PROP ANALYZER - Week 7 (FORCE RELOAD)")
    print("="*60 + "\n")
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    analyzer = PropAnalyzer()
    
    print("📂 Loading Week 7 data (with new loader)...")
    context = loader.load_all_data(week=7)
    
    if not context.get('props'):
        print("\n❌ ERROR: No props found!")
        return
    
    print(f"✅ Loaded {len(context['props'])} props\n")
    
    # Check what data was actually loaded
    print("📊 Data Check:")
    print(f"   Usage data: {len(context.get('usage', {}))} players")
    print(f"   Alignment data: {len(context.get('alignment', {}))} players")
    print(f"   Receiving base: {len(context.get('receiving_base', {}))} players")
    print(f"   Rushing base: {len(context.get('rushing_base', {}))} RBs")
    print(f"   Injuries: {sum(len(v) for v in context.get('injuries', {}).values())} players\n")
    
    if len(context.get('usage', {})) == 0:
        print("⚠️  WARNING: Usage data not loaded!")
        print("Check that wk7_receiving_usage.csv exists in data folder\n")
    
    print("🧠 Running analysis...\n")
    top_props = analyzer.get_top_props(context, n=5, min_confidence=50)
    
    print("\n" + "="*60)
    print("📊 TOP 5 PROPS")
    print("="*60 + "\n")
    
    for i, analysis in enumerate(top_props, 1):
        prop = analysis.prop
        
        print(f"{i}. {analysis.recommendation}")
        print(f"   Player: {prop.player_name} ({prop.team} vs {prop.opponent})")
        print(f"   Bet: {prop.stat_type} {analysis.prop.direction} {prop.line}")
        print(f"   Confidence: {analysis.final_confidence}")
        
        print(f"   Rationale:")
        for reason in analysis.rationale[:3]:
            print(f"      • {reason}")
        print()
    
    print("\n✅ Analysis Complete!\n")

if __name__ == "__main__":
    setup_logging()
    try:
        test_week_7()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
