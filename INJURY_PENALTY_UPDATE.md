================================================================================
INJURY AGENT PENALTY UPDATE - GRANULAR BY STATUS
================================================================================

CHANGE SUMMARY:
---------------
Updated injury_agent.py to apply different penalties based on injury status:

PREVIOUS SCORING:
- OUT: 0
- DOUBTFUL: 20
- QUESTIONABLE: 40  ← Too lenient (only 10 point penalty)
- Healthy: 50

NEW SCORING (Effective Immediately):
- OUT/IR/RESERVE-RET/INACTIVE: 0 (eliminates prop)
- DOUBTFUL: 20 (30 point penalty from baseline 50)
- QUESTIONABLE: 0 (50 point penalty from baseline 50)  ← NEW: More severe
- PROBABLE: 20 (30 point penalty from baseline 50)    ← NEW: Less severe
- DAY TO DAY: 25 (25 point penalty from baseline 50)   ← NEW: Medium penalty
- Healthy/Not listed: 50 (no penalty)

WHAT THIS MEANS:
----------------

Weighted Contribution with Weight 3.0:

STATUS          SCORE  → CONTRIBUTION  → IMPACT ON FINAL CONFIDENCE
OUT             0      → -150 (3.0×50)  → Eliminates prop
DOUBTFUL        20     → -90            → Heavy penalty
QUESTIONABLE    0      → -150           → Severe penalty (50pt)
PROBABLE        20     → -90            → Moderate penalty (30pt)
DAY TO DAY      25     → -75            → Light-moderate penalty (25pt)
Healthy         50     → 0              → No penalty


EXAMPLE: D'ANDRE SWIFT QUESTIONABLE
------------------------------------

BEFORE (Questionable = 40):
  DVOA:       +100
  Injury:     -30 (from 40 score)
  Other agents: ~27
  TOTAL:      ~97 → 61% confidence
  
AFTER (Questionable = 0):
  DVOA:       +100
  Injury:     -150 (from 0 score)
  Other agents: ~27
  TOTAL:      -23 → ~37% confidence
  
Result: Swift drops from top props to completely eliminated!


FILE MODIFIED:
--------------
scripts/analysis/agents/injury_agent.py

Changes:
- Updated analyze() method with granular status penalties
- Added "probable" status support (previously missing)
- Added "day to day" status support
- Updated docstring with penalty breakdown
- Added status labels in rationale output


TO TEST:
--------
1. Run: python diagnostic_injury_system.py
   
   Should now show Swift with:
   - Injury Score: 0 (not 40)
   - Contribution: -150 (not -30)
   - Final Confidence: ~37% (not 61%)

2. Run: python run analyze week 10
   
   Swift should now be:
   - Completely out of top 30 props
   - Not eligible for parlay building (below 62% threshold)

3. Run: python run build-parlays-optimized 10
   
   Swift should no longer appear in any parlays


RATIONALE EXAMPLES:
-------------------
Players will now show in breakdown:
- "🚨 PLAYER OUT (IR)"
- "⚠️ PLAYER DOUBTFUL (30pt penalty)"
- "🟡 PLAYER QUESTIONABLE (50pt penalty)"  ← NEW: Clear communication
- "✅ PLAYER PROBABLE (30pt penalty)"      ← NEW: Positive framing
- "⚠️ PLAYER DAY TO DAY (25pt penalty)"    ← NEW: Medium concern


TUNING OPTIONS:
---------------
If you want to adjust further, you can:

1. Change QUESTIONABLE from 0 to other values:
   - 5: 45pt penalty
   - 10: 40pt penalty
   
2. Change PROBABLE from 20 to other values:
   - 25: 25pt penalty (less than doubtful)
   - 30: 20pt penalty

3. Adjust weight from 3.0 to higher values:
   - 4.0: Injury overrides DVOA entirely
   - 5.0: Injury becomes dominant signal

Current configuration (3.0 weight, QUESTIONABLE=0) is very conservative
and should eliminate most questionable players from consideration.


CAUTION:
--------
With these new penalties, many borderline injured players will be filtered out.
This is intentional but may be too aggressive for your use case.

Monitor results and adjust if needed:
- If you're losing too many props: Increase QUESTIONABLE score to 10-15
- If injured players keep showing up: Decrease QUESTIONABLE to 0 or increase weight

================================================================================
