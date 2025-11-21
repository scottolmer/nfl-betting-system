#!/usr/bin/env python
"""
Quick verification test for Props Validator installation
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "="*70)
print("✅ PROPS VALIDATOR INSTALLATION VERIFICATION")
print("="*70 + "\n")

# Test 1: Import validator
try:
    from scripts.analysis.props_validator import PropsValidator
    print("✓ props_validator.py imports successfully")
except ImportError as e:
    print(f"✗ FAILED to import props_validator: {e}")
    sys.exit(1)

# Test 2: Import models
try:
    from scripts.analysis.models import PlayerProp, PropAnalysis
    print("✓ models.py imports successfully")
except ImportError as e:
    print(f"✗ FAILED to import models: {e}")
    sys.exit(1)

# Test 3: Import orchestrator with validator
try:
    from scripts.analysis.orchestrator import PropAnalyzer
    print("✓ orchestrator.py imports successfully (includes PropsValidator)")
except ImportError as e:
    print(f"✗ FAILED to import orchestrator: {e}")
    sys.exit(1)

# Test 4: Import parlay_builder with validator
try:
    from scripts.analysis.parlay_builder import ParlayBuilder
    print("✓ parlay_builder.py imports successfully (includes PropsValidator)")
except ImportError as e:
    print(f"✗ FAILED to import parlay_builder: {e}")
    sys.exit(1)

# Test 5: Basic validation
try:
    prop_dict = {
        'player_name': 'Test Player',
        'team': 'KC',
        'opponent': 'LAC',
        'position': 'QB',
        'stat_type': 'Pass Yds',
        'line': 250.5,
    }
    
    prop_obj = PropsValidator.ensure_player_prop(prop_dict)
    assert isinstance(prop_obj, PlayerProp)
    assert prop_obj.player_name == 'Test Player'
    print("✓ Validator converts dict to PlayerProp correctly")
except Exception as e:
    print(f"✗ Validator test failed: {e}")
    sys.exit(1)

# Test 6: Check orchestrator has PropsValidator usage
try:
    import inspect
    source = inspect.getsource(PropAnalyzer.analyze_all_props)
    if 'PropsValidator.validate' in source:
        print("✓ orchestrator.analyze_all_props has PropsValidator calls")
    else:
        print("✗ orchestrator.analyze_all_props missing PropsValidator calls")
        sys.exit(1)
except Exception as e:
    print(f"⚠️  Could not verify orchestrator source: {e}")

# Test 7: Check parlay_builder has PropsValidator usage
try:
    import inspect
    source = inspect.getsource(ParlayBuilder.build_parlays)
    if 'PropsValidator.validate' in source:
        print("✓ parlay_builder.build_parlays has PropsValidator call")
    else:
        print("✗ parlay_builder.build_parlays missing PropsValidator call")
        sys.exit(1)
except Exception as e:
    print(f"⚠️  Could not verify parlay_builder source: {e}")

# Test 8: PropAnalysis validation
try:
    prop_dict = {
        'player_name': 'Patrick Mahomes',
        'team': 'KC',
        'opponent': 'LAC',
        'position': 'QB',
        'stat_type': 'Pass Yds',
        'line': 250.5,
    }
    
    # Create analysis with dict (testing validation)
    analysis = PropAnalysis(
        prop=prop_dict,
        final_confidence=75,
        recommendation='MODERATE OVER',
        rationale=['QB is hot'],
        agent_breakdown={},
        edge_explanation='Edge detected'
    )
    
    # Validate - should convert dict to PlayerProp
    validated = PropsValidator.validate_prop_analysis(analysis)
    
    assert isinstance(validated.prop, PlayerProp)
    assert validated.prop.player_name == 'Patrick Mahomes'
    print("✓ PropAnalysis validation works (converts dict to PlayerProp)")
except Exception as e:
    print(f"✗ PropAnalysis validation test failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL INSTALLATION CHECKS PASSED!")
print("="*70)
print("\n🎉 Your NFL Betting System is now ready to use!\n")
print("You can now run:")
print("  python run analyze week 8")
print("  python run build-parlays-optimized 8")
print()
