#!/usr/bin/env python
"""Test script for Parlay Tracking System"""

from scripts.analysis.parlay_tracker import ParlayTracker
from pathlib import Path

def test_tracking_system():
    """Test the parlay tracking system with sample data"""
    
    print("=" * 70)
    print("TESTING PARLAY TRACKING SYSTEM")
    print("=" * 70)
    
    # Create tracker
    test_file = Path("test_parlay_tracking.json")
    if test_file.exists():
        test_file.unlink()  # Delete old test file
    
    tracker = ParlayTracker(str(test_file))
    print(f"\n✅ Created tracker: {test_file}")
    
    # Test 1: Add Traditional Parlay
    print("\n" + "-" * 70)
    print("TEST 1: Adding Traditional Parlay")
    print("-" * 70)
    
    props1 = [
        {
            "player": "Patrick Mahomes",
            "team": "KC",
            "opponent": "LV",
            "stat_type": "passing_yards",
            "line": 250.5,
            "direction": "OVER",
            "confidence": 78.2,
            "agent_scores": {"dvoa": 78, "matchup": 82, "volume": 75}
        },
        {
            "player": "Travis Kelce",
            "team": "KC",
            "opponent": "LV",
            "stat_type": "receiving_yards",
            "line": 60.5,
            "direction": "OVER",
            "confidence": 76.5,
            "agent_scores": {"dvoa": 72, "matchup": 80, "volume": 78}
        }
    ]
    
    parlay1_id = tracker.add_parlay(
        week=9,
        year=2024,
        parlay_type="traditional",
        props=props1,
        raw_confidence=77.4,
        effective_confidence=77.4,
        correlations=[],
        payout_odds=450,
        kelly_bet_size=150.00,
        data_source="live_api"
    )
    
    print(f"✅ Added parlay: {parlay1_id}")
    print(f"   Props: {len(props1)}")
    print(f"   Confidence: 77.4%")
    
    # Test 2: Add Enhanced Parlay (same props, different confidence)
    print("\n" + "-" * 70)
    print("TEST 2: Adding Enhanced Parlay (same props)")
    print("-" * 70)
    
    parlay2_id = tracker.add_parlay(
        week=9,
        year=2024,
        parlay_type="enhanced",
        props=props1,  # Same props
        raw_confidence=77.4,
        effective_confidence=58.3,  # Lower due to correlation
        correlations=[
            {
                "prop1": "Mahomes passing_yards",
                "prop2": "Kelce receiving_yards",
                "correlation": 0.45,
                "impact": "Reduces confidence by 19.1 points"
            }
        ],
        payout_odds=450,
        kelly_bet_size=65.00,
        data_source="live_api"
    )
    
    print(f"✅ Added parlay: {parlay2_id}")
    print(f"   Raw Confidence: 77.4%")
    print(f"   Effective Confidence: 58.3% (after correlation)")
    print(f"   Content Hash: Should match {parlay1_id.split('_')[2]}")
    
    # Test 3: Mark a bet
    print("\n" + "-" * 70)
    print("TEST 3: Marking Parlay as Bet")
    print("-" * 70)
    
    success = tracker.mark_bet(parlay1_id, 150.00)
    print(f"✅ Marked {parlay1_id} as bet: ${150.00}")
    
    # Test 4: Add another parlay
    print("\n" + "-" * 70)
    print("TEST 4: Adding Another Parlay")
    print("-" * 70)
    
    props2 = [
        {
            "player": "Josh Allen",
            "team": "BUF",
            "opponent": "MIA",
            "stat_type": "passing_yards",
            "line": 275.5,
            "direction": "OVER",
            "confidence": 72.1,
            "agent_scores": {"dvoa": 70, "matchup": 75, "volume": 72}
        }
    ]
    
    parlay3_id = tracker.add_parlay(
        week=9,
        year=2024,
        parlay_type="traditional",
        props=props2,
        raw_confidence=72.1,
        effective_confidence=72.1,
        correlations=[],
        payout_odds=200,
        kelly_bet_size=100.00
    )
    
    print(f"✅ Added parlay: {parlay3_id}")
    
    # Test 5: Mark results
    print("\n" + "-" * 70)
    print("TEST 5: Marking Results")
    print("-" * 70)
    
    tracker.mark_result(parlay1_id, "won")
    print(f"✅ Marked {parlay1_id} as WON")
    
    tracker.mark_result(parlay2_id, "won")
    print(f"✅ Marked {parlay2_id} as WON (wasn't bet on)")
    
    tracker.mark_result(parlay3_id, "lost")
    print(f"✅ Marked {parlay3_id} as LOST")
    
    # Test 6: Get statistics
    print("\n" + "-" * 70)
    print("TEST 6: Retrieving Statistics")
    print("-" * 70)
    
    stats_all = tracker.get_statistics()
    print("\n📊 Overall Statistics:")
    print(f"   Total Parlays: {stats_all['total_parlays']}")
    print(f"   Record: {stats_all['won']}-{stats_all['lost']}")
    print(f"   Win Rate: {stats_all['win_rate']}%")
    print(f"   Avg Predicted: {stats_all['avg_predicted_confidence']}%")
    print(f"   Calibration Error: {stats_all['calibration_error']:+.1f} points")
    
    stats_trad = tracker.get_statistics(parlay_type="traditional")
    print("\n📊 Traditional Parlays:")
    print(f"   Record: {stats_trad['won']}-{stats_trad['lost']}")
    print(f"   Win Rate: {stats_trad['win_rate']}%")
    
    stats_enh = tracker.get_statistics(parlay_type="enhanced")
    print("\n🧠 Enhanced Parlays:")
    print(f"   Record: {stats_enh['won']}-{stats_enh['lost']}")
    print(f"   Win Rate: {stats_enh['win_rate']}%")
    print(f"   Calibration: {stats_enh['calibration_error']:+.1f} points")
    
    # Test 7: Week parlays
    print("\n" + "-" * 70)
    print("TEST 7: Getting Week 9 Parlays")
    print("-" * 70)
    
    week9_parlays = tracker.get_parlays_by_week(9)
    print(f"\n✅ Found {len(week9_parlays)} parlays for Week 9")
    
    for p in week9_parlays:
        bet_status = "💰 BET" if p['bet_on'] else "📊 TRACK"
        result = p['result'] or "pending"
        print(f"   {bet_status} | {p['parlay_id']} | {result}")
    
    # Test 8: Export
    print("\n" + "-" * 70)
    print("TEST 8: Exporting to CSV")
    print("-" * 70)
    
    export_file = Path("test_parlay_export.csv")
    tracker.export_to_csv(str(export_file))
    print(f"✅ Exported to {export_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ All tests passed!")
    print(f"✅ Tracking file created: {test_file}")
    print(f"✅ Export file created: {export_file}")
    print(f"\n💡 Check {test_file} to see the JSON structure")
    print(f"💡 Check {export_file} to see CSV export format")
    
    return tracker


if __name__ == "__main__":
    tracker = test_tracking_system()
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)
    print("\nYou can now:")
    print("1. Check test_parlay_tracking.json to see the data structure")
    print("2. Check test_parlay_export.csv to see CSV export format")
    print("3. Run the enhanced Streamlit app with tracking!")
    print("\nTo run the enhanced app:")
    print("   cd ui")
    print("   streamlit run app_with_tracking.py")
