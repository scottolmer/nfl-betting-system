"""
Diagnostic: Check D'Andre Swift confidence breakdown
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

# Load context
loader = NFLDataLoader('data')
context = loader.load_all_data(week=10)

# Find Swift in the props
swift_props = [p for p in context.get('props', []) if "d'andre swift" in p.get('player_name', '').lower()]

print("=" * 80)
print("D'ANDRE SWIFT DIAGNOSTIC")
print("=" * 80)
print()

if not swift_props:
    print("❌ No props found for D'Andre Swift")
    sys.exit(1)

print(f"Found {len(swift_props)} prop(s) for D'Andre Swift:")
print()

analyzer = PropAnalyzer()

for prop_data in swift_props:
    print(f"Prop: {prop_data.get('stat_type')} O{prop_data.get('line')}")
    print("-" * 80)
    
    # Analyze
    analysis = analyzer.analyze_prop(prop_data, context)
    
    print(f"Final Confidence: {analysis.final_confidence}%")
    print()
    print("Agent Breakdown:")
    print()
    
    for agent_name, result in analysis.agent_breakdown.items():
        score = result.get('raw_score', 50)
        weight = result.get('weight', 0)
        direction = result.get('direction', 'N/A')
        rationale = result.get('rationale', [])
        
        weighted_contribution = (score - 50) * weight
        
        print(f"  {agent_name:15} | Score: {score:3.0f} | Weight: {weight:4.2f} | Contribution: {weighted_contribution:+6.2f}")
        
        if rationale:
            for r in rationale:
                print(f"                    └─ {r}")
        print()
    
    print(f"Overall Recommendation: {analysis.recommendation}")
    print()
    print(f"Edge Explanation: {analysis.edge_explanation}")
    print()
    print("=" * 80)
    print()

# Check injury report
print("Injury Report Content:")
print("-" * 80)
injury_text = context.get('injuries', '')
if injury_text:
    lines = injury_text.split('\n')
    for line in lines:
        if "swift" in line.lower():
            print(line)
else:
    print("❌ No injury data loaded")

print()
