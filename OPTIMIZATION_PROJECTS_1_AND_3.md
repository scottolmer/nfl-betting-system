## OPTIMIZATION PROJECT 1: Kill the Neutral Score Problem

### Current Problem
Agents return score=50 ("AVOID") when they lack data, which artificially suppresses overall confidence even when other agents have strong signals.

**Example:**
- 7 agents score 60-75 (strong signal)
- 1 agent returns 50 (missing data like weather)
- Final weighted average gets dragged down unnecessarily

### Root Cause
When agents can't find data (Weather agent without weather, Injury agent without injury data, etc.), they return a neutral 50 instead of being excluded from calculation.

### Current Code Location
- `scripts/analysis/orchestrator.py` → `analyze_prop()` method (lines 46-76)
- Each agent returns `(score, direction, rationale)` or None
- Orchestrator currently includes all agents in weighted average

### The Fix
**Step 1: Modify agents to return None when data unavailable**

Instead of:
```python
if not opp_def:
    return (50, "AVOID", rationale)  # Artificially neutral
```

Do:
```python
if not opp_def:
    return None  # Orchestrator will skip this agent
```

**Agents to update:**
- `weather_agent.py` - return None if no weather data
- `injury_agent.py` - return None if no injury data
- Other agents that currently return 50 as fallback

**Step 2: Modify orchestrator to skip None results**

Current code (line 57):
```python
analysis_result = agent.analyze(prop, context)
if analysis_result is None:
    score, direction, rationale = 50, "AVOID", [f"⚠️ {agent_name} returned None"]
else:
    score, direction, rationale = analysis_result
```

Should become:
```python
analysis_result = agent.analyze(prop, context)
if analysis_result is None:
    continue  # Skip this agent entirely - don't include in weighted average
else:
    score, direction, rationale = analysis_result
```

**Step 3: Modify confidence calculation to handle variable agent counts**

Current `_calculate_final_confidence()` always uses all agents. Need to:
1. Track which agents actually contributed
2. Only average scores from agents that had real data
3. Normalize weights to sum to 1.0 for contributing agents

### Success Criteria
- Props with missing agent data no longer artificially suppressed
- Confidence scores reflect only data-backed signals
- System logs which agents contributed vs. skipped
- Test: A prop with 7 strong agents at 65+ should reach 65+, not get dragged to 58

### Files to Modify
1. `scripts/analysis/orchestrator.py` - analyze_prop() and _calculate_final_confidence()
2. `scripts/analysis/agents/weather_agent.py` - add None return
3. `scripts/analysis/agents/injury_agent.py` - add None return
4. Any other agents with fallback 50 scores

### Testing
Run `python test_under_fix.py` and check:
- OVER average stays ~56%
- UNDER average stays ~54%
- Confidence distribution shifts UP (fewer props at 50-60%, more at 60-70%)
- Agent breakdown shows which agents contributed to each prop

---

## OPTIMIZATION PROJECT 3: Strategic Correlation Risk Detection

### Current Problem
Parlay builder checks player diversity but ignores **statistical correlation**. Two different players can have identical correlation if driven by same matchup signal.

**Example of Hidden Correlation:**
- Josh Allen 250+ Pass Yards (driven by HOU weak pass D via DVOA)
- Khalil Shakir 5+ Receptions (ALSO driven by HOU weak pass D via DVOA)
- Builder sees "different players" ✓ but they're correlated ✗

### Root Cause
- `parlays` command uses simple `ParlayBuilder` (player diversity only)
- `opt-parlays` command uses `DependencyAnalyzer` with Claude (catches correlations)
- Standard parlays ignore correlation entirely

### Current Code Locations
- `scripts/analysis/parlay_builder.py` → `build_parlays()` (player diversity only)
- `scripts/analysis/dependency_analyzer.py` → analyzes correlations (Claude-based)
- Only called from `opt-parlays`, not standard `parlays`

### The Fix

**Step 1: Enhance prop analysis metadata**

Each `PropAnalysis` should track which agent drove the decision:

```python
# In orchestrator.py, add to PropAnalysis:
analysis.top_contributing_agents = [
    ('DVOA', 25),      # Agent name, contribution to confidence
    ('Volume', 15),
    ('Matchup', 12)
]
```

**Step 2: Create correlation scorer in parlay builder**

```python
def calculate_correlation_risk(leg1: PropAnalysis, leg2: PropAnalysis) -> float:
    """
    Compare top drivers of each prop.
    If same agents drive both, they're correlated.
    
    Returns: correlation_adjustment (0.0 to -15.0 confidence penalty)
    """
    # Get top 2 agents for each
    leg1_drivers = set(leg1.top_contributing_agents[:2])
    leg2_drivers = set(leg2.top_contributing_agents[:2])
    
    # If they share top drivers, they're correlated
    shared_drivers = len(leg1_drivers & leg2_drivers)
    
    return -5 * shared_drivers  # -5 per shared driver
```

**Step 3: Apply correlation penalty in parlay builder**

When building parlays, for each leg pair in the parlay:
```python
total_correlation_penalty = 0
for i, leg1 in enumerate(parlay_legs):
    for leg2 in parlay_legs[i+1:]:
        penalty = calculate_correlation_risk(leg1, leg2)
        total_correlation_penalty += penalty

# Adjust parlay confidence
parlay.combined_confidence += total_correlation_penalty
```

**Step 4: Make dependency analysis standard**

Move `DependencyAnalyzer` logic into `ParlayBuilder`:
- Don't call Claude for every parlay (too slow)
- Use simple agent-based correlation detection
- Only call Claude for final validation on top parlays

### Success Criteria
- Standard `parlays` command now detects correlated props
- Parlays with same-driver correlations show reduced confidence
- Parlay output explains correlation adjustments
- Test: Josh Allen + Shakir parlay shows correlation penalty in display

### Example Output Change
Before:
```
**PARLAY 21** - Confidence: 71%
  Leg 1: Josh Allen Pass Yds OVER 250
  Leg 2: Khalil Shakir Receptions OVER 4
```

After:
```
**PARLAY 21** - Confidence: 68% (was 71%, -3% correlation)
  Leg 1: Josh Allen Pass Yds OVER 250 [driven by DVOA, Matchup]
  Leg 2: Khalil Shakir Receptions OVER 4 [driven by DVOA, Matchup]
  ⚠️  Correlation: Both legs driven by HOU weak pass defense
```

### Files to Modify
1. `scripts/analysis/orchestrator.py` - add top_contributing_agents to PropAnalysis
2. `scripts/analysis/parlay_builder.py` - add correlation detection logic
3. `scripts/analysis/models.py` - update PropAnalysis dataclass

### Testing
Run `parlays 50` and check:
- Parlays with same-game receivers show correlation adjustments
- Parlay confidence reflects correlation penalties
- Output explains which agents drive correlation
- Compare vs `opt-parlays` output—should be similar now

---

## Project Dependencies
- Project 1 must complete first (cleaner signals = better correlation detection)
- Then Project 3 (use clean signals to detect correlations)

## Estimated Effort
- Project 1: 2-3 hours (straightforward code changes)
- Project 3: 3-4 hours (requires careful testing of correlation math)

## Expected Impact
- Project 1: +2-3% confidence accuracy
- Project 3: -5-10% false positives (fewer correlated parlays that look good but fail)
- Combined: Significantly more reliable parlay generation
