"""
Verify that data_loader.py has normalization code
"""

from pathlib import Path

project_root = Path(r"C:\Users\scott\Desktop\nfl-betting-system")
loader_file = project_root / "scripts" / "analysis" / "data_loader.py"

print("🔍 Verifying data_loader.py updates...")
print("="*60)

content = loader_file.read_text(encoding='utf-8')

checks = {
    "_normalize_name": "_normalize_name" in content,
    "normalized_name in usage": "normalized_name = self._normalize_name(player)" in content,
    "Multiple occurrences": content.count("normalized_name = self._normalize_name") >= 3,
}

print("\n📊 Verification Results:")
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"   {status} {check}: {result}")

if all(checks.values()):
    print("\n" + "="*60)
    print("✅ All checks passed! File is correctly updated.")
    print("\nNow run:")
    print("  1. python scripts\\clear_all_cache.py")
    print("  2. python scripts\\debug_aj_brown.py")
else:
    print("\n" + "="*60)
    print("❌ File verification FAILED!")
    print("The normalization code may not have been added properly.")
    
    # Show a snippet
    if "_normalize_name" in content:
        print("\n📄 Found _normalize_name method:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '_normalize_name' in line:
                print(f"   Line {i}: {line[:80]}")
    else:
        print("\n⚠️ _normalize_name method NOT FOUND in file!")
