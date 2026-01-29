"""
Test the Hit Rate Agent to verify it's working correctly
"""

from scripts.analysis.agents.hit_rate_agent import HitRateAgent
from scripts.analysis.models import PlayerProp
from scripts.analysis.data_loader import NFLDataLoader
from pathlib import Path

def test_hit_rate_agent():
    """Test the hit rate agent with real data"""
    print("\n" + "="*70)
    print("TESTING HIT RATE AGENT")
    print("="*70)

    # Load data for week 14 (so we have historical data from weeks 11-13)
    loader = NFLDataLoader(data_dir="data")
    context = loader.load_all_data(week=14)

    # Check if historical stats loaded
    historical_stats = context.get('historical_stats', {})
    print(f"\nHistorical weeks loaded: {list(historical_stats.keys())}")

    # Debug: Check what's in the data
    if historical_stats and 'wk13' in historical_stats:
        wk13 = historical_stats['wk13']
        if 'receiving_base' in wk13:
            df = wk13['receiving_base']
            print(f"\nWeek 13 receiving_base has {len(df)} players")
            print(f"Sample players: {df['Player'].head(5).tolist()}")

    # Create a test prop - let's use a real player
    # Example: Test with a WR who likely has reception data
    test_prop = PlayerProp(
        player_name="Puka Nacua",  # Well-known WR with good data
        team="LAR",
        opponent="SF",
        position="WR",
        stat_type="Receptions",
        line=5.5,
        bet_type="OVER",
        week=14
    )

    # Initialize agent
    agent = HitRateAgent(weight=2.0)

    # Analyze the prop
    print(f"\nAnalyzing: {test_prop.player_name} - {test_prop.stat_type} {test_prop.line}")
    print("-" * 70)

    result = agent.analyze(test_prop, context)

    if result is None:
        print("Result: No data available for this player/stat combination")
    else:
        score, direction, rationale = result
        print(f"\nScore: {score:.1f}")
        print(f"Direction: {direction}")
        print(f"\nRationale:")
        for item in rationale:
            # Handle unicode encoding issues on Windows console
            try:
                print(f"  {item}")
            except UnicodeEncodeError:
                print(f"  {item.encode('ascii', 'ignore').decode('ascii')}")

    # Test with a different stat type
    print("\n" + "="*70)
    test_prop2 = PlayerProp(
        player_name="Christian McCaffrey",
        team="SF",
        opponent="LAR",
        position="RB",
        stat_type="Rush Yds",
        line=75.5,
        bet_type="OVER",
        week=14
    )

    print(f"\nAnalyzing: {test_prop2.player_name} - {test_prop2.stat_type} {test_prop2.line}")
    print("-" * 70)

    result2 = agent.analyze(test_prop2, context)

    if result2 is None:
        print("Result: No data available for this player/stat combination")
    else:
        score, direction, rationale = result2
        print(f"\nScore: {score:.1f}")
        print(f"Direction: {direction}")
        print(f"\nRationale:")
        for item in rationale:
            # Handle unicode encoding issues on Windows console
            try:
                print(f"  {item}")
            except UnicodeEncodeError:
                print(f"  {item.encode('ascii', 'ignore').decode('ascii')}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_hit_rate_agent()
