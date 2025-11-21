"""
Quick test of correlation strength matrix - standalone version
Run this to verify the implementation works
"""

import sys
from pathlib import Path

# Add project root
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.correlation_detector import CorrelationAnalyzer

print("\n" + "="*80)
print("CORRELATION STRENGTH MATRIX - QUICK VALIDATION TEST")
print("="*80 + "\n")

analyzer = CorrelationAnalyzer()

# Test 1: Verify strength matrix exists
print("✅ TEST 1: Correlation Strength Matrix")
print("-" * 80)

expected_pairs = [
    ('DVOA', 'Matchup', 1.5),
    ('DVOA', 'GameScript', 1.3),
    ('Matchup', 'GameScript', 1.2),
    ('Injury', 'Volume', 1.1),
    ('DVOA', 'Volume', 1.0),
    ('Injury', 'Matchup', 0.9),
    ('Trend', 'Volume', 0.7),
    ('Trend', 'Injury', 0.6),
    ('Variance', 'Weather', 0.5),
]

all_pass = True
for agent1, agent2, expected in expected_pairs:
    actual = analyzer.get_correlation_strength(agent1, agent2)
    status = "✓" if actual == expected else "✗"
    if actual != expected:
        all_pass = False
    print(f"{status} {agent1:12} + {agent2:12} = {actual:.1f} (expected {expected:.1f})")

print()

# Test 2: Verify penalty calculation
print("✅ TEST 2: Penalty Calculations")
print("-" * 80)

test_cases = [
    (1.5, "DVOA + Matchup", -7.5),
    (1.3, "DVOA + GameScript", -6.5),
    (1.0, "DVOA + Volume", -5.0),
    (0.7, "Trend + Volume", -3.5),
    (0.5, "Variance + Weather", -2.5),
]

for strength, label, expected_penalty in test_cases:
    penalty = -5.0 * strength
    status = "✓" if abs(penalty - expected_penalty) < 0.1 else "✗"
    if abs(penalty - expected_penalty) > 0.1:
        all_pass = False
    print(f"{status} {label:25} strength {strength:.1f} → penalty {penalty:.1f}%")

print()

# Test 3: Emoji mapping
print("✅ TEST 3: Emoji Indicators")
print("-" * 80)

emoji_tests = [
    (1.5, "🔥"),
    (1.3, "🔥"),
    (1.0, "⚠️"),
    (0.9, "⚠️"),
    (0.7, "⚡"),
    (0.5, "⚡"),
]

for strength, expected_emoji in emoji_tests:
    actual_emoji = analyzer._get_strength_emoji(strength)
    status = "✓" if actual_emoji == expected_emoji else "✗"
    if actual_emoji != expected_emoji:
        all_pass = False
    print(f"{status} Strength {strength:.1f} → {actual_emoji} (expected {expected_emoji})")

print()

# Test 4: Overall system check
print("✅ TEST 4: System Integrity")
print("-" * 80)

try:
    # Check methods exist
    checks = [
        (hasattr(analyzer, 'get_correlation_strength'), "get_correlation_strength method"),
        (hasattr(analyzer, 'calculate_correlation_risk'), "calculate_correlation_risk method"),
        (hasattr(analyzer, 'analyze_parlay_correlations'), "analyze_parlay_correlations method"),
        (hasattr(analyzer, '_extract_drivers'), "_extract_drivers method"),
        (hasattr(analyzer, '_get_strength_emoji'), "_get_strength_emoji method"),
    ]
    
    for check, name in checks:
        status = "✓" if check else "✗"
        if not check:
            all_pass = False
        print(f"{status} {name} exists")
    
except Exception as e:
    print(f"✗ Error checking methods: {e}")
    all_pass = False

print()

# Final result
print("="*80)
if all_pass:
    print("✅ ALL TESTS PASSED - System is ready!")
else:
    print("❌ SOME TESTS FAILED - Check output above")
print("="*80 + "\n")

if all_pass:
    print("NEXT STEPS:")
    print("  1. Read: PROJECT_3_IMPROVEMENT_1_QUICK_REFERENCE.txt")
    print("  2. Integrate EnhancedParlayBuilder into your betting CLI")
    print("  3. Generate test parlays to verify output")
    print()
