"""
Clear all Python caches completely
"""

import shutil
from pathlib import Path

project_root = Path(r"C:\Users\scott\Desktop\nfl-betting-system")

print("🧹 Clearing all Python caches...")
print("="*60)

cache_dirs = list(project_root.rglob('__pycache__'))

if not cache_dirs:
    print("✅ No cache directories found")
else:
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Deleted: {cache_dir}")
        except Exception as e:
            print(f"❌ Failed to delete {cache_dir}: {e}")

print("\n" + "="*60)
print("✅ Cache clearing complete!")
print("\nNow run: python scripts\\debug_aj_brown.py")
