#!/usr/bin/env python
"""
COMPREHENSIVE INJURY AGENT DIAGNOSTIC
Verifies that the injury system is correctly:
1. Loading injury data
2. Parsing player names
3. Applying penalties
4. Using proper weights
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.agents.injury_agent import InjuryAgent

print("\n" + "=" * 80)
print("INJURY AGENT DIAGNOSTIC - COMPLETE SYSTEM CHECK")
print("=" * 80 + "\n")

# ============================================================================
# STEP 1: Check Injury Data Loading
# ============================================================================
print("STEP 1: Injury Data Loading")
print("-" * 80)

loader = NFLDataLoader('data')
context = loader.load_all_data(week=10)

injury_text = context.get('injuries')

if not injury_text:
    print("❌ CRITICAL: No injury data loaded!")
    print("   File might not exist: wk10-injury-report.csv")
    sys.exit(1)

lines = injury_text.split('\n')
print(f"✅ Injury data loaded: {len(lines)} lines")

# Find Swift in injury data
swift_in_injuries = any("swift" in line.lower() for line in lines)
if swift_in_injuries:
    print("✅ D'Andre Swift found in injury data")
    for line in lines:
        if "swift" in line.lower():
            print(f"   → {line}")
else:
    print("⚠️  D'Andre Swift NOT found in injury data")

print()

# ============================================================================
# STEP 2: Test Injury Agent Directly
# ============================================================================
print("STEP 2: Injury Agent Direct Test")
print("-" * 80)

injury_agent = InjuryAgent()
print(f"✅ InjuryAgent created with weight: {injury_agent.weight}")

if injury_agent.weight != 3.0:
    print(f"⚠️  WARNING: Weight is {injury_agent.weight}, expected 3.0")
else:
    print(f"✅ Weight correctly set to 3.0 (high priority)")

print()

# ============================================================================
# STEP 3: Check Orchestrator Has Injury Agent
# ============================================================================
print("STEP 3: Orchestrator Agent Configuration")
print("-" * 80)

analyzer = PropAnalyzer()
agent_names = list(analyzer.agents.keys())
print(f"✅ Orchestrator has {len(agent_names)} agents:")
for name in agent_names:
    agent = analyzer.agents[name]
    print(f"   - {name:15} (weight: {agent.weight})")

if 'Injury' not in agent_names:
    print("❌ CRITICAL: Injury agent not in orchestrator!")
    sys.exit(1)

if analyzer.agents['Injury'].weight != 3.0:
    print(f"⚠️  WARNING: Injury agent weight is {analyzer.agents['Injury'].weight}, expected 3.0")

print()

# ============================================================================
# STEP 4: Analyze D'Andre Swift
# ============================================================================
print("STEP 4: D'Andre Swift Analysis")
print("-" * 80)

swift_props = [p for p in context.get('props', []) if "d'andre swift" in p.get('player_name', '').lower()]

if not swift_props:
    print("❌ No props found for D'Andre Swift")
    print("   (This might be OK if he doesn't have betting props this week)")
else:
    print(f"Found {len(swift_props)} prop(s) for D'Andre Swift\n")
    
    for prop_data in swift_props:
        print(f"Analyzing: {prop_data.get('stat_type')} O{prop_data.get('line')}")
        print("-" * 80)
        
        analysis = analyzer.analyze_prop(prop_data, context)
        
        print(f"Final Confidence: {analysis.final_confidence}%")
        print(f"Recommendation: {analysis.recommendation}\n")
        
        # Check Injury Agent specifically
        injury_result = analysis.agent_breakdown.get('Injury', {})
        injury_score = injury_result.get('raw_score', 'N/A')
        injury_weight = injury_result.get('weight', 'N/A')
        injury_rationale = injury_result.get('rationale', [])
        
        print("Injury Agent Breakdown:")
        print(f"  Score: {injury_score}")
        print(f"  Weight: {injury_weight}")
        print(f"  Rationale: {injury_rationale if injury_rationale else 'None'}")
        
        if injury_score < 50 and injury_rationale:
            print("  ✅ Injury penalty IS being applied!")
        elif injury_score == 50:
            print("  ⚠️  WARNING: Injury score is 50 (neutral) - player might not be found")
        else:
            print("  ⚠️  Unexpected injury score")
        
        print("\nAll Agent Scores:")
        print("-" * 80)
        
        total_contribution = 0
        for agent_name, result in analysis.agent_breakdown.items():
            score = result.get('raw_score', 50)
            weight = result.get('weight', 0)
            contribution = (score - 50) * weight
            total_contribution += contribution
            
            status = "↑" if contribution > 0 else ("↓" if contribution < 0 else "→")
            print(f"  {status} {agent_name:15} Score: {score:3.0f} × Weight: {weight:4.2f} = {contribution:+6.2f}")
        
        print("-" * 80)
        print(f"  Total Contribution: {total_contribution:+.2f} (final conf: {analysis.final_confidence}%)")
        print()

print()

# ============================================================================
# STEP 5: Summary
# ============================================================================
print("SUMMARY")
print("-" * 80)

checks = {
    "Injury data loads": injury_text is not None,
    "Swift in injury data": swift_in_injuries,
    "Injury agent in orchestrator": 'Injury' in analyzer.agents,
    "Injury agent weight is 3.0": analyzer.agents.get('Injury', {}).weight == 3.0 if 'Injury' in analyzer.agents else False,
}

all_pass = all(checks.values())

for check_name, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")

print()

if all_pass:
    print("✅ SYSTEM FULLY OPERATIONAL")
    print("   Injury penalties should now be properly applied!")
else:
    print("❌ SYSTEM HAS ISSUES")
    print("   Review the failures above")

print()
print("=" * 80)
