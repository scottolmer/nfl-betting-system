================================================================================
INJURY DIAGNOSTIC COMMAND - BETTING CLI
================================================================================

NEW COMMAND: injury-diagnostic

USAGE:
------

1. Check overall injury system status:
   📊 Enter command: injury-diagnostic
   
   Shows:
   ✅ Injury data loaded (how many players in report)
   ✅ Status breakdown (count of OUT/DOUBTFUL/QUESTIONABLE/PROBABLE)
   ✅ Injury Agent configuration (weight and status)

2. Analyze specific player:
   📊 Enter command: injury-diagnostic d'andre swift
   
   Shows:
   ✅ Whether player is in injury report
   ✅ Player's injury status
   ✅ All props for that player
   ✅ Injury score for each prop (0-50)
   ✅ Final confidence after injury adjustment
   ✅ Full agent breakdown showing how injury impacts confidence

EXAMPLES:
---------

Check system health:
  📊 Enter command: injury-diagnostic
  
Check D'Andre Swift:
  📊 Enter command: injury-diagnostic swift
  
Check Patrick Mahomes:
  📊 Enter command: injury-diagnostic mahomes
  
Check Travis Kelce:
  📊 Enter command: injury-diagnostic kelce

OUTPUT EXPLANATION:
-------------------

STEP 1: Injury Data Loading
  ✅ Injury data loaded: 1013 lines
  ✅ D'Andre Swift found in injury data
     → D'Andre Swift,CHI,RB,Groin,Questionable,Subscribers Only

STEP 2: Injury Agent Configuration
  ✅ Injury Agent found with weight: 3.0
  ✅ Weight is high (3.0) - injuries take priority

STEP 3: [Player] Analysis
  Final Confidence: 37%
  Recommendation: AVOID
  
  Injury Agent Breakdown:
    Score: 0
    Weight: 3.0
    Rationale: ['🟡 PLAYER QUESTIONABLE (50pt penalty)']
    ✅ Injury penalty IS being applied!

  All Agent Scores:
    ↑ DVOA            Score: 100 × Weight: 2.00 = +100.00
    ↓ Injury          Score:   0 × Weight: 3.00 = -150.00  ← CRITICAL HIT
    ↑ GameScript      Score:  58 × Weight: 1.30 = +10.40
    → Volume          Score:  45 × Weight: 1.20 = -6.00
    Total: -45.60 (final conf: 37%)

INTERPRETATION:
---------------

Score 0 = Severe penalty (50 point deduction)
  Status: OUT, DOUBTFUL, QUESTIONABLE
  Message: 🟡 PLAYER QUESTIONABLE (50pt penalty)

Score 20 = Moderate penalty (30 point deduction)
  Status: PROBABLE, DOUBTFUL
  Message: ✅ PLAYER PROBABLE (30pt penalty)

Score 25 = Light penalty (25 point deduction)
  Status: DAY TO DAY
  Message: ⚠️ PLAYER DAY TO DAY (25pt penalty)

Score 50 = No penalty (player not in report or healthy)
  Status: Not listed or healthy
  Message: (no message shown)

FILTERING LOGIC:
----------------

With weight 3.0, a Questionable player needs:
- Other agents to score 80+ on average to overcome -150 injury hit
- Usually results in 35-45% confidence
- Automatically filtered out from "top props" (60% threshold)
- NOT eligible for parlays (65% minimum)

This is the CORRECT behavior - Questionable players should be heavily discounted!

COMMAND SYNTAX:
---------------

injury-diagnostic                → System overview
injury-diagnostic swift          → Analyze Swift
injury-diagnostic d'andre swift  → Analyze with full name
injury-diagnostic mahomes        → Analyze Mahomes
injury-diagnostic <any part of name>

The search is case-insensitive and works with partial names!

TIPS:
-----

✓ Run this before generating parlays to verify injury data is loaded
✓ Check specific players if you're unsure why they're not showing in top props
✓ Use this to validate the injury system is working correctly
✓ Run after updating injury CSV to verify changes took effect
✓ The injury-diagnostic shows exactly WHY a player was filtered out

================================================================================
