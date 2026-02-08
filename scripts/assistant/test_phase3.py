"""
Test Phase 3 Features - Intelligent Recommendations & Skill Integration
"""

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print("TESTING PHASE 3 FEATURES")
print("="*70)

# Test 1: Suggestion Engine
print("\n[TEST 1] Suggestion Engine - Context-aware suggestions")
print("-"*70)
from suggestion_engine import SuggestionEngine

engine = SuggestionEngine()
state = {
    'has_props': True,
    'has_parlays': True,
    'has_week': True,
    'week': 15,
    'parlay_count': 8,
    'excluded_players_count': 2,
    'last_intent': 'build_parlay',
    'platform': 'pick6'
}

suggestions = engine.generate_suggestions(state, max_suggestions=3)
print(engine.format_suggestions_for_display(suggestions))

# Test 2: Skill Integrator
print("\n\n[TEST 2] Skill Integrator - Historical Query")
print("-"*70)
from skill_integrator import SkillIntegrator

integrator = SkillIntegrator()
result = integrator.invoke_chat_query("How did Week 14 perform?")
print(result[:300] + "...")

# Test 3: Enhanced Pattern Learning
print("\n\n[TEST 3] Enhanced Pattern Learning - Confidence Scoring")
print("-"*70)
from constraint_engine import ConstraintEngine

engine_constraints = ConstraintEngine()
pattern_data = {
    'pattern': 'repeated_prop_type_exclusion',
    'occurrences': 5
}
confidence = engine_constraints.calculate_pattern_confidence(pattern_data, total_interactions=10)
print(f"Pattern confidence: {confidence}")

# Test 4: Betting Assistant with Phase 3 Features
print("\n\n[TEST 4] Betting Assistant Agent - With Suggestions")
print("-"*70)
from betting_assistant_agent import BettingAssistantAgent

assistant = BettingAssistantAgent()

# Simulate a conversation state
assistant.conversation.set_current_week(15)
assistant.conversation.set_current_props([
    {
        'player_name': 'Patrick Mahomes',
        'team': 'KC',
        'opponent': 'LAC',
        'stat_type': 'Pass Yds',
        'bet_type': 'OVER',
        'line': 287.5,
        'confidence': 75,
        'edge_explanation': 'Strong DVOA matchup',
        'agent_breakdown': {
            'DVOA': {'raw_score': 78, 'weight': 2.0, 'direction': 'OVER'},
            'HitRate': {'raw_score': 72, 'weight': 2.0, 'direction': 'OVER'}
        },
        'rationale': ['Strong offensive DVOA', 'Weak defensive matchup', 'High volume expected']
    }
])

response = assistant.process_message("What's the data status?")
print("User: What's the data status?")
print(f"Assistant:\n{response}")

print("\n" + "="*70)
print("PHASE 3 TESTS COMPLETED SUCCESSFULLY")
print("="*70)
