"""
Test Script - Analyze Week 7 Props
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )


def test_week_7():
    print("\n" + "="*60)
    print("🏈 NFL PROP ANALYZER - Week 7 Test")
    print("="*60 + "\n")
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    analyzer = PropAnalyzer()
    
    print("📂 Loading Week 7 data...")
    context = loader.load_all_data(week=7)
    
    if not context.get('props'):
        print("\n❌ ERROR: No props found in data!")
        print("Make sure you have wk7_betting_lines_draftkings.csv")
        return
    
    print(f"✅ Loaded {len(context['props'])} props to analyze\n")
    
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
        for reason in analysis.rationale[:2]:
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
