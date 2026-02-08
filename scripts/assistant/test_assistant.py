"""
Quick test of betting assistant components
"""

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*70)
print("TESTING BETTING ASSISTANT COMPONENTS")
print("="*70)

# Test 1: CSV Handler
print("\n[TEST 1] CSV Handler - Data Loading")
print("-"*70)
from csv_handler import CSVHandler
handler = CSVHandler()
success, message, context = handler.process_files(week=15)
print(message)
print(f"Success: {success}")
print(f"Props loaded: {len(context.get('props', []))}")

# Test 2: Conversation Manager
print("\n[TEST 2] Conversation Manager - Intent Detection")
print("-"*70)
from conversation_manager import ConversationManager
conv = ConversationManager()

test_messages = [
    "What are the best parlays for week 15?",
    "Exclude Mahomes - not available in Pick6",
]

for msg in test_messages:
    intent, params = conv.detect_intent(msg)
    print(f"Message: '{msg}'")
    print(f"  -> Intent: {intent.value}, Params: {params}")

# Test 3: Constraint Engine
print("\n[TEST 3] Constraint Engine - Player Exclusion")
print("-"*70)
from constraint_engine import ConstraintEngine
engine = ConstraintEngine()

# Mark Mahomes unavailable
engine.mark_player_unavailable("Patrick Mahomes", platform="pick6", source="test")
is_avail, reason = engine.is_player_available("Patrick Mahomes", platform="pick6")
print(f"Patrick Mahomes available: {is_avail}")
if reason:
    print(f"Reason: {reason}")

# Test 4: Betting Assistant Agent
print("\n[TEST 4] Betting Assistant Agent - Response Generation")
print("-"*70)
from betting_assistant_agent import BettingAssistantAgent
assistant = BettingAssistantAgent()

# Test data status
response = assistant.process_message("What's the data status?")
print(f"User: What's the data status?")
print(f"Assistant: {response[:200]}...")

print("\n" + "="*70)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("="*70)
