"""
Complete .env Diagnostic Tool
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("ENV FILE DIAGNOSTIC")
print("=" * 70)
print()

# Step 1: Find .env file
project_root = Path(__file__).parent
env_file = project_root / '.env'

print("Step 1: Checking .env file location")
print(f"  Looking for: {env_file}")
print(f"  File exists: {env_file.exists()}")
print()

if env_file.exists():
    # Step 2: Read raw file contents
    print("Step 2: Reading .env file contents")
    print("-" * 70)
    try:
        with open(env_file, 'r') as f:
            contents = f.read()
            print(contents)
    except Exception as e:
        print(f"  ERROR reading file: {e}")
    print("-" * 70)
    print()
    
    # Step 3: Load with dotenv
    print("Step 3: Loading with python-dotenv")
    load_dotenv(env_file)
    print(f"  load_dotenv() called")
    print()
    
    # Step 4: Check environment variables
    print("Step 4: Checking if variables are accessible")
    
    variables = {
        'ODDS_API_KEY': os.getenv('ODDS_API_KEY'),
        'CLAUDE_API_KEY': os.getenv('CLAUDE_API_KEY'),
        'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN'),
        'SLACK_WEBHOOK': os.getenv('SLACK_WEBHOOK'),
    }
    
    for key, value in variables.items():
        if value:
            # Mask for security
            masked = value[:15] + '...' if len(value) > 15 else value
            print(f"  ✅ {key}: {masked}")
        else:
            print(f"  ❌ {key}: NOT FOUND")
    
    print()
    
    # Step 5: Specific ODDS_API_KEY check
    print("Step 5: Detailed ODDS_API_KEY analysis")
    odds_key = os.getenv('ODDS_API_KEY')
    if odds_key:
        print(f"  ✅ Found!")
        print(f"  Length: {len(odds_key)} characters")
        print(f"  First 20 chars: {odds_key[:20]}")
        print(f"  Has spaces: {' ' in odds_key}")
        has_quotes = ('"' in odds_key) or ("'" in odds_key)
        print(f"  Has quotes: {has_quotes}")
    else:
        print(f"  ❌ NOT FOUND")
        print(f"  This means the variable name in .env doesn't match 'ODDS_API_KEY'")
        print(f"  Or there's a formatting issue")
    
else:
    print("  ERROR: .env file does not exist!")
    print(f"  Create it at: {env_file}")

print()
print("=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
