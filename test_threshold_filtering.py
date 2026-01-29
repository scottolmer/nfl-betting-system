"""
Test script to verify minimum threshold filtering is working correctly
"""

from scripts.analysis.prop_availability_validator import PropAvailabilityValidator
from scripts.analysis.models import PropAnalysis, PlayerProp
from datetime import datetime

def create_test_prop(player_name, stat_type, line, bet_type="OVER"):
    """Helper to create a test prop"""
    prop = PlayerProp(
        player_name=player_name,
        team="GB",
        opponent="DET",
        position="WR",
        stat_type=stat_type,
        line=line,
        bet_type=bet_type
    )

    # Create a PropAnalysis with the prop
    analysis = PropAnalysis(
        prop=prop,
        final_confidence=70,
        recommendation="TAKE",
        rationale=["Test prop"],
        agent_breakdown={},
        edge_explanation="Test",
        created_at=datetime.now()
    )

    return analysis

def test_threshold_filtering():
    """Test the threshold filtering"""
    print("\n" + "="*70)
    print("TESTING MINIMUM THRESHOLD FILTERING")
    print("="*70)

    # Create validator
    validator = PropAvailabilityValidator(db_path="bets.db")

    # Print current thresholds
    print("\nCurrent Minimum Thresholds:")
    for stat_type, threshold in validator.min_thresholds.items():
        print(f"   {stat_type:20s} >= {threshold}")

    # Create test props - some below threshold, some above
    test_props = [
        # Should be FILTERED (below threshold)
        create_test_prop("Test Player 1", "Receptions", 1.5, "OVER"),  # Below 2.5
        create_test_prop("Test Player 2", "Receptions", 2.5, "UNDER"), # Equal to 2.5 - should pass
        create_test_prop("Test Player 3", "Rush Att", 2.5, "OVER"),    # Below 3.5
        create_test_prop("Test Player 4", "Completions", 10.5, "OVER"), # Below 14.5
        create_test_prop("Test Player 5", "Rec Yds", 15.5, "OVER"),    # Below 19.5

        # Should PASS (above threshold)
        create_test_prop("Test Player 6", "Receptions", 4.5, "OVER"),  # Above 2.5 OK
        create_test_prop("Test Player 7", "Rush Att", 10.5, "OVER"),   # Above 3.5 OK
        create_test_prop("Test Player 8", "Completions", 20.5, "OVER"), # Above 14.5 OK
        create_test_prop("Test Player 9", "Rec Yds", 45.5, "OVER"),    # Above 19.5 OK
        create_test_prop("Test Player 10", "Pass Yds", 250.5, "OVER"), # Above 149.5 OK

        # No threshold defined (should always pass)
        create_test_prop("Test Player 11", "TDs", 0.5, "OVER"),        # No threshold OK
    ]

    print(f"\nTesting with {len(test_props)} props...")
    print("\nBefore filtering:")
    for i, prop in enumerate(test_props, 1):
        print(f"   {i:2d}. {prop.prop.player_name:20s} - {prop.prop.stat_type:15s} {prop.prop.line:6.1f}")

    # Apply filtering
    filtered = validator.filter_by_minimum_thresholds(test_props, verbose=True)

    print(f"\nAfter filtering:")
    for i, prop in enumerate(filtered, 1):
        print(f"   {i:2d}. {prop.prop.player_name:20s} - {prop.prop.stat_type:15s} {prop.prop.line:6.1f}")

    print(f"\nSummary:")
    print(f"   Before: {len(test_props)} props")
    print(f"   After:  {len(filtered)} props")
    print(f"   Filtered: {len(test_props) - len(filtered)} props")

    # Expected: Should filter out 4 props (Test Players 1, 3, 4, 5 are below threshold, Player 2 is equal and should pass)
    expected_filtered = 4  # Players 1, 3, 4, 5
    actual_filtered = len(test_props) - len(filtered)

    print(f"\n{'TEST PASSED' if actual_filtered == expected_filtered else 'TEST FAILED'}")
    print(f"   Expected to filter: {expected_filtered}")
    print(f"   Actually filtered:  {actual_filtered}")

    print("\n" + "="*70)

if __name__ == "__main__":
    test_threshold_filtering()
