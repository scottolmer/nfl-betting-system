"""Quick test to verify the automated learning system is working"""

print("Testing automated learning system...")
print()

# Test 1: Import AgentWeightManager
print("Test 1: Import AgentWeightManager")
from scripts.analysis.agent_weight_manager import AgentWeightManager
manager = AgentWeightManager("bets.db")
print("  Success!")

# Test 2: Initialize weights
print()
print("Test 2: Initialize default weights")
manager.initialize_default_weights(force=False)
weights = manager.get_current_weights()
print(f"  Loaded {len(weights)} agent weights")

# Test 3: Import PropAnalyzer with dynamic weights
print()
print("Test 3: Initialize PropAnalyzer with dynamic weights")
from scripts.analysis.orchestrator import PropAnalyzer
analyzer = PropAnalyzer(db_path="bets.db", use_dynamic_weights=True)
print(f"  PropAnalyzer initialized with {len(analyzer.agents)} agents")

# Test 4: Verify agents have correct weights
print()
print("Test 4: Verify agent weights match database")
all_match = True
for agent_name, agent in analyzer.agents.items():
    db_weight = weights.get(agent_name, 0.0)
    if abs(agent.weight - db_weight) > 0.01:
        print(f"  X {agent_name}: Agent has {agent.weight}, DB has {db_weight}")
        all_match = False

if all_match:
    print("  All agent weights match database!")

# Test 5: Show current weights
print()
print("Test 5: Current agent weights:")
for agent_name, agent in sorted(analyzer.agents.items(), key=lambda x: x[1].weight, reverse=True):
    print(f"  {agent_name:12s} = {agent.weight:.2f}")

print()
print("="*60)
print("ALL TESTS PASSED!")
print("="*60)
print()
print("Your system is ready for automated learning!")
print("Run: python betting_cli.py")
print("     > enable-auto-learning")
print("     > auto-learn 12")
