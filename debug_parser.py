"""
Simple debug script to test the parser
"""
import re
from pathlib import Path

form_path = Path('data/betting_history/week_8/test_validation_form.txt')

with open(form_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("VALIDATION FORM PARSER DEBUG")
print("=" * 80)
print()

# Test 1: Find parlay sections
print("TEST 1: Looking for parlay sections with pattern: ┌.*?PARLAY.*?└")
parlay_pattern = r'┌.*?PARLAY\s+(\d)(\d).*?└'
parlay_matches = list(re.finditer(parlay_pattern, content, re.DOTALL))
print(f"Parlay sections found: {len(parlay_matches)}")
print()

if parlay_matches:
    # Show first parlay
    first = parlay_matches[0]
    print("FIRST PARLAY SECTION (first 500 chars):")
    print(first.group(0)[:500])
    print()
    print(f"Groups: num_legs={first.group(1)}, parlay_num={first.group(2)}")
    print()
    
    # Test 2: Look for legs in first parlay
    first_section = first.group(0)
    print("TEST 2: Looking for legs in first parlay")
    leg_pattern = r'Leg\s+(\d+)/(\d+):\s+([^(]+)\((\w+)\)\s*-\s*(\w+)'
    leg_matches = list(re.finditer(leg_pattern, first_section))
    print(f"Legs found: {len(leg_matches)}")
    
    for i, leg in enumerate(leg_matches):
        print(f"  Leg {i+1}: {leg.group(3).strip()} ({leg.group(4)}) - {leg.group(5)}")
    print()
    
    # Test 3: Look for actual results
    print("TEST 3: Looking for ACTUAL RESULT entries")
    results = re.findall(r'ACTUAL RESULT:\s*(\w+)', first_section)
    print(f"Results found: {len(results)}")
    print(f"Values: {results}")
    print()
    
    # Test 4: Look for bet type
    print("TEST 4: Looking for bet type")
    bet_matches = re.findall(r'Bet Type:\s+([A-Z\s]+?)\s+([\d.]+)\s*\(vs\s+(\w+)\)', first_section)
    print(f"Bets found: {len(bet_matches)}")
    for bet in bet_matches:
        print(f"  {bet[0].strip()} {bet[1]} (vs {bet[2]})")

print()
print("=" * 80)
