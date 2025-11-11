#!/usr/bin/env python
"""Manually add a parlay to tracking"""

from scripts.analysis.parlay_tracker import ParlayTracker

tracker = ParlayTracker("parlay_tracking.json")

# Example: Add a parlay manually
props = [
    {
        "player": "Patrick Mahomes",
        "team": "KC", 
        "opponent": "LV",
        "stat_type": "passing_yards",
        "line": 250.5,
        "direction": "OVER",
        "confidence": 78.2,
        "agent_scores": {}
    }
]

parlay_id = tracker.add_parlay(
    week=9,
    year=2024,
    parlay_type="traditional",
    props=props,
    raw_confidence=78.2,
    effective_confidence=78.2,
    correlations=[],
    payout_odds=450,
    kelly_bet_size=150.0
)

print(f"✅ Added: {parlay_id}")
print("Now open tracking_app.py to mark bet/results")
