"""
Test if .env file is loading correctly
"""
import os
from dotenv import load_dotenv

print("Testing .env file loading...")
print()

# Load .env
load_dotenv()

# Check each variable
variables = [
    'ODDS_API_KEY',
    'CLAUDE_API_KEY',
    'SLACK_BOT_TOKEN',
    'SLACK_WEBHOOK'
]

for var in variables:
    value = os.getenv(var)
    if value:
        # Show first 10 chars only for security
        masked = value[:10] + '...' if len(value) > 10 else value
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: NOT FOUND")

print()
print("If ODDS_API_KEY shows ❌, the monitor won't work.")
print("Check your .env file format (no spaces, no quotes).")
