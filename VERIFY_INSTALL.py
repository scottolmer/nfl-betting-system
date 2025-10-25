"""
Verify all analysis engine files are created
"""

from pathlib import Path

project_root = Path(r"C:\Users\scott\Desktop\nfl-betting-system")
analysis_dir = project_root / "scripts" / "analysis"
agents_dir = analysis_dir / "agents"

print("🔍 Verifying NFL Prop Analysis Engine Installation")
print("="*60)

files_to_check = [
    ("test_week7.py", project_root / "scripts"),
    ("__init__.py", analysis_dir),
    ("models.py", analysis_dir),
    ("data_loader.py", analysis_dir),
    ("orchestrator.py", analysis_dir),
    ("__init__.py", agents_dir),
    ("base_agent.py", agents_dir),
    ("dvoa_agent.py", agents_dir),
    ("matchup_agent.py", agents_dir),
    ("injury_agent.py", agents_dir),
    ("game_script_agent.py", agents_dir),
    ("volume_agent.py", agents_dir),
    ("trend_agent.py", agents_dir),
    ("variance_agent.py", agents_dir),
    ("weather_agent.py", agents_dir),
]

all_present = True
for filename, directory in files_to_check:
    filepath = directory / filename
    if filepath.exists():
        print(f"✅ {filepath.relative_to(project_root)}")
    else:
        print(f"❌ MISSING: {filepath.relative_to(project_root)}")
        all_present = False

print("\n" + "="*60)
if all_present:
    print("✅ ALL FILES PRESENT!")
    print("\nYou're ready to test! Run:")
    print("  python scripts\\test_week7.py")
else:
    print("❌ Some files are missing")
    print("Please let me know and I'll recreate them")

print("="*60)
