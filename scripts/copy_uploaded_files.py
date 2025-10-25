"""
Copy uploaded data files to data directory
"""

import shutil
from pathlib import Path

# Source and destination
uploads_dir = Path("/mnt/user-data/uploads")
data_dir = Path(r"C:\Users\scott\Desktop\nfl-betting-system\data")

# Files to copy
files_to_copy = [
    "wk7_receiving_base.csv",
    "wk7_receiving_usage.csv",
    "wk7_receiving_alignment.csv",
    "wk7_rushing_base.csv",
    "wk7_rushing_usage.csv",
    "wk7_passing_base.csv",
]

print("📂 Copying data files...")
print("="*60)

for filename in files_to_copy:
    src = uploads_dir / filename
    dst = data_dir / filename
    
    if src.exists():
        shutil.copy(src, dst)
        print(f"✅ Copied: {filename}")
    else:
        print(f"❌ Not found: {filename}")

print("\n" + "="*60)
print("✅ File copy complete!")
print("\nNow run: python scripts\\test_week7.py")
