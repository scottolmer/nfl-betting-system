# Project 1 Implementation: Kill the Neutral Score Problem

## Status: IN PROGRESS

### Overview
This project modifies the orchestrator and agents to return `None` when data is unavailable, preventing missing data from artificially suppressing confidence scores.

### Changes Required

#### 1. orchestrator.py Modifications

**Location:** `scripts/analysis/orchestrator.py`

**Changes in `analyze_prop()` method:**

Replace this section (lines 46-76):
```python
for agent_name, agent in self.agents.items():
    try:
        analysis_result = agent.analyze(prop, context)
        if analysis_result is None:
             score, direction, rationale = 50, "AVOID", [f"⚠️ {agent_name} returned None"]
        else:
            score, direction, rationale = analysis_result
```

With:
```python
for agent_name, agent in self.agents.items():
    try:
        analysis_result = agent.analyze(prop, context)
        if analysis_result is None:
            # Agent lacks data - SKIP it entirely instead of including 50
            self.logger.info(f"  ⏭️  {agent_name} returned None (missing data) - SKIPPING")
            continue
        else:
            score, direction, rationale = analysis_result
```

**Changes in `_calculate_final_confidence()` method:**

Modify to track which agents contributed:
```python
def _calculate_final_confidence(self, agent_results: Dict, bet_type: str = 'OVER') -> int:
    """Combine agent scores using weighted average of contributing agents only
    
    Agents that lack data are excluded from the calculation,
    not included as neutral 50s.
    """
    total_weighted_score = 0.0
    total_weight = 0.0
    contributing_agents = []

    for agent_name, result in agent_results.items():
        weight = result.get('weight', 0)
        if weight > 0:
            raw_score = result.get('raw_score', 50)
            total_weighted_score += raw_score * weight
            total_weight += weight
            contributing_agents.append(agent_name)

    if total_weight == 0:
        # Fallback: equal weight all agents that have data
        for agent_name, result in agent_results.items():
            raw_score = result.get('raw_score', 50)
            total_weighted_score += raw_score
            total_weight += 1
            if agent_name not in contributing_agents:
                contributing_agents.append(agent_name)

    if total_weight == 0:
        self.logger.warning(f"No agents produced scores - using 50")
        return 50

    weighted_avg = total_weighted_score / total_weight
    final_score_int = int(round(max(0, min(100, weighted_avg))))
    
    self.logger.debug(f"Confidence calculation: {len(contributing_agents)} agents contributed, "
                     f"weighted average = {weighted_avg:.1f}% → {final_score_int}%")
    
    return final_score_int
```

#### 2. weather_agent.py Modifications

**Location:** `scripts/analysis/agents/weather_agent.py`

Replace the return at the bottom:
```python
# OLD:
if not game_weather:
    return (50, "OVER", [])
```

With:
```python
# NEW:
if not game_weather:
    return None  # No weather data - skip this agent
```

And:
```python
# OLD:
if venue == 'dome':
    return (50, "OVER", [])
```

With:
```python
# NEW:
if venue == 'dome':
    return None  # Indoor venue - weather irrelevant, skip agent
```

**Complete modified section:**
```python
def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
    rationale = []
    score = 50
    
    weather = context.get('weather', {})
    
    game_key = f"{prop.team}_vs_{prop.opponent}"
    game_weather = weather.get(game_key, {})
    
    if not game_weather:
        game_key = f"{prop.opponent}_vs_{prop.team}"
        game_weather = weather.get(game_key, {})
    
    # CHANGE 1: Return None if no weather data found
    if not game_weather:
        return None
    
    temp = game_weather.get('temperature', 70)
    wind = game_weather.get('wind_mph', 0)
    venue = game_weather.get('venue_type', 'outdoor')
    
    # CHANGE 2: Return None for dome games (weather N/A)
    if venue == 'dome':
        return None
    
    if temp <= 20 and prop.position in ['QB', 'WR', 'TE']:
        score -= 10
        rationale.append(f"⚠️ EXTREME COLD: {temp}°F affects passing")
    
    if wind >= 20 and prop.position in ['QB', 'WR', 'TE']:
        score -= 12
        rationale.append(f"⚠️ HIGH WIND: {wind} mph")
    
    direction = "OVER" if score >= 50 else "UNDER"
    return (score, direction, rationale)
```

#### 3. injury_agent.py Modifications

**Location:** `scripts/analysis/agents/injury_agent.py`

Modify the `analyze()` method to return `None` when injury data is not available:

```python
def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
    """Analyzes injury status for the prop player
    
    Returns None if injury data is not loaded/unavailable.
    Injury status doesn't apply if we don't have data source.
    """
    if not hasattr(self, 'logger'): 
        return None  # Can't analyze without logger - skip

    rationale = []
    score = 50
    injury_text = context.get('injuries')

    if not self.injury_data and injury_text:
        self._parse_injury_report(injury_text)
    
    # CHANGE: Return None if we have no injury data at all
    if not self.injury_data:
        return None  # No injury data available - skip agent

    player_name_norm = normalize_player_name(prop.player_name)
    status = self.injury_data.get(player_name_norm)

    # If player is in the injury data, return the analysis
    # If player is not in injury data but we have injury data, assume healthy (score=50)
    if status:
        # ... existing status logic ...
        pass
    else:
        score = 50  # Player not in injury report, assume healthy
    
    direction = "AVOID" if score < 30 else ("UNDER" if score < 50 else "OVER")
    final_rationale = rationale if score != 50 else []

    return (score, direction, final_rationale)
```

### Implementation Checklist

- [ ] **Step 1:** Modify `orchestrator.py` - `analyze_prop()` method to skip agents returning None
- [ ] **Step 2:** Modify `orchestrator.py` - `_calculate_final_confidence()` to track contributing agents
- [ ] **Step 3:** Modify `weather_agent.py` to return None when data unavailable
- [ ] **Step 4:** Modify `injury_agent.py` to return None when injury data not loaded
- [ ] **Step 5:** Run test_under_fix.py to validate results
- [ ] **Step 6:** Check log output for agent contribution metrics

### Expected Changes After Implementation

**Before Fix:**
```
OVER average confidence: ~58%
UNDER average confidence: ~52%
Confidence distribution: Heavy concentration at 50-60% (pulled down by neutral agents)
```

**After Fix:**
```
OVER average confidence: ~65%
UNDER average confidence: ~54%
Confidence distribution: More spread, fewer artificially suppressed props at 50-60%
```

### Testing

Run this command after implementation:
```bash
python test_under_fix.py
```

Expected output:
- OVER confidence increases by 2-3%
- Prop count increases (more props now meet 60%+ threshold)
- Agent breakdown shows which agents contributed to each prop
- No more 50% scores from agents with missing data

### Files Modified

1. `scripts/analysis/orchestrator.py`
2. `scripts/analysis/agents/weather_agent.py`
3. `scripts/analysis/agents/injury_agent.py`

### Rollback Instructions

If issues arise, revert these files from git:
```bash
git checkout scripts/analysis/orchestrator.py
git checkout scripts/analysis/agents/weather_agent.py
git checkout scripts/analysis/agents/injury_agent.py
```

---

## Implementation Notes

The key insight here is that a neutral 50 score from a missing-data agent is misleading. It's not saying "this agent thinks the prop is balanced" - it's saying "this agent has no data." These are different things.

By returning `None` instead, we allow the orchestrator to exclude that agent from the confidence calculation entirely. This way:

- 7 agents with 65+ scores → final confidence reflects that strength (not dragged to 58)
- Props with strong 5-agent signals aren't penalized for missing weather/injury data
- The system more accurately reflects the actual evidence available

This is especially important for early-season games where weather data may be sparse, and for less well-known players where injury data might not be comprehensive.
