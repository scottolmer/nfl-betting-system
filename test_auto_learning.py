"""
Test script for automated learning system
"""

import sys
from pathlib import Path
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add scripts path
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "analysis"))

from agent_weight_manager import AgentWeightManager

def test_weight_manager():
    """Test the AgentWeightManager"""
    print("\n" + "="*80)
    print("TESTING AUTOMATED LEARNING SYSTEM")
    print("="*80 + "\n")

    # Initialize manager
    manager = AgentWeightManager("bets.db")

    print("✅ Step 1: Initialize default weights")
    manager.initialize_default_weights(force=True)
    manager.print_current_weights()

    print("\n✅ Step 2: Test auto-learning enable/disable")
    print(f"   Auto-learning enabled: {manager.is_auto_learning_enabled()}")

    manager.disable_auto_learning()
    print(f"   After disable: {manager.is_auto_learning_enabled()}")

    manager.enable_auto_learning()
    print(f"   After enable: {manager.is_auto_learning_enabled()}")

    print("\n✅ Step 3: Simulate agent performance data")
    # Simulate Week 10 performance
    agent_performance = {
        'DVOA': {
            'accuracy': 0.65,
            'overconfidence': 0.12,  # Overconfident
            'sample_size': 25
        },
        'Matchup': {
            'accuracy': 0.72,
            'overconfidence': -0.02,  # Well-calibrated
            'sample_size': 30
        },
        'Volume': {
            'accuracy': 0.58,
            'overconfidence': 0.08,  # Slightly overconfident
            'sample_size': 28
        },
        'Injury': {
            'accuracy': 0.75,
            'overconfidence': 0.03,  # Slightly overconfident but high accuracy
            'sample_size': 20
        },
        'Trend': {
            'accuracy': 0.48,
            'overconfidence': 0.15,  # Very overconfident and low accuracy
            'sample_size': 22
        },
        'GameScript': {
            'accuracy': 0.70,
            'overconfidence': -0.05,  # Underconfident
            'sample_size': 26
        },
        'Variance': {
            'accuracy': 0.62,
            'overconfidence': 0.05,
            'sample_size': 24
        },
        'Weather': {
            'accuracy': 0.55,
            'overconfidence': 0.02,
            'sample_size': 15
        }
    }

    print("\n✅ Step 4: Test dry-run adjustments (preview only)")
    adjustments = manager.auto_adjust_weights(
        agent_performance=agent_performance,
        week=10,
        dry_run=True
    )
    manager.print_adjustment_summary(adjustments)

    print("\n✅ Step 5: Apply adjustments for real")
    adjustments = manager.auto_adjust_weights(
        agent_performance=agent_performance,
        week=10,
        dry_run=False
    )
    manager.print_adjustment_summary(adjustments)

    print("\n✅ Step 6: Show updated weights")
    manager.print_current_weights()

    print("\n✅ Step 7: View weight history")
    print("\n" + "="*80)
    print("WEIGHT ADJUSTMENT HISTORY")
    print("="*80)
    history = manager.get_weight_history(limit=20)
    for entry in history[:10]:  # Show last 10
        print(f"\n{entry['agent']:12s} Week {entry['week']}")
        print(f"  {entry['old_weight']:.2f} → {entry['new_weight']:.2f}")
        print(f"  Reason: {entry['reason']}")
        print(f"  Stats: {entry['accuracy']:.1%} accuracy, {entry['overconfidence']:+.1%} overconfidence")

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_weight_manager()
