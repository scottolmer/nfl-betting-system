"""
Clear Python cache and verify data files
"""

import shutil
from pathlib import Path

project_root = Path(r"C:\Users\scott\Desktop\nfl-betting-system")
data_dir = project_root / "data"
cache_dir = project_root / "scripts" / "analysis" / "__pycache__"

print("🔧 System Cleanup & Verification")
print("="*60)

# Step 1: Clear cache
if cache_dir.exists():
    shutil.rmtree(cache_dir)
    print("✅ Cleared Python cache")
else:
    print("⚠️  No cache to clear")

# Step 2: Verify data files exist
print("\n📂 Checking for data files...")
files_to_check = [
    "wk7_receiving_base.csv",
    "wk7_receiving_usage.csv", 
    "wk7_receiving_alignment.csv",
    "wk7_rushing_base.csv",
    "wk7_rushing_usage.csv",
    "wk7_passing_base.csv",
]

all_found = True
for filename in files_to_check:
    filepath = data_dir / filename
    if filepath.exists():
        print(f"✅ {filename}")
    else:
        print(f"❌ MISSING: {filename}")
        all_found = False

# Step 3: Verify data loader has new code
print("\n📄 Checking data_loader.py...")
loader_file = project_root / "scripts" / "analysis" / "data_loader.py"
content = loader_file.read_text()

if "_load_receiving_usage" in content:
    print("✅ Data loader has new parsing functions")
else:
    print("❌ Data loader is still using old code!")

print("\n" + "="*60)
if all_found:
    print("✅ All systems ready!")
    print("\nNow run: python scripts\\test_week7.py")
else:
    print("❌ Some data files are missing")
    print("Make sure you copied all 6 files to the data folder")
